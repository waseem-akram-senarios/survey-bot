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
        """Switch the survey language mid-call if the recipient requests it."""
        self.session.userdata.detected_language = language
        logger.info(f"[LANGUAGE] Recipient switched language to: {language}")
        if language == "es":
            return "Language switched to Spanish. Re-ask the current question in Spanish and continue entirely in Spanish."
        return "Language switched to English. Re-ask the current question in English and continue entirely in English."

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

        if userdata.question_ids:
            first_q_id = userdata.question_ids[0]
            first_q_text = userdata.questions_map.get(first_q_id, "")
            if first_q_text:
                lang = getattr(userdata, "detected_language", "en")
                if lang == "es":
                    # For Spanish, let the LLM speak Q1 in Spanish from the prompt
                    # rather than TTS-speaking the English question text
                    intro = "¡Perfecto, comencemos!"
                    spoken_q1 = intro
                else:
                    intro = f"Great, let's get started! {first_q_text}"
                    spoken_q1 = first_q_text

                # Tell the LLM Q1 status — for Spanish, instruct it to ask Q1 in Spanish
                if lang == "es":
                    system_note = (
                        "Identity and availability have been confirmed by the greeter. "
                        "Do NOT re-introduce yourself or ask for availability again. "
                        "The intro '¡Perfecto, comencemos!' was spoken. "
                        "Now ask Q1 in Spanish (use the [ES] version from the QUESTIONS section). "
                        "Do NOT use the English version."
                    )
                else:
                    system_note = (
                        "Identity and availability have been confirmed by the greeter. "
                        "Do NOT re-introduce yourself or ask for availability again. "
                        f"Q1 is already being spoken to the caller verbatim: \"{first_q_text}\". "
                        "Do NOT repeat Q1. Wait silently for the caller's answer."
                    )

                chat_ctx.add_message(role="system", content=system_note)
                await self.update_chat_ctx(chat_ctx)

                # Speak the intro and wait for full audio playout before returning
                await self.session.say(intro).wait_for_playout()

                # For English: inject Q1 as assistant message so LLM won't repeat it.
                # For Spanish: inject only the intro — LLM will generate Q1 in Spanish.
                chat_ctx2 = self.chat_ctx.copy()
                chat_ctx2.add_message(role="assistant", content=intro)
                await self.update_chat_ctx(chat_ctx2)

                # For Spanish, generate the LLM reply so it asks Q1 in Spanish
                if lang == "es":
                    await self.session.generate_reply()
                return

        if self._language == "es":
            fallback_msg = (
                "La identidad y disponibilidad han sido confirmadas por el saludo inicial. "
                "NO te vuelvas a presentar ni preguntes por disponibilidad. "
                "Comienza la encuesta inmediatamente con la primera pregunta. "
                "DEBES responder SIEMPRE en español."
            )
        else:
            fallback_msg = (
                "Identity and availability have been confirmed by the greeter. "
                "Do NOT re-introduce yourself or ask for availability again. "
                "Start the survey immediately with Q1."
            )
        chat_ctx.add_message(role="system", content=fallback_msg)
        await self.update_chat_ctx(chat_ctx)
        await self.session.generate_reply()
