"""
Greeter Agent — first agent in the call.

Responsibilities:
  - Speak the opening greeting (introduce Cameron + org, confirm identity)
  - Handle availability check
  - End call early: wrong_person, not_available, callback_scheduled, link_sent, declined
  - Hand off to QuestionsAgent via the to_questions tool once availability is confirmed

Tools: end_survey, schedule_callback, send_survey_link, to_questions
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


class GreeterAgent(Agent):
    """
    Handles identity confirmation and availability check.
    Hands off to QuestionsAgent when the person confirms they're available.
    """

    def __init__(
        self,
        instructions: str,
        rider_first_name: str,
        organization_name: str = None,
        language: str = "en",
        **kwargs,
    ):
        super().__init__(instructions=instructions, **kwargs)
        self.rider_first_name = rider_first_name
        self.organization_name = organization_name or ORGANIZATION_NAME
        self.language = language

    async def on_enter(self) -> None:
        """Speak the opening greeting and wait for full playout before LLM takes over."""
        await asyncio.sleep(0.8)

        name = self.rider_first_name
        org = self.organization_name
        is_spanish = self.language == "es"

        if _is_real_name(name):
            if is_spanish:
                greeting = (
                    f"Hola, mi nombre es Cameron y estoy llamando de parte de {org}. "
                    f"¿Estoy hablando con {name}?"
                )
            else:
                greeting = (
                    f"Hi there, my name is Cameron and I'm calling on behalf of {org}. "
                    f"Am I speaking with {name}?"
                )
        else:
            if is_spanish:
                greeting = (
                    f"Hola, mi nombre es Cameron y estoy llamando de parte de {org}. "
                    f"Me comunico para obtener sus comentarios. ¿Podría saber con quién estoy hablando?"
                )
            else:
                greeting = (
                    f"Hi there, my name is Cameron and I'm calling on behalf of {org}. "
                    f"May I know who I'm speaking with?"
                )

        logger.info(f"[AGENT] {greeting}")
        speech_handle = self.session.say(greeting)
        await speech_handle.wait_for_playout()
