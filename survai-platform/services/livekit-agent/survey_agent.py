"""
Survey Agent class definition.
Contains the main Agent that conducts customer surveys.
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


class SurveyAgent(Agent):
    def __init__(self, instructions: str, rider_first_name: str, organization_name: str = None, language: str = "en", **kwargs):
        super().__init__(instructions=instructions, **kwargs)
        self.rider_first_name = rider_first_name
        self.organization_name = organization_name or ORGANIZATION_NAME
        self.language = language

    def _is_real_name(self, name: str) -> bool:
        if not name or not name.strip():
            return False
        clean = name.strip()
        if clean.lower() in PLACEHOLDER_NAMES:
            return False
        if _PLACEHOLDER_PATTERN.match(clean):
            return False
        alpha_only = re.sub(r"[^a-zA-Z]", "", clean)
        return len(alpha_only) >= 2

    async def on_enter(self):
        """Speak the greeting, then hand control to the LLM for the survey flow."""
        await asyncio.sleep(0.8)

        name = self.rider_first_name
        org = self.organization_name
        is_spanish = self.language == "es"

        if self._is_real_name(name):
            if is_spanish:
                greeting = (
                    f"Hola, soy Cameron de {org}. "
                    f"¿Estoy hablando con {name}?"
                )
            else:
                greeting = (
                    f"Hi, this is Cameron with {org}. "
                    f"Am I speaking to {name}?"
                )
        else:
            if is_spanish:
                greeting = (
                    f"Hola, soy Cameron de {org}. "
                    f"Me comunico para obtener sus comentarios. ¿Es un buen momento?"
                )
            else:
                greeting = (
                    f"Hi, this is Cameron with {org}. "
                    f"I'm reaching out to get your quick feedback. Is now a good time?"
                )
        logger.info(f"[AGENT] {greeting}")
        await self.session.say(greeting)
