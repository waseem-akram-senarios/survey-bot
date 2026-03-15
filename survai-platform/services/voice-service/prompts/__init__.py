# -*- coding: utf-8 -*-
"""
prompts package — public API for all survey agent prompt builders.

Exports the same interface as the original prompt_builder.py so no
callers outside this package need to change their imports.
"""

from typing import Any, Dict, List, Optional

from .greeter_en import build_greeter_prompt_en
from .greeter_es import build_greeter_prompt_es
from .lang_preference import build_lang_preference_prompt
from .questions_en import build_questions_prompt_en
from .questions_es import build_questions_prompt_es

__all__ = [
    "build_greeter_prompt",
    "build_questions_prompt",
    "build_survey_prompt",
    "build_lang_preference_prompt",
]


def build_greeter_prompt(
    organization_name: str,
    rider_first_name: str,
    language: str = "en",
) -> str:
    """
    Build the greeter agent system prompt.

    language="en": English-only greeter — goes to identity confirmation then availability.
    language="es": Spanish-only greeter — goes to identity confirmation then availability.
    """
    if language not in ("en", "es"):
        raise ValueError(f"language must be 'en' or 'es', got '{language}'")
    
    if language == "es":
        return build_greeter_prompt_es(organization_name, rider_first_name)
    return build_greeter_prompt_en(organization_name, rider_first_name)


async def build_questions_prompt(
    organization_name: str,
    rider_first_name: str,
    survey_name: str,
    questions: List[Dict[str, Any]],
    restricted_topics: Optional[List[str]] = None,
    language: str = "en",
) -> Any:
    """
    Build the QuestionsAgent system prompt (~900 tokens).

    Returns:
        tuple: (prompt_text: str, questions_map: dict)
    """
    if language == "es":
        return await build_questions_prompt_es(
            organization_name, rider_first_name, survey_name, questions, restricted_topics
        )
    return await build_questions_prompt_en(
        organization_name, rider_first_name, survey_name, questions, restricted_topics
    )


async def build_survey_prompt(
    organization_name: str,
    rider_first_name: str,
    survey_name: str,
    questions: List[Dict[str, Any]],
    restricted_topics: Optional[List[str]] = None,
    language: str = "en",
) -> str:
    """
    Backward-compatible single prompt (greeter + questions joined).
    Use build_greeter_prompt() and build_questions_prompt() for the multi-agent setup.
    
    language="en": English-only call flow.
    language="es": Spanish-only call flow.
    """
    if language not in ("en", "es"):
        raise ValueError(f"language must be 'en' or 'es', got '{language}'")
    
    greeter = build_greeter_prompt(organization_name, rider_first_name, language=language)
    questions_p, _ = await build_questions_prompt(
        organization_name, rider_first_name, survey_name, questions, restricted_topics, language=language
    )
    return greeter + "\n\n---\n\n" + questions_p
