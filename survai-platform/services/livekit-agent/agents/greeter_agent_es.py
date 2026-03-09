"""
Spanish Greeter Agent — first agent for Spanish-language calls.

Call flow:
  1. on_enter(): speak Spanish opening greeting / identity question
  2. STEP 1 — Identity: confirm who they are (in Spanish)
  3. STEP 2 — Availability: ask if they have time (in Spanish)
  4. Hand off via to_questions() → loads SpanishQuestionsAgent

No language-preference step — the call language is always Spanish.

Tools (from survey_tools): end_survey, schedule_callback, send_survey_link, to_questions
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


class SpanishGreeterAgent(Agent):
    """
    Handles identity confirmation and availability check entirely in Spanish.
    Language preference is not asked — the call is always in Spanish.
    Hands off to SpanishQuestionsAgent when the recipient confirms availability.
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
        # Ensure detected_language is pre-set for any tools/agents that read it

    async def on_enter(self) -> None:
        """Speak the Spanish opening greeting and wait for playout before the LLM takes over."""
        await asyncio.sleep(0.8)

        if self.greetings:
            greeting = self.greetings
        else:
            name = self.rider_first_name
            org = self.organization_name

            if _is_real_name(name):
                greeting = (
                    f"Hola, mi nombre es Cameron y estoy llamando de parte de {org}. "
                    f"¿Estoy hablando con {name}?"
                )
            else:
                greeting = (
                    f"Hola, mi nombre es Cameron y estoy llamando de parte de {org}. "
                    f"¿Con quién tengo el gusto de hablar?"
                )

        logger.info(f"[AGENT] {greeting}")
        self.session.say(greeting)
