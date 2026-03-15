"""
Language Preference Agent — always the first agent in every call.

Responsibilities:
  - Speak an opening greeting in the initial language (EN or ES)
  - Present the exact bilingual language preference question
  - Use set_language tool to record the caller's language choice
  - Transition to the appropriate greeter agent (EN or ES) via to_greeter tool

Call flow:
  1. on_enter(): speak greeting in initial_language, then ask bilingual preference question
  2. Caller responds in their preferred language
  3. Agent calls set_language("en"|"es") to record preference
  4. Agent calls to_greeter() to hand off to EnglishGreeterAgent or SpanishGreeterAgent

This agent does NOT handle identity or availability - that's the greeter's job.

Tools: set_language, to_greeter, end_survey
"""

import asyncio

from livekit.agents.voice import Agent

from config.settings import ORGANIZATION_NAME
from utils.logging import get_logger

logger = get_logger()


class LanguagePreferenceAgent(Agent):
    """
    First agent in every call. Asks the caller which language they prefer,
    then transitions to the appropriate greeter agent.
    """

    def __init__(
        self,
        instructions: str,
        organization_name: str,
        rider_first_name: str,
        initial_language: str = "en",
        **kwargs,
    ):
        """
        Initialize the language preference agent.

        Args:
            instructions: System prompt for the agent (from voice-service)
            organization_name: Organization name for the greeting
            rider_first_name: Recipient's first name (for context, not used in greeting)
            initial_language: Which language to start speaking ("en" or "es")
                             This determines the opening greeting language only
        """
        super().__init__(instructions=instructions, **kwargs)
        self.organization_name = organization_name or ORGANIZATION_NAME
        self.rider_first_name = rider_first_name
        self.initial_language = initial_language

    async def on_enter(self) -> None:
        """
        Speak the opening greeting in the initial language, then present the
        bilingual language preference question. Wait for playout before LLM takes over.
        """
        await asyncio.sleep(1.5)

        org = self.organization_name

        # Single greeting with language preference question
        if self.initial_language == "es":
            full_greeting = (
                f"Hola, mi nombre es Cameron y llamo de {org}. Me gustaría realizar una breve encuesta contigo. "
                "Para continuar en español, di español."
                "To continue in English, say English."
            )
        else:
            full_greeting = (
                f"Hi, I'm Cameron from {org}. I'd like to conduct a brief survey with you. "
                "To continue in English, say English."
                "Para continuar en español, di español."
            )

        logger.info(f"[LANG-AGENT] initial_lang={self.initial_language} | greeting={full_greeting[:100]}...")

        await self.session.say(full_greeting).wait_for_playout()

        # Inject AFTER playout so preemptive_generation doesn't race with TTS
        chat_ctx = self.chat_ctx.copy()
        chat_ctx.add_message(role="assistant", content=full_greeting)
        await self.update_chat_ctx(chat_ctx)
