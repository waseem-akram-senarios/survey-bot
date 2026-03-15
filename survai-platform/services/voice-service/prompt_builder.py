# -*- coding: utf-8 -*-
"""
Thin shim — re-exports the public prompt-builder API from the prompts package.

All logic now lives in prompts/ (one file per agent).
This file is kept so existing imports like:
    from prompt_builder import build_greeter_prompt, build_questions_prompt
continue to work without any changes to callers.
"""

from prompts import build_greeter_prompt, build_questions_prompt, build_survey_prompt, build_lang_preference_prompt

__all__ = ["build_greeter_prompt", "build_questions_prompt", "build_survey_prompt", "build_lang_preference_prompt"]