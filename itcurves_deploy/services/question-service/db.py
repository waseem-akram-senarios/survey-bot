import sys

sys.path.insert(0, "/app")  # so shared package at /app/shared can be found

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from openai import OpenAI
from sqlalchemy import create_engine, text

SYMPATHIZE_PROMPT = """You are a helpful customer representative for a company that conducts interview. Given a question and a user's response, try to respond with a short phrase that matches the user's response. If the user's response is positive, appreciate the positive feedback. If the user's response is negative, respond with an apologetic tone. If the user's response is neutral, acknowledge the response without any strong emotion. Do not attempt to remediate the user's response, just acknowledge it. You must not try to repeat the response of the user or phrases from it."""

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER', 'pguser')}:{os.getenv('DB_PASSWORD', 'root')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/db"
)


def sql_execute(
    query: str,
    params: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
) -> List[Dict[str, Any]]:
    """
    Execute a SQL query and return results.
    For SELECT: returns list of dicts.
    For INSERT/UPDATE/DELETE: commits and returns empty list.
    """
    params = params if params is not None else {}
    with engine.begin() as conn:
        result = conn.execute(text(query), params)
        if result.returns_rows:
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result]
        return []


def get_current_time() -> str:
    return datetime.now(timezone.utc).isoformat()


def sympathize(question: str, response: str) -> str:
    """Generate empathetic response using OpenAI gpt-4.1-mini."""
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYMPATHIZE_PROMPT},
            {"role": "user", "content": f"Question: {question}\nResponse: {response}"},
        ],
    )
    return completion.choices[0].message.content


def process_question_stats(data: Dict[str, Any]) -> Dict[str, int]:
    """
    Process question stats based on criteria.
    Takes dict with: criteria, categories (list), scales (int), answers (list).
    Returns category_counts for categorical, scale_counts for scale.
    """
    criteria = data.get("criteria")
    categories = data.get("categories", [])
    scales = data.get("scales", 0)
    answers = data.get("answers", [])

    if criteria == "categorical":
        category_counts = {cat: 0 for cat in categories}
        for ans in answers:
            if ans in category_counts:
                category_counts[ans] += 1
        return category_counts

    if criteria == "scale":
        try:
            scale_max = int(scales)
        except (ValueError, TypeError):
            return {}
        scale_counts = {str(i): 0 for i in range(1, scale_max + 1)}
        for ans in answers:
            try:
                if 1 <= int(ans) <= scale_max:
                    scale_counts[str(ans)] += 1
            except (ValueError, TypeError):
                continue
        return scale_counts

    return {}
