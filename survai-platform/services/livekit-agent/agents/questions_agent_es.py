"""
Spanish Questions Agent — second agent for Spanish-language calls.

Responsibilities:
  - Copy chat history from the GreeterAgent so the LLM has full context
  - Speak the Spanish intro via TTS, generate Q1 in Spanish, then inject it
    as an assistant turn so the LLM waits for the caller's answer
  - Ask all survey questions in Spanish, record answers, handle mid-call exits
  - End call via end_survey("completed") or end_survey("declined")

Language: always Spanish. No set_language tool. No bilingual branching.

Tools: record_answer, end_survey
"""

from livekit.agents.voice import Agent

from utils.logging import get_logger

logger = get_logger()


class SpanishQuestionsAgent(Agent):
    """
    Focuses solely on conducting the survey questions in Spanish.
    Receives a ~900-token Spanish-only prompt with translated questions.
    """

    def __init__(self, instructions: str, **kwargs):
        super().__init__(instructions=instructions, **kwargs)

    async def on_enter(self) -> None:
        """
        Copy greeter's chat history, speak the Spanish intro via TTS, then
        generate Q1 in Spanish so the LLM takes over from there.
        """
        userdata = self.session.userdata
        chat_ctx = self.chat_ctx.copy()

        # Carry over context from the greeter agent
        if userdata.prev_agent is not None:
            truncated = userdata.prev_agent.chat_ctx.copy(
                exclude_instructions=False, exclude_function_call=False
            ).truncate(max_items=20)
            existing_ids = {item.id for item in chat_ctx.items}
            new_items = [item for item in truncated.items if item.id not in existing_ids]
            chat_ctx.items.extend(new_items)

        if userdata.question_ids:
            first_q_id = userdata.question_ids[0]
            first_q_text = (
                userdata.questions_map_es.get(first_q_id, "")
                or userdata.questions_map.get(first_q_id, "")
            )
            if first_q_text:
                intro = f"¡Perfecto, comencemos! {first_q_text}"
                system_note = (
                    "La identidad y disponibilidad han sido confirmadas por el saludo inicial. "
                    "NO te vuelvas a presentar ni preguntes por disponibilidad.\n\n"
                    "*** IDIOMA: ESPAÑOL ***\n"
                    "DEBES hablar SIEMPRE y ÚNICAMENTE en español. NUNCA uses inglés.\n\n"
                    f"La pregunta 1 (P1) ya ha sido leída al receptor: \"{first_q_text}\". "
                    "NO repitas P1. Espera en silencio a que el receptor responda."
                )
                chat_ctx.add_message(role="system", content=system_note)
                await self.update_chat_ctx(chat_ctx)

                await self.session.say(intro).wait_for_playout()

                chat_ctx_after_intro = self.chat_ctx.copy()
                chat_ctx_after_intro.add_message(role="assistant", content=intro)
                await self.update_chat_ctx(chat_ctx_after_intro)
                return

        # Fallback: no questions or missing Q1 text
        fallback_msg = (
            "La identidad y disponibilidad han sido confirmadas por el saludo inicial. "
            "NO te vuelvas a presentar ni preguntes por disponibilidad.\n\n"
            "*** IDIOMA: ESPAÑOL ***\n"
            "DEBES responder SIEMPRE y ÚNICAMENTE en español. NUNCA uses inglés.\n"
            "Comienza la encuesta inmediatamente con la primera pregunta en español."
        )
        chat_ctx.add_message(role="system", content=fallback_msg)
        await self.update_chat_ctx(chat_ctx)
        await self.session.generate_reply()
