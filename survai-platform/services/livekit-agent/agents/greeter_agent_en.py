"""
English Greeter Agent — first agent for English and bilingual calls.

Supports two modes:
  - language_mode="bilingual": asks caller to choose English or Spanish, then verifies identity
  - language_mode="en": English-only, skips language question, goes straight to identity

Call flow (bilingual):
  1. on_enter(): "Hi, I'm Cameron... To continue in English say English / Para continuar en español..."
  2. Language preference → set_language()
  3. Identity → Availability → to_questions()

Call flow (English-only):
  1. on_enter(): "Hi, I'm Cameron... Am I speaking with {name}?"
  2. Identity → Availability → to_questions()
"""

import asyncio
import re
from typing import Annotated

from livekit.agents.voice import Agent
from livekit.agents import function_tool

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
    Handles opening, language detection, identity confirmation, and availability check
    for English-initiated calls. Hands off to the correct QuestionsAgent once the
    recipient confirms they are available.
    """

    def __init__(
        self,
        instructions: str,
        rider_first_name: str,
        organization_name: str = None,
        greetings: str = "",
        language_mode: str = "bilingual",
        **kwargs,
    ):
        super().__init__(instructions=instructions, **kwargs)
        self.rider_first_name = rider_first_name
        self.organization_name = organization_name or ORGANIZATION_NAME
        self.greetings = greetings
        self.language_mode = language_mode

    @function_tool
    async def set_language(
        self,
        language: Annotated[str, "Language code: 'en' for English, 'es' for Spanish"],
    ) -> str:
        """
        Record the recipient's language preference detected from their reply.
        Call this as soon as the language is clear. This LOCKS the language for the entire call.
        """
        self.session.userdata.detected_language = language
        logger.info(f"[LANGUAGE] Recipient selected: {language}")

        name = self.rider_first_name
        name_known = _is_real_name(name)

        if language == "es":
            next_q = (
                f"¿Estoy hablando con {name}?"
                if name_known
                else "¿Con quién tengo el gusto de hablar?"
            )
            return f"Español confirmado. Pregunta: '{next_q}'"

        next_q = (
            f"Am I speaking with {name}?"
            if name_known
            else "May I know who I'm speaking with?"
        )
        return f"English confirmed. Ask: '{next_q}'"

    async def on_enter(self) -> None:
        """Speak the opening line and wait for full playout before the LLM takes over."""
        await asyncio.sleep(1.5)

        org = self.organization_name
        name = self.rider_first_name

        if self.greetings:
            greeting = self.greetings
        elif self.language_mode == "en":
            if _is_real_name(name):
                greeting = (
                    f"Hi, I'm Cameron from {org}. I'd like to conduct a brief survey with you. "
                    f"Am I speaking with {name}?"
                )
            else:
                greeting = (
                    f"Hi, I'm Cameron from {org}. I'd like to conduct a brief survey with you. "
                    "May I know who I'm speaking with?"
                )
        else:
            greeting = (
                f"Hi, I'm Cameron from {org}. I'd like to conduct a brief survey with you. "
                "To continue in English, say English. "
                "Para continuar en español, di español."
            )

        logger.info(f"[AGENT] {greeting}")
        await self.session.say(greeting).wait_for_playout()
