"""
Survey function tools — aligned with brain-service prompt.

Tools:
  - record_answer(question_id, answer)  — store any survey answer
  - end_survey(reason)                  — end the call and disconnect
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

HANGUP_DELAY_SECONDS = 6.0
AUTO_END_DELAY_SECONDS = 14.0
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
    survey_id: Optional[str] = None,
    survey_url: Optional[str] = None,
    rider_email: Optional[str] = None,
    rider_name: Optional[str] = None,
):
    total_questions = len(question_ids) if question_ids else 0
    qmap = questions_map or {}
    person_name = rider_name or "there"
    survey_finished = {"done": False}

    async def _save_and_disconnect(reason: str = "completed"):
        """Save results, notify backend, disconnect."""
        if survey_responses.get("_finalized"):
            logger.info("Already finalized, skipping duplicate _save_and_disconnect")
            if disconnect_fn:
                await disconnect_fn()
            return
        survey_responses["_finalized"] = True
        logger.info(f"Finalizing survey: reason={reason}")

        survey_responses["end_reason"] = reason
        survey_responses["completed"] = reason == "completed"
        call_duration = (datetime.now() - call_start_time).total_seconds()
        save_survey_responses(caller_number, survey_responses, call_duration)
        cleanup_logging_fn(log_handler)

        if survey_id:
            await _call_service(
                f"{VOICE_SERVICE_URL}/api/voice/complete-survey",
                {"survey_id": survey_id, "reason": reason},
            )
            transcript_lines = []
            for qid, ans in survey_responses.get("answers", {}).items():
                transcript_lines.append(f"Q[{qid}]: {ans}")
            try:
                await _call_service(
                    f"{VOICE_SERVICE_URL}/api/voice/store-transcript",
                    {
                        "survey_id": survey_id,
                        "full_transcript": "\n".join(transcript_lines),
                        "call_duration_seconds": str(int(call_duration)),
                        "call_status": reason,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to store transcript: {e}")

        logger.info(f"Disconnecting call in {HANGUP_DELAY_SECONDS}s")
        await asyncio.sleep(HANGUP_DELAY_SECONDS)
        if disconnect_fn:
            await disconnect_fn()

    @function_tool()
    async def record_answer(context: RunContext, question_id: str, answer: str):
        """
        Record the caller's answer to a survey question.
        IMPORTANT: After calling this, read the response carefully — it tells you EXACTLY what to do next.

        Args:
            question_id: The question identifier from the survey
            answer: The caller's response in their own words
        """
        if survey_finished["done"]:
            return (
                f"The survey is already complete. Say goodbye to {person_name} warmly "
                f"then call end_survey(\"completed\") to hang up."
            )

        if question_id in survey_responses["answers"]:
            done = list(survey_responses["answers"].keys())
            if question_ids:
                remaining = [q for q in question_ids if q not in done]
                if remaining:
                    next_id = remaining[0]
                    next_text = qmap.get(next_id, "")
                    return (
                        f"Already recorded {question_id}. "
                        f"Move on — ask this next: \"{next_text}\" (question_id: {next_id})."
                    )
                else:
                    survey_finished["done"] = True
                    return (
                        f"All questions are already answered. Say goodbye to {person_name} now, "
                        f"then call end_survey(\"completed\")."
                    )
            return f"Already recorded {question_id}. Move to the next question."

        survey_responses["answers"][question_id] = answer
        done = list(survey_responses["answers"].keys())
        done_count = len(done)
        logger.info(f"✅ [{question_id}] ({done_count}/{total_questions}) {answer[:120]}")

        if survey_id:
            asyncio.create_task(_call_service(
                f"{VOICE_SERVICE_URL}/api/voice/record-answer",
                {"survey_id": survey_id, "question_id": question_id, "answer": answer},
            ))

        if question_ids:
            remaining = [q for q in question_ids if q not in done]
            if remaining:
                next_id = remaining[0]
                next_text = qmap.get(next_id, "")
                return (
                    f"RECORDED ({done_count}/{total_questions}). "
                    f"⚠️ {len(remaining)} questions left. "
                    f"NEXT QUESTION → \"{next_text}\" (question_id: {next_id}). "
                    f"Ask it now."
                )
            else:
                survey_finished["done"] = True
                logger.info(f"✅ ALL {total_questions} questions answered — telling agent to close")

                return (
                    f"RECORDED ({done_count}/{total_questions}). "
                    f"✅ ALL DONE. Now do these two things IN ORDER: "
                    f"1) Say: \"Thanks so much for sharing your thoughts, {person_name}. "
                    f"I really appreciate your time, and I hope you have a great rest of your day!\" "
                    f"2) Then call end_survey(\"completed\")."
                )
        return f"Recorded {question_id}."

    @function_tool()
    async def end_survey(context: RunContext, reason: str = "completed"):
        """
        End the survey call and hang up. Say your full goodbye BEFORE calling this.

        Args:
            reason: Why the call is ending — completed, wrong_person, declined, callback_scheduled, link_sent
        """
        logger.info(f"📞 end_survey called — reason: {reason}")
        await _save_and_disconnect(reason)
        return "Call ended."

    @function_tool()
    async def schedule_callback(context: RunContext, preferred_time: str):
        """
        Schedule a callback for the person at their preferred time.
        Use this when the person says they are busy but would like a call back later.

        Args:
            preferred_time: When they want to be called back (e.g. "tomorrow at 3pm", "next Monday morning")
        """
        logger.info(f"📅 Scheduling callback for {caller_number} at: {preferred_time}")
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
                f"{SCHEDULER_SERVICE_URL}/scheduler/schedule-call",
                {"survey_id": survey_id, "phone": caller_number, "delay_seconds": str(delay)},
            )

        return f"Callback scheduled for {preferred_time}. Now say goodbye and call end_survey(reason='callback_scheduled')."

    @function_tool()
    async def send_survey_link(context: RunContext):
        """
        Send the survey link to the person via email or text so they can fill it out at their convenience.
        Use this when the person declines a callback but agrees to receive the survey link.
        """
        logger.info(f"📧 Sending survey link for survey={survey_id} to {rider_email or caller_number}")

        sent = False
        if survey_id and survey_url and rider_email:
            sent = await _call_service(
                f"{VOICE_SERVICE_URL}/api/voice/send-email-fallback",
                {"survey_id": survey_id, "email": rider_email, "survey_url": survey_url},
            )

        if sent:
            return "Survey link sent successfully. Now say goodbye and call end_survey(reason='link_sent')."
        else:
            return "Could not send link (no email on file). Apologize and say goodbye, then call end_survey(reason='link_sent')."

    return [record_answer, end_survey, schedule_callback, send_survey_link]
