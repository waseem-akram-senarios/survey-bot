"""
English-only question block formatter for system prompts.
"""

from typing import Any, Dict


def _format_question_en(order: int, q: Dict[str, Any]) -> str:
    """Format a single question block for the English-only agent prompt."""
    qid = q.get("id", f"q{order}")
    text = q.get("text", "")
    criteria = q.get("criteria", "open")
    categories = q.get("categories", [])
    scale_max = q.get("scales") or 5
    parent_id = q.get("parent_id")
    parent_order = q.get("_parent_order", "")
    trigger_cats = q.get("parent_category_texts", [])

    question_text = f'"{text}"'

    if parent_id:
        trigger_str = ", ".join(trigger_cats) if trigger_cats else "any answer"
        return (
            f"Q{order} [{qid}] CONDITIONAL (ask ONLY IF the answer to Q{parent_order} "
            f"includes: {trigger_str}): {question_text}\n"
            f"  Skip entirely if the condition is not met."
        )
    elif criteria == "scale":
        return (
            f"Q{order} [{qid}] SCALE 1-{scale_max} (1=very poor, {scale_max}=excellent): {question_text}\n"
            f"  Ask it word-for-word. Always tell the caller: '1 is very poor, {scale_max} is excellent.'\n"
            f"  If they give a word instead of a number, ask once: \"If you had to put a number on it — where 1 is very poor and {scale_max} is excellent — what number between 1 and {scale_max} would you give?\"\n"
            f"  After recording their answer: give ONE brief acknowledgment sentence, then move to the next question.\n"
            f"  Do NOT ask a follow-up or probe in the same response as the acknowledgment."
        )
    elif criteria == "categorical":
        cats_str = ", ".join(categories) if categories else "open"
        if categories:
            return (
                f"Q{order} [{qid}] CHOICE [{cats_str}]: {question_text}\n"
                f"  ALWAYS read the options aloud after asking the question.\n"
                f"  Say something like: \"Your options are: {cats_str}.\"\n"
                f"  Accept their choice. If unclear, repeat the options once.\n"
                f"  Negative choice: empathize briefly and move on.\n"
                f"  Positive choice: acknowledge briefly and move on."
            )
        return (
            f"Q{order} [{qid}] CHOICE: {question_text}\n"
            f"  Let them answer freely.\n"
            f"  Negative choice: empathize briefly and move on.\n"
            f"  Positive choice: acknowledge briefly and move on."
        )
    else:
        return (
            f"Q{order} [{qid}] OPEN: {question_text}\n"
            f"  If vague (\"fine\", \"okay\", \"good\") — probe gently with ONE clarifying question.\n"
            f"  If detailed — acknowledge warmly and move on.\n"
            f"  If emotional — validate first, then continue."
        )
