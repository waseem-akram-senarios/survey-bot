"""
Questions Agent — second agent in the call, activated after identity + availability confirmed.

Responsibilities:
  - Copy chat history from the GreeterAgent so the LLM has full context
  - Inject a system message to kick off Q1 immediately
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

    def __init__(self, instructions: str, **kwargs):
        super().__init__(instructions=instructions, **kwargs)

    async def on_enter(self) -> None:
        """
        Copy greeter's chat history so the LLM knows who it's speaking with,
        then inject a system nudge to start Q1 without re-introducing.
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

        chat_ctx.add_message(
            role="system",
            content=(
                "Identity and availability have been confirmed by the greeter. "
                "Do NOT re-introduce yourself or ask for availability again. "
                "Start the survey immediately with Q1."
            ),
        )
        await self.update_chat_ctx(chat_ctx)

        # Speak Q1 directly via TTS — skips one full LLM round-trip
        userdata = self.session.userdata
        if userdata.question_ids:
            first_q_id = userdata.question_ids[0]
            first_q_text = userdata.questions_map.get(first_q_id, "")
            if first_q_text:
                intro = f"Great, let's get started! {first_q_text}"
                await self.session.say(intro).wait_for_playout()
                return

        # Fallback: let LLM ask the first question if no questions are pre-loaded
        await self.session.generate_reply()
