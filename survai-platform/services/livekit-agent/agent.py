"""
Survey Voice Bot — Main Entry Point (Multi-Agent)

Two agents handle each call. The pair depends on the call language:
  language=="en" (default):
    EnglishGreeterAgent — lang-pref detection + identity + availability (~300-token prompt)
    EnglishQuestionsAgent or SpanishQuestionsAgent — chosen after lang-pref
  language=="es":
    SpanishGreeterAgent — identity + availability in Spanish (~300-token prompt)
    SpanishQuestionsAgent — Spanish-only survey questions

Prompts come from voice-service via dispatch metadata (greeter_prompt / questions_prompt).
"""

import asyncio
import os
import json
from datetime import datetime
import aiohttp

from livekit import api
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    AutoSubscribe,
    RoomInputOptions,
)
from livekit.agents.voice import AgentSession
from livekit.plugins import deepgram, openai, silero, elevenlabs, noise_cancellation

from config.settings import (
    ORGANIZATION_NAME,
    SIP_OUTBOUND_TRUNK_ID,
    STT_MODEL,
    STT_LANGUAGE,
    STT_DETECT_LANGUAGE,
    STT_ENDPOINTING_MS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    TTS_MODEL,
    TTS_MODEL_ES,
    TTS_VOICE_ID,
    TTS_VOICE_ID_ES,
    PREEMPTIVE_GENERATION,
    RESUME_FALSE_INTERRUPTION,
    FALSE_INTERRUPTION_TIMEOUT,
    MAX_TOOL_STEPS,
    WORKER_INITIALIZE_TIMEOUT,
    JOB_MEMORY_WARN_MB,
    JOB_MEMORY_LIMIT_MB,
    VAD_MIN_SILENCE_DURATION,
    VAD_MIN_SPEECH_DURATION,
    VAD_ACTIVATION_THRESHOLD,
)
from agents import (
    SurveyCallData,
    GreeterAgent,
    QuestionsAgent,
    EnglishGreeterAgent,
    SpanishGreeterAgent,
    EnglishQuestionsAgent,
    SpanishQuestionsAgent,
)
from tools.survey_tools import create_survey_tools
from utils.logging import get_logger, setup_survey_logging, cleanup_survey_logging
from utils.metrics_logger import log_pipeline_metrics
from utils.storage import create_empty_response_dict
from utils.recording import start_call_recording, stop_call_recording

logger = get_logger()
VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://voice-service:8017")

MINIMAL_GREETER_PROMPT = (
    "You are Cameron, a friendly survey caller. "
    "Confirm the person's identity and ask if they have time for a brief survey. "
    "Call to_questions() once they confirm availability."
)

MINIMAL_QUESTIONS_PROMPT = (
    "You are Cameron, a friendly AI survey assistant. "
    "Identity and availability are already confirmed. "
    "Conduct the survey questions. Use record_answer(question_id, answer) to save each response. "
    "When done, call end_survey(reason='completed') — it says goodbye and hangs up automatically."
)


