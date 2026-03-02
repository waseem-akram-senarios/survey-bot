"""
Survey function tools — two tools that cover the full call lifecycle:
  - record_answer(question_id, answer) — store any survey answer
  - end_survey(reason)                 — save data, speak farewell, wait for playout, hang up
"""

import asyncio
from datetime import datetime
from typing import Callable, List

from livekit.agents import function_tool, RunContext

from utils.logging import get_logger
from utils.storage import save_survey_responses

logger = get_logger()

POST_FAREWELL_BUFFER_SECONDS = 2.0


def create_survey_tools(
    survey_responses: dict,
    caller_number: str,
    call_start_time: datetime,
    log_handler,
    cleanup_logging_fn: Callable,
    disconnect_fn: Callable = None,
    question_ids: List[str] = None,
):
    total_questions = len(question_ids) if question_ids else 0

    @function_tool()
    async def record_answer(context: RunContext, question_id: str, answer: str):
        """
        Record the caller's answer to a survey question.

        Args:
            question_id: The question identifier (e.g. "q1", "overall_satisfaction")
            answer: The caller's response in their own words
        """
        survey_responses["answers"][question_id] = answer
        done = list(survey_responses["answers"].keys())
        done_count = len(done)
        logger.info(f"[{question_id}] ({done_count}/{total_questions}) {answer[:120]}")

        if question_ids:
            remaining = [q for q in question_ids if q not in done]
            if remaining:
                return (
                    f"Recorded {question_id}. "
                    f"Progress: {done_count}/{total_questions} done. "
                    f"ALREADY ASKED (do NOT repeat): {', '.join(done)}. "
                    f"NEXT question to ask: {remaining[0]}. "
                    f"Remaining: {', '.join(remaining)}."
                )
            else:
                return (
                    f"Recorded {question_id}. "
                    f"ALL {total_questions} questions are done. "
                    f"Call end_survey(reason='completed') now."
                )
        return f"Recorded {question_id}."

    @function_tool()
    async def end_survey(context: RunContext, reason: str = "completed"):
        """
        End the call: save survey data, speak farewell, wait for it to finish, then hang up.
        This is the ONLY way to end a call. One call to this tool does everything.

        Args:
            reason: Why the call is ending — completed, wrong_person, declined, not_available
        """
        if reason == "completed" and question_ids:
            done = set(survey_responses["answers"].keys())
            remaining = [q for q in question_ids if q not in done]
            if remaining:
                logger.warning(
                    f"end_survey(completed) blocked — {len(remaining)} required questions unanswered: "
                    f"{', '.join(remaining)}"
                )
                return (
                    f"Cannot end as 'completed' yet — {len(remaining)} required question(s) still unanswered: "
                    f"{', '.join(remaining)}. "
                    f"You MUST ask these before ending. Next to ask: {remaining[0]}."
                )

        logger.info(f"end_survey called — reason: {reason}")
        survey_responses["end_reason"] = reason
        survey_responses["completed"] = reason == "completed"

        call_duration = (datetime.now() - call_start_time).total_seconds()
        save_survey_responses(caller_number, survey_responses, call_duration)
        cleanup_logging_fn(log_handler)

        rider_name = survey_responses.get("rider_name", "").strip()
        name_part = f", {rider_name}" if rider_name else ""

        if reason == "completed":
            farewell = (
                f"Thanks so much for sharing your thoughts{name_part}! "
                "I really appreciate your time, and I hope you have a great rest of your day! Goodbye!"
            )
        elif reason in ("not_available", "callback_scheduled"):
            farewell = "Fantastic! We'll be in touch. Thank you for your time, and have a wonderful day! Goodbye!"
        elif reason == "wrong_person":
            farewell = "I apologize for the mix-up! Have a great day! Goodbye!"
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

    return [record_answer, end_survey]
