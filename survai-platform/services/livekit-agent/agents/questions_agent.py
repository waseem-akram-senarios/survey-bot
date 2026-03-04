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

from livekit.agents.voice import Agent

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
                if self._language == "es":
                    intro = f"¡Perfecto, comencemos! {first_q_text}"
                else:
                    intro = f"Great, let's get started! {first_q_text}"

                if self._language == "es":
                    system_msg = (
                        "La identidad y disponibilidad han sido confirmadas por el saludo inicial. "
                        "NO te vuelvas a presentar ni preguntes por disponibilidad. "
                        f"La primera pregunta ya se está pronunciando al llamante textualmente: \"{first_q_text}\". "
                        "NO repitas la primera pregunta. Espera en silencio la respuesta del llamante. "
                        "DEBES responder SIEMPRE en español."
                    )
                else:
                    system_msg = (
                        "Identity and availability have been confirmed by the greeter. "
                        "Do NOT re-introduce yourself or ask for availability again. "
                        f"Q1 is already being spoken to the caller verbatim: \"{first_q_text}\". "
                        "Do NOT repeat Q1. Wait silently for the caller's answer."
                    )
                chat_ctx.add_message(role="system", content=system_msg)
                await self.update_chat_ctx(chat_ctx)

                # Speak Q1 and wait for full audio playout before returning
                await self.session.say(intro).wait_for_playout()

                # Inject Q1 as an assistant message so the LLM sees it was spoken
                # and won't generate a duplicate or jump to Q2 unprompted
                chat_ctx2 = self.chat_ctx.copy()
                chat_ctx2.add_message(role="assistant", content=intro)
                await self.update_chat_ctx(chat_ctx2)
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
