"""
Survey function tools for the full call lifecycle:
  - record_answer(question_id, answer)  — store any survey answer
  - end_survey(reason)                  — save data, speak farewell, wait for playout, hang up
  - schedule_callback(preferred_time)   — schedule a callback for later
  - send_survey_link()                  — send the survey link via email/text
"""

import asyncio
import os
from datetime import datetime
from typing import Callable, List, Optional

import aiohttp
from livekit.agents import function_tool, RunContext

from utils.logging import get_logger
from utils.storage import save_survey_responses

logger = get_logger()

POST_FAREWELL_BUFFER_SECONDS = 2.0
VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://voice-service:8017")
SCHEDULER_SERVICE_URL = os.getenv("SCHEDULER_SERVICE_URL", "http://scheduler-service:8070")


async def _call_service(url: str, params: dict):
    """POST to an internal service endpoint."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=8),
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.warning(f"{url} returned {resp.status}: {body}")
                    return False
                return True
    except Exception as e:
        logger.warning(f"Service call {url} failed: {e}")
        return False


def create_survey_tools(
    survey_responses: dict,
    caller_number: str,
    call_start_time: datetime,
    log_handler,
    cleanup_logging_fn: Callable,
    disconnect_fn: Callable = None,
    question_ids: List[str] = None,
    questions_map: dict = None,
    questions_map_es: dict = None,
    survey_id: Optional[str] = None,
    survey_url: Optional[str] = None,
    rider_email: Optional[str] = None,
    rider_name: Optional[str] = None,
    questions_metadata: List[dict] = None,
    language_mode: str = "bilingual",
):
    total_questions = len(question_ids) if question_ids else 0
    qmap = questions_map or {}
    qmap_es = questions_map_es or {}
    person_name = rider_name or "there"

    # Build lookup for full question metadata (parent_id, criteria, categories, etc.)
    _qmeta: dict = {}
    for q in (questions_metadata or []):
        _qmeta[q.get("id", "")] = q

    def _next_question_text(next_id: str, lang: str) -> str:
        if lang == "es" and qmap_es:
            return qmap_es.get(next_id, "") or qmap.get(next_id, "")
        return qmap.get(next_id, "")

    def _should_skip_conditional(qid: str) -> bool:
        """Check if a conditional question should be skipped based on its parent's answer."""
        meta = _qmeta.get(qid, {})
        parent_id = meta.get("parent_id")
        if not parent_id:
            return False
        parent_answer = survey_responses.get("answers", {}).get(parent_id)
        if parent_answer is None:
            return True
        trigger_cats = meta.get("parent_category_texts", [])
        if not trigger_cats:
            return False
        answer_lower = str(parent_answer).lower().strip()
        for cat in trigger_cats:
            if cat.lower().strip() in answer_lower or answer_lower in cat.lower().strip():
                return False
        return True

    def _find_next_question(remaining: List[str]) -> Optional[str]:
        """Find the next non-skippable question from the remaining list."""
        for qid in remaining:
            if _should_skip_conditional(qid):
                survey_responses["answers"][qid] = "__skipped__"
                logger.info(f"[SKIP] {qid} — conditional not met")
                continue
            return qid
        return None

    def _format_next_instruction(next_id: str, lang: str) -> str:
        """Build the instruction for the next question, including options for categorical."""
        next_text = _next_question_text(next_id, lang)
        meta = _qmeta.get(next_id, {})
        criteria = meta.get("criteria", "open")
        categories = meta.get("categories", [])
        if isinstance(categories, str):
            try:
                categories = __import__("json").loads(categories)
            except Exception:
                categories = []

        instruction = f'Ask VERBATIM: "{next_text}" (id:{next_id}).'
        if criteria == "categorical" and categories:
            opts = [c for c in categories if c.lower() != "none of the above"]
            if opts:
                opts_str = ", ".join(opts)
                instruction += f" READ these options: {opts_str}."
        elif criteria == "scale":
            scale_max = meta.get("scales") or 5
            instruction += f" Tell them the scale: 1 is very poor, {scale_max} is excellent."
        return instruction

    async def _save_and_notify(reason: str, call_duration: float):
        """Save results and notify backend services."""
        if survey_responses.get("_finalized"):
            logger.info("Already finalized, skipping duplicate save")
            return
        survey_responses["_finalized"] = True

        survey_responses["end_reason"] = reason
        survey_responses["completed"] = reason == "completed"
        save_survey_responses(caller_number, survey_responses, call_duration)
        cleanup_logging_fn(log_handler)

        if survey_id:
            await _call_service(
                f"{VOICE_SERVICE_URL}/api/voice/complete-survey",
                {"survey_id": survey_id, "reason": reason},
            )

            convo_log = survey_responses.get("_conversation_log", [])
            if convo_log:
                transcript_lines = []
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
                full_transcript = "\n".join(transcript_lines)
            else:
                transcript_lines = []
                for qid, ans in survey_responses.get("answers", {}).items():
                    transcript_lines.append(f"Q[{qid}]: {ans}")
                full_transcript = "\n".join(transcript_lines)

            try:
                await _call_service(
                    f"{VOICE_SERVICE_URL}/api/voice/store-transcript",
                    {
                        "survey_id": survey_id,
                        "full_transcript": full_transcript,
                        "call_duration_seconds": str(int(call_duration)),
                        "call_status": reason,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to store transcript: {e}")

    @function_tool()
    async def record_answer(context: RunContext, question_id: str, answer: str):
        """
        Record the caller's answer to a survey question.
        IMPORTANT: After calling this, read the response carefully — it tells you EXACTLY what to do next.
        It gives you the exact next question to ask. Do NOT ask any other question.

        Args:
            question_id: The question identifier from the survey
            answer: The caller's response in their own words
        """
        lang = getattr(context.userdata, "detected_language", "en")
        lang_reminder = " Respond ONLY in Spanish." if lang == "es" else ""

        if question_id in survey_responses["answers"]:
            done = list(survey_responses["answers"].keys())
            if question_ids:
                remaining = [q for q in question_ids if q not in done]
                next_id = _find_next_question(remaining) if remaining else None
                if next_id:
                    instr = _format_next_instruction(next_id, lang)
                    return f"Already recorded. {instr}{lang_reminder}"
                else:
                    return f"All questions answered. Call end_survey(\"completed\") now.{lang_reminder}"
            return f"Already recorded. Continue.{lang_reminder}"

        survey_responses["answers"][question_id] = answer
        done = list(survey_responses["answers"].keys())
        done_count = len(done)
        logger.info(f"[{question_id}] ({done_count}/{total_questions}) {answer[:120]}")

        if survey_id:
            asyncio.create_task(_call_service(
                f"{VOICE_SERVICE_URL}/api/voice/record-answer",
                {"survey_id": survey_id, "question_id": question_id, "answer": answer},
            ))

        if question_ids:
            remaining = [q for q in question_ids if q not in done]
            next_id = _find_next_question(remaining) if remaining else None
            if next_id:
                instr = _format_next_instruction(next_id, lang)
                return f"Recorded. {instr}{lang_reminder}"
            else:
                logger.info(f"ALL {total_questions} questions answered")
                return f"All questions answered. Call end_survey(\"completed\") now.{lang_reminder}"
        return f"Recorded.{lang_reminder}"

    @function_tool()
    async def end_survey(context: RunContext, reason: str = "completed"):
        """
        End the call: save survey data, speak farewell, wait for it to finish, then hang up.
        This is the ONLY way to end a call. One call to this tool does everything.

        Args:
            reason: Why the call is ending — completed, wrong_person, declined, not_available, callback_scheduled, link_sent
        """
        if reason == "completed" and question_ids:
            done = set(survey_responses["answers"].keys())
            remaining = [q for q in question_ids if q not in done]
            if remaining:
                logger.warning(
                    f"end_survey(completed) — {len(remaining)} questions unanswered, marking as skipped: "
                    f"{', '.join(remaining)}"
                )
                for qid in remaining:
                    survey_responses["answers"][qid] = "__skipped__"

        logger.info(f"end_survey called — reason: {reason}")

        call_duration = (datetime.now() - call_start_time).total_seconds()
        await _save_and_notify(reason, call_duration)

        rider = survey_responses.get("rider_name", "").strip()
        name_part = f", {rider}" if rider else ""
        lang = getattr(context.userdata, "detected_language", "en")

        if lang == "es":
            if reason == "completed":
                farewell = (
                    f"¡Muchas gracias por compartir sus opiniones{name_part}! "
                    "Realmente aprecio su tiempo. ¡Que tenga un excelente día! ¡Adiós!"
                )
            elif reason in ("not_available", "callback_scheduled"):
                farewell = "¡Perfecto! Estaremos en contacto. ¡Gracias por su tiempo y que tenga un excelente día! ¡Adiós!"
            elif reason == "wrong_person":
                farewell = "¡Le pido disculpas por la confusión! ¡Que tenga un buen día! ¡Adiós!"
            elif reason == "link_sent":
                farewell = "¡Perfecto! Le enviaremos el enlace. ¡Gracias por su tiempo y que tenga un excelente día! ¡Adiós!"
            else:
                farewell = "¡Por supuesto, no hay problema! ¡Gracias por su tiempo y que tenga un buen día! ¡Adiós!"
        else:
            if reason == "completed":
                farewell = (
                    f"Thanks so much for sharing your thoughts{name_part}! "
                    "I really appreciate your time, and I hope you have a great rest of your day! Goodbye!"
                )
            elif reason in ("not_available", "callback_scheduled"):
                farewell = "Fantastic! We'll be in touch. Thank you for your time, and have a wonderful day! Goodbye!"
            elif reason == "wrong_person":
                farewell = "I apologize for the mix-up! Have a great day! Goodbye!"
            elif reason == "link_sent":
                farewell = "Great! We'll send that over. Thank you for your time, and have a wonderful day! Goodbye!"
            else:
                farewell = "Of course, no problem at all! Thanks for your time — have a great day! Goodbye!"

        logger.info(f"[FAREWELL] {farewell}")
        speech_handle = context.session.say(farewell)
        await speech_handle.wait_for_playout()
        logger.info("[FAREWELL] playout finished — person heard the full goodbye")

        await asyncio.sleep(POST_FAREWELL_BUFFER_SECONDS)

        logger.info("Disconnecting call now")
        if disconnect_fn:
            await disconnect_fn()

        return "Call ended."

    @function_tool()
    async def schedule_callback(context: RunContext, preferred_time: str):
        """
        Schedule a callback for the person at their preferred time.
        Use this when the person says they are busy but would like a call back later.
        After this returns, call end_survey(reason='callback_scheduled') to end the call.

        Args:
            preferred_time: When they want to be called back (e.g. "tomorrow at 3pm", "next Monday morning")
        """
        logger.info(f"Scheduling callback for {caller_number} at: {preferred_time}")
        survey_responses["callback_requested"] = True
        survey_responses["callback_time"] = preferred_time

        if survey_id:
            delay = 3600
            time_lower = preferred_time.lower()
            if "hour" in time_lower:
                try:
                    hours = int("".join(c for c in time_lower.split("hour")[0] if c.isdigit()) or "1")
                    delay = hours * 3600
                except ValueError:
                    pass
            elif "tomorrow" in time_lower:
                delay = 86400
            elif "minute" in time_lower:
                try:
                    mins = int("".join(c for c in time_lower.split("minute")[0] if c.isdigit()) or "30")
                    delay = mins * 60
                except ValueError:
                    pass

            await _call_service(
                f"{SCHEDULER_SERVICE_URL}/api/scheduler/schedule-call",
                {"survey_id": survey_id, "phone": caller_number, "delay_seconds": str(delay)},
            )

        return "Callback scheduled. Now call end_survey(reason='callback_scheduled') to end the call."

    @function_tool()
    async def send_survey_link(context: RunContext):
        """
        Send the survey link to the person via email or text so they can fill it out at their convenience.
        Use this when the person declines a callback but agrees to receive the survey link.
        After this returns, call end_survey(reason='link_sent') to end the call.
        """
        logger.info(f"Sending survey link for survey={survey_id} to {rider_email or caller_number}")
        SURVEY_SERVICE_URL = os.getenv("SURVEY_SERVICE_URL", "http://survey-service:8020")

        sent = False
        # 1. Try email if we have an email address
        lang = getattr(context.userdata, "detected_language", "en")
        if survey_id and survey_url and rider_email:
            sent = await _call_service(
                f"{VOICE_SERVICE_URL}/api/voice/send-email-fallback",
                {"survey_id": survey_id, "email": rider_email, "survey_url": survey_url, "language": lang},
            )

        # 2. Fallback to SMS if email failed or no email
        if not sent and survey_id and caller_number:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{SURVEY_SERVICE_URL}/api/surveys/sendsms",
                        json={
                            "phone": caller_number,
                            "survey_id": survey_id,
                            "survey_url": survey_url or "",
                            "rider_name": person_name,
                            "language": lang,
                        },
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            sent = True
                            logger.info(f"Survey link sent via SMS to {caller_number}")
                        else:
                            body = await resp.text()
                            logger.warning(f"SMS send failed ({resp.status}): {body}")
            except Exception as e:
                logger.warning(f"SMS fallback failed: {e}")

        if sent:
            return "Survey link sent. Now call end_survey(reason='link_sent') to end the call."
        else:
            return "Could not send link (no email or phone on file). Apologize, then call end_survey(reason='link_sent') to end the call."

    @function_tool()
    async def to_questions(context: RunContext):
        """
        Hand off to the survey questions agent.
        Call this ONLY after the person has confirmed their identity AND confirmed they are available for the survey.
        Do NOT call before both confirmations are complete.
        """
        call_data = context.userdata
        call_data.prev_agent = context.session.current_agent

        # English path: both language variants are registered — pick by detected language
        if "questions_en" in call_data.agents:
            lang = getattr(call_data, "detected_language", "en")
            key = "questions_es" if lang == "es" else "questions_en"
            logger.info(f"[HANDOFF] to_questions → {key} (detected_language={lang})")
            return call_data.agents[key]

        # Spanish path (or legacy): single "questions" key
        logger.info("[HANDOFF] to_questions → questions")
        return call_data.agents["questions"]

    @function_tool()
    async def set_language(context: RunContext, language: str):
        """
        Record the recipient's language preference detected from their reply.
        Call this as soon as the language is clear. This LOCKS the language for the entire call.
        language must be 'en' for English or 'es' for Spanish.
        """
        context.userdata.detected_language = language
        logger.info(f"[LANGUAGE] Recipient selected: {language}")

        name = rider_name or ""
        name_known = bool(name and len(name.strip()) >= 2 and name.strip().lower() not in {
            "customer", "unknown", "user", "recipient", "test", "n/a", "na", "none", "name"
        })

        if language == "es":
            next_q = (
                f"¿Estoy hablando con {name}?"
                if name_known
                else "¿Con quién tengo el gusto de hablar?"
            )
            return f"Español confirmado. Pregunta: '{next_q}'"

        next_q = (
            f"Am I speaking with {name}?"
            if name_known
            else "May I know who I'm speaking with?"
        )
        return f"English confirmed. Ask: '{next_q}'"

    greeter_tools = [end_survey, schedule_callback, send_survey_link, to_questions]
    if language_mode == "bilingual":
        greeter_tools.insert(0, set_language)

    question_tools = [record_answer, end_survey]
    return greeter_tools, question_tools
