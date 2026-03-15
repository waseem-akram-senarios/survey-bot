"""
Self-contained prompt builders for the demo bot.
All prompts are built locally — not received from voice-service metadata.
"""

from .greeter import build_greeter_prompt
from .questions import build_questions_prompt
from .ending import build_ending_prompt

__all__ = [
    "build_greeter_prompt",
    "build_questions_prompt",
    "build_ending_prompt",
]
