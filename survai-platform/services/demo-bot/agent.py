"""
Demo Voice Bot — Main Entry Point (Multi-Agent)

Three-agent pipeline for every call:
  1. GreetingAgent  — opening message + availability confirmation
  2. QuestionsAgent — conduct survey questions
  3. EndingAgent    — raffle offer + closing

English only. Prompts are built locally (not from voice-service metadata).
Questions come from dispatch metadata.
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
    room_io,
)
from livekit.agents.voice import AgentSession
from livekit.agents.voice.events import CloseEvent
from livekit.plugins import deepgram, openai, silero, elevenlabs, noise_cancellation

from config.settings import (
    ORGANIZATION_NAME,
    SIP_OUTBOUND_TRUNK_ID,
    STT_MODEL,
    STT_ENDPOINTING_MS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    TTS_MODEL,
    TTS_VOICE_ID,
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
    AGENT_NAME,
    INACTIVITY_TIMEOUT,
    MAX_INACTIVITY_REPROMPTS,
)
from agents import (
    DemoCallData,
    GreetingAgent,
    QuestionsAgent,
    EndingAgent,
)
from tools.demo_tools import create_demo_tools
from prompts import build_greeter_prompt, build_questions_prompt, build_ending_prompt
from utils.logging import get_logger, setup_survey_logging, cleanup_survey_logging
from utils.metrics_logger import log_pipeline_metrics
from utils.storage import create_empty_response_dict

logger = get_logger()
VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://voice-service:8017")


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

    _display = (metadata.get("organization_name") or ORGANIZATION_NAME or "").strip()
    caller_id_name = _display or "IT Curves"

    if phone_number:
        logger.info(f"Outbound call to {phone_number} in room {ctx.room.name} (Caller ID: {caller_id_name})")
        try:
            await ctx.api.sip.create_sip_participant(
                api.CreateSIPParticipantRequest(
                    room_name=ctx.room.name,
                    sip_trunk_id=SIP_OUTBOUND_TRUNK_ID,
                    sip_call_to=phone_number,
                    participant_identity=phone_number,
                    wait_until_answered=True,
                    display_name=caller_id_name,
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

    platform_org = metadata.get("organization_name", "")
    org_name = platform_org or ORGANIZATION_NAME
    rider_name = metadata.get("recipient_name", "")
    rider_first_name = rider_name.split()[0] if rider_name else ""

    logger.info(f"Call config: recipient={rider_first_name}, org={org_name}")

    questions_list = metadata.get("questions", [])
    question_ids = [q.get("id", f"q{i+1}") for i, q in enumerate(questions_list) if isinstance(q, dict)]
    questions_map = {}
    for i, q in enumerate(questions_list):
        if isinstance(q, dict):
            qid = q.get("id", f"q{i+1}")
            questions_map[qid] = q.get("text") or q.get("question_text") or f"Question {i+1}"

    logger.info(
        f"Recipient: '{rider_first_name}' | Org: '{org_name}' | Phone: {caller_number} | "
        f"Questions: {len(question_ids)}"
    )

    survey_responses = create_empty_response_dict(rider_first_name, caller_number)
    survey_responses["survey_id"] = survey_id

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
    call_data = DemoCallData(
        survey_responses=survey_responses,
        caller_number=caller_number,
        call_start_time=call_start_time,
        log_handler=log_handler,
        cleanup_logging_fn=cleanup_survey_logging,
        disconnect_fn=hangup_call,
        question_ids=question_ids,
        questions_map=questions_map,
        survey_id=survey_id,
        survey_url=survey_url,
        rider_email=rider_email,
        rider_name=rider_first_name,
    )

    # Create tools — split into greeting, questions, and ending sets
    greeting_tools, question_tools, ending_tools = create_demo_tools(
        survey_responses=survey_responses,
        caller_number=caller_number,
        call_start_time=call_start_time,
        log_handler=log_handler,
        cleanup_logging_fn=cleanup_survey_logging,
        disconnect_fn=hangup_call,
        question_ids=question_ids,
        questions_map=questions_map,
        survey_id=survey_id,
        survey_url=survey_url,
        rider_email=rider_email,
        rider_name=rider_first_name,
        questions_metadata=questions_list,
    )

    # Build prompts locally
    greeter_prompt = build_greeter_prompt(org_name)
    questions_prompt = build_questions_prompt(org_name, questions_list)
    ending_prompt = build_ending_prompt()

    # Create agents
    greeting_agent = GreetingAgent(
        instructions=greeter_prompt,
        organization_name=org_name,
        tools=greeting_tools,
    )
    questions_agent = QuestionsAgent(
        instructions=questions_prompt,
        tools=question_tools,
    )
    ending_agent = EndingAgent(
        instructions=ending_prompt,
        tools=ending_tools,
    )

    # Register all agents in call_data
    call_data.agents["greeting"] = greeting_agent
    call_data.agents["questions"] = questions_agent
    call_data.agents["ending"] = ending_agent

    logger.info("Agent pipeline: greeting → questions → ending")

    stt_kw: dict = {
        "model": STT_MODEL,
        "language": "en",
        "endpointing_ms": STT_ENDPOINTING_MS,
        "keyterm": [
            "Yes", "No", "Yeah", "Yep", "Nope",
        ],
    }

    session = AgentSession[DemoCallData](
        userdata=call_data,
        stt=deepgram.STT(**stt_kw),
        llm=openai.LLM(model=LLM_MODEL, temperature=LLM_TEMPERATURE, service_tier="priority"),
        tts=elevenlabs.TTS(
            voice_id=TTS_VOICE_ID,
            model=TTS_MODEL,
            apply_text_normalization="on",
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

    # ── Inactivity monitor ──────────────────────────────────────────────────
    _inactivity_reprompt_count = 0
    _inactivity_task: asyncio.Task = None

    def _cancel_inactivity() -> None:
        nonlocal _inactivity_task
        if _inactivity_task and not _inactivity_task.done():
            _inactivity_task.cancel()
        _inactivity_task = None

    def _start_inactivity() -> None:
        nonlocal _inactivity_task
        _cancel_inactivity()
        _inactivity_task = asyncio.create_task(_inactivity_watchdog())

    async def _inactivity_watchdog() -> None:
        nonlocal _inactivity_reprompt_count
        try:
            await asyncio.sleep(INACTIVITY_TIMEOUT)
        except asyncio.CancelledError:
            return

        if survey_responses.get("end_reason"):
            return

        _inactivity_reprompt_count += 1

        if _inactivity_reprompt_count > MAX_INACTIVITY_REPROMPTS:
            logger.info(
                f"[INACTIVITY] No response after {MAX_INACTIVITY_REPROMPTS} re-prompts — ending call"
            )
            survey_responses["end_reason"] = "not_available"
            try:
                await session.say(
                    "It seems we've lost the connection. Thank you for your time. Goodbye!"
                )
                await asyncio.sleep(3)
            except Exception:
                pass
            await hangup_call()
            return

        logger.info(
            f"[INACTIVITY] Silence timeout — re-prompt "
            f"{_inactivity_reprompt_count}/{MAX_INACTIVITY_REPROMPTS}"
        )
        try:
            await session.say("Hello? Are you still there?")
        except Exception as e:
            logger.warning(f"[INACTIVITY] Failed to speak re-prompt: {e}")

    # ───────────────────────────────────────────────────────────────────────

    @session.on("user_input_transcribed")
    def _on_user_input(ev) -> None:
        nonlocal _inactivity_reprompt_count
        transcript = getattr(ev, "transcript", None) or str(ev)
        is_final = getattr(ev, "is_final", True)
        if is_final and transcript.strip():
            _inactivity_reprompt_count = 0
            text = transcript.strip()[:400]
            logger.info(f"[USER] {text}")
            survey_responses["_conversation_log"].append({
                "role": "user",
                "text": text,
                "ts": datetime.now().isoformat(),
            })

    @session.on("conversation_item_added")
    def _on_conversation_item(ev) -> None:
        try:
            msg = getattr(ev, "item", None)
            if msg is None:
                return
            role = getattr(msg, "role", None)
            if role != "assistant":
                return
            text = ""
            content = getattr(msg, "content", None)
            if hasattr(msg, "text_content"):
                tc = getattr(msg, "text_content", None)
                text = (tc() if callable(tc) else tc) or ""
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
        except Exception as e:
            logger.warning("[conversation_item_added] %s", e, exc_info=False)

    @session.on("metrics_collected")
    def _on_metrics(ev) -> None:
        log_pipeline_metrics(ev.metrics)

    @session.on("agent_state_changed")
    def _on_agent_state(ev) -> None:
        logger.info("[STATE] %s → %s", ev.old_state, ev.new_state)
        new = ev.new_state
        if new == "listening":
            _start_inactivity()
        elif new in ("thinking", "speaking", "initializing"):
            _cancel_inactivity()

    time_limit_minutes = metadata.get("time_limit_minutes", 8)

    async def _time_limit_watchdog():
        """Enforce call time limit — speak a farewell then disconnect."""
        await asyncio.sleep(time_limit_minutes * 60)
        if not survey_responses.get("end_reason"):
            logger.warning(f"Time limit reached ({time_limit_minutes}m) — saying farewell and disconnecting")
            survey_responses["end_reason"] = "time_limit"
            try:
                farewell = (
                    "We've reached the end of our survey time. "
                    "Thank you so much for your time — have a wonderful day! Goodbye!"
                )
                speech_handle = session.say(farewell)
                await speech_handle.wait_for_playout()
                await asyncio.sleep(2.0)
            except Exception as e:
                logger.warning(f"[TIME_LIMIT] Farewell failed: {e}")
            try:
                await hangup_call()
            except Exception:
                pass

    asyncio.create_task(_time_limit_watchdog())

    async def _on_session_close_async():
        """Cleanup when the AgentSession actually closes."""
        _cancel_inactivity()

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

    @session.on("close")
    def _on_session_close(ev: CloseEvent):
        logger.info(f"[SESSION] closed — reason: {ev.reason}")
        asyncio.create_task(_on_session_close_async())

    await session.start(
        room=ctx.room,
        agent=call_data.agents["greeting"],
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=noise_cancellation.BVCTelephony(),
            ),
        ),
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            # agent_name=AGENT_NAME,
            initialize_process_timeout=WORKER_INITIALIZE_TIMEOUT,
            job_memory_warn_mb=JOB_MEMORY_WARN_MB,
            job_memory_limit_mb=JOB_MEMORY_LIMIT_MB,
        ),
    )
