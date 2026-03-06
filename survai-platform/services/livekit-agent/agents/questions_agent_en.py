"""
English Questions Agent — second agent for English-language calls.

Responsibilities:
  - Copy chat history from the GreeterAgent so the LLM has full context
  - Speak Q1 directly via TTS, then inject it as an assistant turn so the LLM
    knows Q1 was already asked and simply waits for the caller's answer
  - Ask all survey questions in English, record answers, handle mid-call exits
  - End call via end_survey("completed") or end_survey("declined")

Language: always English. No set_language tool. No bilingual branching.

Tools: record_answer, end_survey
"""

from livekit.agents.voice import Agent

from utils.logging import get_logger

logger = get_logger()


class EnglishQuestionsAgent(Agent):
    """
    Focuses solely on conducting the survey questions in English.
    Receives a ~900-token English-only prompt with the full questions block.
    """

    def __init__(self, instructions: str, **kwargs):
        super().__init__(instructions=instructions, **kwargs)

    async def on_enter(self) -> None:
        """
        Copy greeter's chat history, speak Q1 via TTS, inject it as an assistant turn.

        Injecting Q1 as an assistant message prevents preemptive_generation from
        firing an LLM response that would double-ask Q1 or jump to Q2 before the
        user has answered anything.
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
            first_q_text = userdata.questions_map.get(first_q_id, "")
            if first_q_text:
                intro = f"Great, let's get started! {first_q_text}"
                system_note = (
                    "Identity and availability have been confirmed by the greeter. "
                    "Do NOT re-introduce yourself or ask for availability again.\n\n"
                    "*** LANGUAGE: ENGLISH ***\n"
                    "You MUST speak ONLY in English for the ENTIRE survey. NEVER use Spanish.\n\n"
                    f"Q1 is already being spoken to the caller verbatim: \"{first_q_text}\". "
                    "Do NOT repeat Q1. Wait silently for the caller's answer."
                )

                chat_ctx.add_message(role="system", content=system_note)
                chat_ctx.add_message(role="assistant", content=intro)
                await self.update_chat_ctx(chat_ctx)

                self.session.say(intro)
                return

        # Fallback: no questions or missing Q1 text
        fallback_msg = (
            "Identity and availability have been confirmed by the greeter. "
            "Do NOT re-introduce yourself or ask for availability again.\n\n"
            "*** LANGUAGE: ENGLISH ***\n"
            "You MUST speak ONLY in English. NEVER use Spanish.\n"
            "Start the survey immediately with Q1."
        )
        chat_ctx.add_message(role="system", content=fallback_msg)
        await self.update_chat_ctx(chat_ctx)
        await self.session.generate_reply()