async def entrypoint(ctx: JobContext):
    metadata = json.loads(ctx.job.metadata or "{}")
    phone_number = metadata.get("phone_number")
    survey_id = metadata.get("survey_id")

    async def _voice_service_post(endpoint: str, params: dict) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{VOICE_SERVICE_URL}/api/voice/{endpoint}",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=8),
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"{endpoint} returned {resp.status}: {await resp.text()}")
        except Exception as e:
            logger.warning(f"Failed to call {endpoint} for survey {survey_id}: {e}")

    async def release_call_lock() -> None:
        if not survey_id and not phone_number:
            return
        await _voice_service_post("release-call", {"survey_id": survey_id or "", "phone": phone_number or ""})

    async def confirm_call_lock() -> None:
        if not survey_id:
            return
        await _voice_service_post("confirm-call", {"survey_id": survey_id or "", "phone": phone_number or ""})

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    if phone_number:
        logger.info(f"Outbound call to {phone_number} in room {ctx.room.name}")
        try:
            await ctx.api.sip.create_sip_participant(
                api.CreateSIPParticipantRequest(
                    room_name=ctx.room.name,
                    sip_trunk_id=SIP_OUTBOUND_TRUNK_ID,
                    sip_call_to=phone_number,
                    participant_identity=phone_number,
                    wait_until_answered=True,
                    display_name=ORGANIZATION_NAME,
                )
            )
            logger.info(f"Answered: {phone_number}")
            await confirm_call_lock()
        except Exception as e:
            logger.error(f"Call to {phone_number} failed: {e}")
            await release_call_lock()
            return
        participant = await ctx.wait_for_participant()
        caller_number = phone_number
    else:
        logger.info("Sandbox mode — waiting for browser participant")
        participant = await ctx.wait_for_participant()
        caller_number = participant.identity or "sandbox-user"

    log_filename, log_handler = setup_survey_logging(ctx.room.name, caller_number)
    call_start_time = datetime.now()

    recording_handle = await start_call_recording(
        room_name=ctx.room.name,
        survey_id=survey_id or ctx.room.name,
        lk_api=ctx.api,
    )

    platform_recipient = metadata.get("recipient_name", "")
    platform_org = metadata.get("organization_name", "")

    rider_first_name = platform_recipient.split()[0] if platform_recipient else ""
    org_name = platform_org or ORGANIZATION_NAME
    call_language = metadata.get("language", "bilingual")
    greetings = metadata.get("greetings", "")
    logger.info(f"Call config: language={call_language}, recipient={rider_first_name}, org={org_name}")

    # Ensure detected_language is pre-set to the call language
    # (for Spanish calls it is always "es"; for English calls it may change after lang-pref)

    greeter_prompt = metadata.get("greeter_prompt") or metadata.get("system_prompt") or MINIMAL_GREETER_PROMPT
    questions_prompt = metadata.get("questions_prompt") or MINIMAL_QUESTIONS_PROMPT

    questions_list = metadata.get("questions", [])
    question_ids = [q.get("id", f"q{i+1}") for i, q in enumerate(questions_list) if isinstance(q, dict)]
    questions_map = {}
    for i, q in enumerate(questions_list):
        if isinstance(q, dict):
            qid = q.get("id", f"q{i+1}")
            questions_map[qid] = q.get("text") or q.get("question_text") or f"Question {i+1}"

    # For Spanish-initiated calls, overwrite with Spanish question texts
    translated_map = metadata.get("translated_questions")
    if isinstance(translated_map, dict) and translated_map:
        logger.info(f"Applying {len(translated_map)} translated question texts")
        questions_map.update(translated_map)
    # For English-initiated calls, keep Spanish map separate (used when user selects Spanish)
    questions_map_es = metadata.get("questions_es_map") or {}
    if questions_map_es:
        logger.info(f"Spanish question map available for lang switch: {len(questions_map_es)} questions")

    logger.info(
        f"Recipient: '{rider_first_name}' | Org: '{org_name}' | Phone: {caller_number} | "
        f"Language: {call_language} | Questions: {len(question_ids)} | "
        f"Greeter prompt: {len(greeter_prompt)} chars | "
        f"Questions prompt: {len(questions_prompt)} chars | "
        f"Greetings override: {'yes' if greetings else 'no'}"
    )

    survey_responses = create_empty_response_dict(rider_first_name, caller_number)

    async def hangup_call():
        logger.info("Hanging up — deleting room")
        try:
            await ctx.api.room.delete_room(
                api.DeleteRoomRequest(room=ctx.room.name)
            )
        except Exception as e:
            logger.error(f"Room delete failed: {e}")
            await ctx.room.disconnect()

    survey_url = metadata.get("survey_url", "")
    rider_email = metadata.get("rider_email", "")

    # Build shared state
    call_data = SurveyCallData(
        survey_responses=survey_responses,
        caller_number=caller_number,
        call_start_time=call_start_time,
        log_handler=log_handler,
        cleanup_logging_fn=cleanup_survey_logging,
        disconnect_fn=hangup_call,
        question_ids=question_ids,
        questions_map=questions_map,
        questions_map_es=questions_map_es,
        survey_id=survey_id,
        survey_url=survey_url,
        rider_email=rider_email,
        rider_name=rider_first_name,
    )

    # Create tools — split into greeter and questions sets
    greeter_tools, question_tools = create_survey_tools(
        survey_responses=survey_responses,
        caller_number=caller_number,
        call_start_time=call_start_time,
        log_handler=log_handler,
        cleanup_logging_fn=cleanup_survey_logging,
        disconnect_fn=hangup_call,
        question_ids=question_ids,
        questions_map=questions_map,
        questions_map_es=questions_map_es,
        survey_id=survey_id,
        survey_url=survey_url,
        rider_email=rider_email,
        rider_name=rider_first_name,
        questions_metadata=questions_list,
    )

    # Build agents based on call language mode
    if call_language == "es":
        # Spanish-only pipeline: SpanishGreeterAgent → SpanishQuestionsAgent
        call_data.detected_language = "es"
        greeter_agent = SpanishGreeterAgent(
            instructions=greeter_prompt,
            rider_first_name=rider_first_name,
            organization_name=org_name,
            greetings=greetings,
            tools=greeter_tools,
        )
        questions_agent = SpanishQuestionsAgent(
            instructions=questions_prompt,
            tools=question_tools,
        )
        call_data.agents["questions"] = questions_agent
        call_data.agents["greeter"] = greeter_agent
    elif call_language == "en":
        # English-only pipeline: EnglishGreeterAgent (no lang question) → EnglishQuestionsAgent
        call_data.detected_language = "en"
        greeter_agent = EnglishGreeterAgent(
            instructions=greeter_prompt,
            rider_first_name=rider_first_name,
            organization_name=org_name,
            greetings=greetings,
            language_mode="en",
            tools=greeter_tools,
        )
        questions_agent = EnglishQuestionsAgent(
            instructions=questions_prompt,
            tools=question_tools,
        )
        call_data.agents["greeter"] = greeter_agent
        call_data.agents["questions"] = questions_agent
        call_data.agents["questions_en"] = questions_agent
    else:
        # Bilingual pipeline: EnglishGreeterAgent (asks lang pref) → EnglishQuestionsAgent or SpanishQuestionsAgent
        greeter_agent = EnglishGreeterAgent(
            instructions=greeter_prompt,
            rider_first_name=rider_first_name,
            organization_name=org_name,
            greetings=greetings,
            language_mode="bilingual",
            tools=greeter_tools,
        )
        questions_agent_en = EnglishQuestionsAgent(
            instructions=questions_prompt,
            tools=question_tools,
        )
        questions_prompt_es = metadata.get("questions_prompt_es") or questions_prompt
        questions_agent_es = SpanishQuestionsAgent(
            instructions=questions_prompt_es,
            tools=question_tools,
        )
        call_data.agents["greeter"] = greeter_agent
        call_data.agents["questions_en"] = questions_agent_en
        call_data.agents["questions_es"] = questions_agent_es
        questions_agent = questions_agent_en

    stt_language = "es" if call_language == "es" else STT_LANGUAGE
    stt_detect_language = STT_DETECT_LANGUAGE and call_language not in ("es", "en")

    tts_model = TTS_MODEL_ES if call_language == "es" else TTS_MODEL
    tts_voice = TTS_VOICE_ID_ES if call_language == "es" else TTS_VOICE_ID

    session = AgentSession[SurveyCallData](
        userdata=call_data,
        stt=deepgram.STT(
            model=STT_MODEL,
            language=stt_language,
            detect_language=stt_detect_language,
            endpointing_ms=STT_ENDPOINTING_MS,
            keywords=[
                "Yes:2", "No:2", "Yeah:2", "Yep:2", "Nope:2",
                "Sí:2", "No:2", "Bueno:1",
            ],
        ),
        llm=openai.LLM(model=LLM_MODEL, temperature=LLM_TEMPERATURE, service_tier="priority"),
        tts=elevenlabs.TTS(
                voice_id=tts_voice,
                model=tts_model,
                apply_text_normalization="on"
            ),
        vad=silero.VAD.load(
            min_silence_duration=VAD_MIN_SILENCE_DURATION,
            min_speech_duration=VAD_MIN_SPEECH_DURATION,
            activation_threshold=VAD_ACTIVATION_THRESHOLD,
        ),
        preemptive_generation=PREEMPTIVE_GENERATION,
        resume_false_interruption=RESUME_FALSE_INTERRUPTION,
        false_interruption_timeout=FALSE_INTERRUPTION_TIMEOUT,
        max_tool_steps=MAX_TOOL_STEPS,
    )

    survey_responses["_conversation_log"] = []

    @session.on("user_input_transcribed")
    def _on_user_input(ev) -> None:
        transcript = getattr(ev, "transcript", None) or str(ev)
        is_final = getattr(ev, "is_final", True)
        if is_final and transcript.strip():
            text = transcript.strip()[:400]
            logger.info(f"[USER] {text}")
            survey_responses["_conversation_log"].append({
                "role": "user",
                "text": text,
                "ts": datetime.now().isoformat(),
            })

    @session.on("conversation_item_added")
    def _on_conversation_item(ev) -> None:
        msg = getattr(ev, "item", None)
        if msg is None:
            return
        role = getattr(msg, "role", None)
        if role == "assistant":
            text = ""
            content = getattr(msg, "content", None)
            if hasattr(msg, "text_content"):
                text = msg.text_content() or ""
            elif isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = " ".join(str(c) for c in content if c)
            if text.strip():
                logger.info(f"[AGENT] {text.strip()[:400]}")
                survey_responses["_conversation_log"].append({
                    "role": "agent",
                    "text": text.strip()[:400],
                    "ts": datetime.now().isoformat(),
                })

    @session.on("metrics_collected")
    def _on_metrics(ev) -> None:
        log_pipeline_metrics(ev.metrics)

    @session.on("agent_state_changed")
    def _on_agent_state(ev) -> None:
        logger.info("[STATE] %s → %s", ev.old_state, ev.new_state)

    time_limit_minutes = metadata.get("time_limit_minutes", 8)

    async def _time_limit_watchdog():
        """Enforce call time limit — gracefully end call if exceeded."""
        await asyncio.sleep(time_limit_minutes * 60)
        if not survey_responses.get("end_reason"):
            logger.warning(f"Time limit reached ({time_limit_minutes}m) — disconnecting")
            survey_responses["end_reason"] = "time_limit"
            try:
                await hangup_call()
            except Exception:
                pass

    asyncio.create_task(_time_limit_watchdog())

    try:
        await session.start(
            room=ctx.room,
            agent=call_data.agents["greeter"],
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVCTelephony(),
            ),
        )
    finally:
        audio_url = await stop_call_recording(recording_handle, ctx.api)

        if survey_id and not survey_responses.get("_finalized"):
            reason = survey_responses.get("end_reason") or "disconnected"
            answered = len(survey_responses.get("answers", {}))
            total = len(question_ids) if question_ids else 0
            if answered > 0 and answered >= total and reason == "disconnected":
                reason = "completed"
            logger.info(
                f"Session ended without end_survey — finalizing as '{reason}' "
                f"({answered}/{total} answered)"
            )
            survey_responses["_finalized"] = True
            call_duration = (datetime.now() - call_start_time).total_seconds()
            try:
                await _voice_service_post("complete-survey", {
                    "survey_id": survey_id, "reason": reason,
                })
            except Exception as e:
                logger.warning(f"Failed to finalize survey on exit: {e}")

            convo_log = survey_responses.get("_conversation_log", [])
            transcript_lines = []
            if convo_log:
                for entry in convo_log:
                    role_label = "AGENT" if entry["role"] == "agent" else "CALLER"
                    transcript_lines.append(
                        f'[{entry["ts"]}] {role_label}: {entry["text"]}'
                    )
                answers_section = []
                for qid, ans in survey_responses.get("answers", {}).items():
                    answers_section.append(f"  Q[{qid}]: {ans}")
                if answers_section:
                    transcript_lines.append("\n--- RECORDED ANSWERS ---")
                    transcript_lines.extend(answers_section)
            else:
                for qid, ans in survey_responses.get("answers", {}).items():
                    transcript_lines.append(f"Q[{qid}]: {ans}")

            if transcript_lines:
                store_params = {
                    "survey_id": survey_id,
                    "full_transcript": "\n".join(transcript_lines),
                    "call_duration_seconds": str(int(call_duration)),
                    "call_status": reason,
                }
                if audio_url:
                    store_params["audio_url"] = audio_url
                try:
                    await _voice_service_post("store-transcript", store_params)
                except Exception as e:
                    logger.warning(f"Failed to store transcript on exit: {e}")

            try:
                from utils.storage import save_survey_responses
                save_survey_responses(caller_number, survey_responses, call_duration)
                cleanup_survey_logging(log_handler)
            except Exception as e:
                logger.warning(f"Failed to save responses on exit: {e}")
        await release_call_lock()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="survey-agent",
            initialize_process_timeout=WORKER_INITIALIZE_TIMEOUT,
            job_memory_warn_mb=JOB_MEMORY_WARN_MB,
            job_memory_limit_mb=JOB_MEMORY_LIMIT_MB,
        ),
    )
