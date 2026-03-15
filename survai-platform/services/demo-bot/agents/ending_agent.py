"""
Ending / Raffle Agent — third and final agent in the demo call pipeline.

Responsibilities:
  - Copy chat history from QuestionsAgent so the LLM has full context
  - Speak the raffle offer via TTS
  - If they want to enter: collect name + phone, call record_raffle_entry()
  - After raffle (or decline): call end_survey("completed")

Tools: record_raffle_entry, end_survey
"""

from livekit.agents.voice import Agent

from utils.logging import get_logger

logger = get_logger()

RAFFLE_OFFER = (
    "That's all the questions we have — thank you so much for your time. "
    "If you'd like to be entered into our raffle for a chance to win the big prize, "
    "just give us your name and phone number and we'll get you entered."
)


class EndingAgent(Agent):
    """
    Handles the closing raffle offer after all survey questions are complete.
    Collects name + phone for raffle entry, then ends the call.
    """

    def __init__(self, instructions: str, **kwargs):
        super().__init__(instructions=instructions, **kwargs)

    async def on_enter(self) -> None:
        """
        Copy questions agent's chat history, speak raffle offer via TTS,
        inject as assistant message.
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

        system_note = (
            "All survey questions have been completed and recorded. "
            "Do NOT ask any more survey questions. "
            "You are now offering the caller a chance to enter a raffle. "
            "The raffle offer has already been spoken — wait for their response."
        )
        chat_ctx.add_message(role="system", content=system_note)
        await self.update_chat_ctx(chat_ctx)

        logger.info(f"[ENDING] {RAFFLE_OFFER[:80]}...")

        await self.session.say(RAFFLE_OFFER).wait_for_playout()

        chat_ctx_after = self.chat_ctx.copy()
        chat_ctx_after.add_message(role="assistant", content=RAFFLE_OFFER)
        await self.update_chat_ctx(chat_ctx_after)
