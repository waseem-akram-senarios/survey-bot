"""
Greeting Agent — first agent in every demo call.

Call flow:
  1. on_enter(): speak hardcoded opening message
  2. Confirm availability (NOT identity — no identity check in demo)
  3. If available → hand off via to_questions()
  4. If not available → end_survey("not_available") or schedule_callback / send_survey_link

Tools (from demo_tools): to_questions, schedule_callback, send_survey_link, end_survey
"""

import asyncio

from livekit.agents.voice import Agent

from config.settings import ORGANIZATION_NAME
from utils.logging import get_logger

logger = get_logger()

HARDCODED_OPENING = (
    "Hi, thanks for taking a few minutes to chat with us. "
    "We're conducting a quick survey on AI adoption in public transportation agencies. "
    "This will only take about two minutes."
)


class GreetingAgent(Agent):
    """
    Handles the opening greeting and availability check.
    No identity confirmation — goes straight to asking if they have time.
    Hands off to QuestionsAgent once the recipient confirms availability.
    """

    def __init__(
        self,
        instructions: str,
        organization_name: str = None,
        **kwargs,
    ):
        super().__init__(instructions=instructions, **kwargs)
        self.organization_name = organization_name or ORGANIZATION_NAME

    async def on_enter(self) -> None:
        """Speak the hardcoded opening and wait for a response."""
        await asyncio.sleep(1.0)

        greeting = HARDCODED_OPENING

        logger.info(f"[GREETER] {greeting[:80]}...")

        await self.session.say(greeting).wait_for_playout()

        chat_ctx = self.chat_ctx.copy()
        chat_ctx.add_message(role="assistant", content=greeting)
        await self.update_chat_ctx(chat_ctx)
