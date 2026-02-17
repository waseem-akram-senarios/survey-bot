"""
Intelligent Agent Brain -- builds the system prompt and VAPI workflow
for a single-node, low-latency AI survey agent.

All context is loaded upfront into the system prompt so the agent
never needs mid-call API fetches.
"""

import logging
from typing import Any, Dict, List, Optional

from prompts import (
    AGENT_SYSTEM_PROMPT_TEMPLATE,
    QUESTION_FORMAT_BRANCH,
    QUESTION_FORMAT_CATEGORICAL,
    QUESTION_FORMAT_OPEN,
    QUESTION_FORMAT_SCALE,
)

logger = logging.getLogger(__name__)


def build_system_prompt(
    survey_name: str,
    questions: List[Dict[str, Any]],
    rider_data: Optional[Dict[str, Any]] = None,
    company_name: str = "the transit agency",
    time_limit_minutes: int = 8,
    restricted_topics: Optional[List[str]] = None,
) -> str:
    """
    Build the complete system prompt for the survey agent.
    All context is baked in upfront for minimum latency.
    """

    # Build rider context
    if rider_data and any(rider_data.values()):
        rider_name = rider_data.get("name", "there")
        rider_lines = [f"- Name: {rider_name}"]
        if rider_data.get("phone"):
            rider_lines.append(f"- Phone: {rider_data['phone']}")
        if rider_data.get("last_ride_date"):
            rider_lines.append(f"- Last ride: {rider_data['last_ride_date']}")
        if rider_data.get("ride_count"):
            rider_lines.append(f"- Total rides: {rider_data['ride_count']}")
        if rider_data.get("biodata"):
            bio = rider_data["biodata"]
            if isinstance(bio, dict):
                for k, v in bio.items():
                    rider_lines.append(f"- {k}: {v}")
            else:
                rider_lines.append(f"- Bio: {bio}")
        rider_context = "\n".join(rider_lines)
        rider_greeting = f", {rider_name}"
    else:
        rider_context = "No rider data available. Ask all questions from scratch."
        rider_name = "there"
        rider_greeting = ""

    # Build questions block
    questions_block = _build_questions_block(questions)

    # Build restricted topics block
    if restricted_topics:
        restricted_topics_block = "\n".join(
            f"- NEVER discuss {topic}" for topic in restricted_topics
        )
    else:
        restricted_topics_block = "- No additional topic restrictions"

    # Calculate time markers
    warning_minutes = max(1, time_limit_minutes - 2)
    hard_stop_minutes = max(2, time_limit_minutes - 1)
    absolute_max_minutes = time_limit_minutes

    prompt = AGENT_SYSTEM_PROMPT_TEMPLATE.format(
        company_name=company_name,
        survey_name=survey_name,
        rider_context=rider_context,
        questions_block=questions_block,
        restricted_topics_block=restricted_topics_block,
        time_limit_minutes=time_limit_minutes,
        warning_minutes=warning_minutes,
        hard_stop_minutes=hard_stop_minutes,
        absolute_max_minutes=absolute_max_minutes,
        rider_name=rider_name,
        rider_greeting=rider_greeting,
    )

    return prompt


def _build_questions_block(questions: List[Dict[str, Any]]) -> str:
    """Build the formatted questions block for the system prompt."""
    lines = []
    order_map = {}  # question_id -> order number

    # First pass: build order map
    for q in questions:
        order_map[q["id"]] = q.get("order", 0)

    for q in questions:
        order = q.get("order", 0)
        qid = q["id"]
        text = q["text"]
        criteria = q.get("criteria", "open")
        parent_id = q.get("parent_id")

        # Check if this is a branch question
        if parent_id and parent_id in order_map:
            trigger_cats = q.get("parent_category_texts", [])
            trigger_str = ", ".join(trigger_cats) if trigger_cats else "any"
            line = QUESTION_FORMAT_BRANCH.format(
                order=order,
                question_id=qid,
                parent_order=order_map[parent_id],
                trigger_categories=trigger_str,
                question_text=text,
            )
        elif criteria == "scale":
            scale_max = q.get("scales", 5)
            line = QUESTION_FORMAT_SCALE.format(
                order=order,
                question_id=qid,
                question_text=text,
                scale_max=scale_max,
            )
        elif criteria == "categorical":
            categories = q.get("categories", [])
            line = QUESTION_FORMAT_CATEGORICAL.format(
                order=order,
                question_id=qid,
                question_text=text,
                categories=", ".join(categories),
            )
        else:
            line = QUESTION_FORMAT_OPEN.format(
                order=order,
                question_id=qid,
                question_text=text,
            )

        lines.append(line)

    return "\n\n".join(lines)


def build_vapi_tools() -> List[Dict]:
    """Return the VAPI function tool definitions for the agent."""
    from prompts import VAPI_FUNCTION_RECORD_ANSWER, VAPI_FUNCTION_END_SURVEY
    return [VAPI_FUNCTION_RECORD_ANSWER, VAPI_FUNCTION_END_SURVEY]
