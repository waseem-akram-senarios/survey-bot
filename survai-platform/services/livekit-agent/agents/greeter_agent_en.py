"""
English Greeter Agent — handles identity and availability confirmation in English.

Call flow:
  1. on_enter(): speak English opening greeting with identity question
  2. STEP 1 — Identity: confirm who they are
  3. STEP 2 — Availability: ask if they have time
  4. Hand off via to_questions() → loads EnglishQuestionsAgent

No language-preference step — that's handled by LanguagePreferenceAgent.

Tools (from survey_tools): to_questions, schedule_callback, send_survey_link, end_survey
"""

import asyncio
import re

from livekit.agents.voice import Agent

from config.settings import ORGANIZATION_NAME
from utils.logging import get_logger

logger = get_logger()

PLACEHOLDER_NAMES = {
    "customer", "unknown", "user", "recipient", "test",
    "n/a", "na", "none", "name",
}

_PLACEHOLDER_PATTERN = re.compile(
    r"^(rider|user|customer|recipient|test)\s*\d*$", re.IGNORECASE
)


def _is_real_name(name: str) -> bool:
    if not name or not name.strip():
        return False
    clean = name.strip()
    if clean.lower() in PLACEHOLDER_NAMES:
        return False
    if _PLACEHOLDER_PATTERN.match(clean):
        return False
    alpha_only = re.sub(r"[^a-zA-Z]", "", clean)
    return len(alpha_only) >= 2


class EnglishGreeterAgent(Agent):
    """
    Handles identity confirmation and availability check in English.
    Hands off to EnglishQuestionsAgent once the recipient confirms availability.
    """

    def __init__(
        self,
        instructions: str,
        rider_first_name: str,
        organization_name: str = None,
        greetings: str = "",
        **kwargs,
    ):
        super().__init__(instructions=instructions, **kwargs)
        self.rider_first_name = rider_first_name
        self.organization_name = organization_name or ORGANIZATION_NAME
        self.greetings = greetings

    async def on_enter(self) -> None:
        """Go straight to identity confirmation (lang-agent already introduced)."""
        await asyncio.sleep(0.5)

        name = self.rider_first_name

        if self.greetings:
            greeting = self.greetings
        elif _is_real_name(name):
            greeting = f"Great. Am I speaking with {name}?"
        else:
            greeting = "Great. May I know who I'm speaking with?"

        logger.info(f"[GREETER EN] {greeting[:80]}...")

        await self.session.say(greeting).wait_for_playout()

        # Inject AFTER playout so preemptive_generation doesn't race with TTS
        chat_ctx = self.chat_ctx.copy()
        chat_ctx.add_message(role="assistant", content=greeting)
        await self.update_chat_ctx(chat_ctx)
