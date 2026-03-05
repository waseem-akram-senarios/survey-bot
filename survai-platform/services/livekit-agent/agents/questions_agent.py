"""
Questions Agent — second agent in the call, activated after identity + availability confirmed.

Responsibilities:
  - Copy chat history from the GreeterAgent so the LLM has full context
  - Speak Q1 directly via TTS, then inject it as an assistant turn so the LLM
    knows Q1 was already asked and simply waits for the caller's answer
  - Ask all survey questions, record answers, handle mid-call exits
  - End call via end_survey("completed") or end_survey("declined")

Tools: record_answer, end_survey
"""

from typing import Annotated

from livekit.agents.voice import Agent
from livekit.agents import function_tool

from utils.logging import get_logger

logger = get_logger()


class QuestionsAgent(Agent):
    """
    Focuses solely on conducting the survey questions.
    Receives a ~900-token prompt with the full questions block.
    """

    def __init__(self, instructions: str, language: str = "en", **kwargs):
        super().__init__(instructions=instructions, **kwargs)
        self._language = language

    @function_tool
    async def set_language(
        self,
        language: Annotated[str, "Language code: 'en' for English, 'es' for Spanish"],
    ) -> str:
        """Switch the survey language ONLY if the recipient explicitly asks to change. Do NOT call this proactively."""
        self.session.userdata.detected_language = language
        logger.info(f"[LANGUAGE] Recipient switched language to: {language}")
        if language == "es":
            return (
                "Language LOCKED to Spanish. From now on you MUST speak ONLY in Spanish. "
                "Use ONLY the ES version of each question. NEVER use English again. "
                "Re-ask the current question using the ES version now."
            )
        return (
            "Language LOCKED to English. From now on you MUST speak ONLY in English. "
            "Use ONLY the EN version of each question. NEVER use Spanish again. "
            "Re-ask the current question using the EN version now."
        )

    async def on_enter(self) -> None:
        """
        Copy greeter's chat history so the LLM has full context,
        speak Q1 directly via TTS, then inject it as an assistant turn.

        Injecting Q1 as an assistant message prevents preemptive_generation
        from firing an LLM response that would double-ask Q1 or jump to Q2
        before the user has answered anything.
        """
        userdata = self.session.userdata
        chat_ctx = self.chat_ctx.copy()

        if userdata.prev_agent is not None:
            truncated = userdata.prev_agent.chat_ctx.copy(
                exclude_instructions=False, exclude_function_call=False
            ).truncate(max_items=20)
            existing_ids = {item.id for item in chat_ctx.items}
            new_items = [item for item in truncated.items if item.id not in existing_ids]
            chat_ctx.items.extend(new_items)

        lang = getattr(userdata, "detected_language", "en")

        if userdata.question_ids:
            first_q_id = userdata.question_ids[0]
            first_q_text = userdata.questions_map.get(first_q_id, "")
            if first_q_text:
                if lang == "es":
                    intro = "¡Perfecto, comencemos!"
                    system_note = (
                        "Identity and availability have been confirmed by the greeter. "
                        "Do NOT re-introduce yourself or ask for availability again.\n\n"
                        "*** LANGUAGE LOCKED: SPANISH ***\n"
                        "The recipient chose SPANISH. You MUST speak ONLY in Spanish for the ENTIRE survey.\n"
                        "For each question, use ONLY the ES version. NEVER read or say the EN version.\n"
                        "NEVER switch to English. NEVER mix languages. ALL acknowledgments, transitions, "
                        "and responses must be in Spanish only.\n\n"
                        "The intro '¡Perfecto, comencemos!' was spoken. "
                        "Now ask Q1 in Spanish (use ONLY the ES version). Do NOT use English."
                    )
                else:
                    intro = f"Great, let's get started! {first_q_text}"
                    system_note = (
                        "Identity and availability have been confirmed by the greeter. "
                        "Do NOT re-introduce yourself or ask for availability again.\n\n"
                        "*** LANGUAGE LOCKED: ENGLISH ***\n"
                        "The recipient chose ENGLISH. You MUST speak ONLY in English for the ENTIRE survey.\n"
                        "For each question, use ONLY the EN version. NEVER read or say the ES version.\n"
                        "NEVER switch to Spanish. NEVER mix languages.\n\n"
                        f"Q1 is already being spoken to the caller verbatim: \"{first_q_text}\". "
                        "Do NOT repeat Q1. Wait silently for the caller's answer."
                    )

                chat_ctx.add_message(role="system", content=system_note)
                await self.update_chat_ctx(chat_ctx)

                await self.session.say(intro).wait_for_playout()

                chat_ctx2 = self.chat_ctx.copy()
                chat_ctx2.add_message(role="assistant", content=intro)
                await self.update_chat_ctx(chat_ctx2)

                if lang == "es":
                    await self.session.generate_reply()
                return

        if lang == "es":
            fallback_msg = (
                "La identidad y disponibilidad han sido confirmadas por el saludo inicial. "
                "NO te vuelvas a presentar ni preguntes por disponibilidad.\n\n"
                "*** IDIOMA BLOQUEADO: ESPAÑOL ***\n"
                "DEBES responder SIEMPRE y ÚNICAMENTE en español. NUNCA uses inglés.\n"
                "Comienza la encuesta inmediatamente con la primera pregunta en español."
            )
        else:
            fallback_msg = (
                "Identity and availability have been confirmed by the greeter. "
                "Do NOT re-introduce yourself or ask for availability again.\n\n"
                "*** LANGUAGE LOCKED: ENGLISH ***\n"
                "You MUST speak ONLY in English. NEVER use Spanish.\n"
                "Start the survey immediately with Q1."
            )
        chat_ctx.add_message(role="system", content=fallback_msg)
        await self.update_chat_ctx(chat_ctx)
        await self.session.generate_reply()
