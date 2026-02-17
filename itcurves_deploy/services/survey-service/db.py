"""
Database operations for the Survey Service.
"""

import sys
sys.path.insert(0, "/app")

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Literal, Optional, Union

import requests
from fastapi import HTTPException
from openai import OpenAI
from pydantic import BaseModel
from sqlalchemy import create_engine, text

from shared.models.common import SurveyQuestionAnswerP

logger = logging.getLogger(__name__)

# Prompts
filtering_prompt = "You are a helpful survey assistant. Given a user's biodata and other information, determine whether the given survey question is relevant or not. Simply return 'Yes' if it is or 'No' if it isn't without any additional text."

autofill_prompt = "You are a helpful survey assistant. Given a question, context, and a list of response options, determine whether the question can be answered based strictly on the provided context. If the context provides clear information about the subject of the question, choose the most appropriate response from the options. If the context does not provide enough information to answer the question about the specific subject mentioned, return an empty string. Do not make assumptions or infer information that is not explicitly stated. Your response should include only the answer selected from the list, or an empty string if the answer cannot be determined."

autofill_prompt_open = "You are a helpful survey assistant. Given a question and a context, extract the answer to the question based strictly on the provided context. If the context does not provide enough information to answer the question about the specific subject mentioned, return the string 'Cannot be determined'. Do not make assumptions or infer information that is not explicitly stated."

parse_prompt = "You are a helpful survey assistant. Given a question asked to a user and his response, provide the answer as a value given a list of possible options. Do not make up information or assume anything. Your response must be based on the response of the user."


def get_engine():
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "pguser")
    db_password = os.getenv("DB_PASSWORD", "root")
    url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/db"
    return create_engine(url, pool_size=5, max_overflow=10, pool_pre_ping=True)


_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


def sql_execute(query: str, params: Union[dict, list, None] = None):
    """Execute SQL query. Returns list of dicts for SELECT, rowcount for mutations.
    For batch operations, params can be a list of dicts."""
    engine = _get_engine()
    with engine.begin() as conn:
        if isinstance(params, list) and params:
            for p in params:
                conn.execute(text(query), p)
            return len(params)
        result = conn.execute(text(query), params or {})
    if result.returns_rows:
        return result.mappings().all()
    return result.rowcount


def get_current_time() -> str:
    """Returns current UTC time as ISO format."""
    return datetime.now(timezone.utc).isoformat()


def filtering(biodata: str, question: str) -> str:
    """Hardcoded to return 'Yes' as the current monolith does."""
    return "Yes"


def parse(question: str, response: str, response_format: type):
    """Parse user response into structured format using gpt-4.1 with parse_prompt."""
    openai_client = OpenAI()
    resp = openai_client.beta.chat.completions.parse(
        model="gpt-4.1",
        messages=[
            {"role": "developer", "content": parse_prompt},
            {
                "role": "user",
                "content": f"Survey Question: {question}\nuser's Response: {response}",
            },
        ],
        response_format=response_format,
    )
    return resp.choices[0].message.parsed


def autofill(context: str, question: str, response_format: type):
    """Autofill answer from context using gpt-4.1 with autofill_prompt."""
    openai_client = OpenAI()
    resp = openai_client.beta.chat.completions.parse(
        model="gpt-4.1",
        messages=[
            {"role": "developer", "content": autofill_prompt},
            {
                "role": "user",
                "content": f"Context of the survey: {context}\nSurvey Question: {question}",
            },
        ],
        response_format=response_format,
    )
    return resp.choices[0].message.parsed


def autofill_open(context: str, question: str) -> Optional[str]:
    """Autofill open-ended question from context."""
    openai_client = OpenAI()
    resp = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "developer", "content": autofill_prompt_open},
            {
                "role": "user",
                "content": f"Context of the survey: {context}\nSurvey Question: {question}",
            },
        ],
    )
    content = resp.choices[0].message.content
    if content == "Cannot be determined":
        return None
    return content


def summarize(question: str, response: str) -> str:
    """Summarize long responses (>300 chars) using gpt-4.1."""
    if len(response) <= 300:
        return response
    openai_client = OpenAI()
    resp = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "developer",
                "content": "You are a helpful assistant that summarizes the response of a survey question. Please summarize the response in one or two short sentences without any additional context or text.",
            },
            {
                "role": "user",
                "content": f"Survey Question: {question}\nuser's Response: {response}",
            },
        ],
    )
    return resp.choices[0].message.content


def process_question_sync(question_data, biodata: str) -> Optional[SurveyQuestionAnswerP]:
    """Synchronous wrapper for process_question."""
    return asyncio.run(process_question(question_data, biodata))


async def process_question(question, biodata: str) -> Optional[SurveyQuestionAnswerP]:
    """Process a single question with filtering and autofill."""
    que_id = question.QueId
    choice = filtering(biodata, question.QueText)

    if choice == "Yes":
        que_criteria = question.QueCriteria
        filled = None

        if que_criteria == "scale":
            scale_max = question.QueScale
            scale_list = list(range(1, int(scale_max) + 1))
            scale_list = list(map(str, scale_list))

            class AutoFill(BaseModel):
                can_be_answered_definitely: Literal["Yes", "No"]
                definite_answer: Optional[Literal[tuple(scale_list)]] = None

            result = autofill(biodata, question.QueText, AutoFill)
            filled = result.definite_answer if result else None

        elif que_criteria == "categorical":
            que_categories = list(question.QueCategories or [])
            if "None of the above" in que_categories:
                que_categories.remove("None of the above")

            class AutoFill(BaseModel):
                can_be_answered_definitely: Literal["Yes", "No"]
                definite_answer: Optional[Literal[tuple(que_categories)]] = None

            result = autofill(biodata, question.QueText, AutoFill)
            filled = result.definite_answer if result else None

        elif que_criteria == "open":
            filled = autofill_open(biodata, question.QueText)

        return SurveyQuestionAnswerP(
            QueId=que_id,
            QueText=question.QueText,
            QueScale=question.QueScale,
            QueCriteria=question.QueCriteria,
            QueCategories=question.QueCategories,
            Order=str(question.Order),
            Ans=filled or None,
            RawAns=None,
            Autofill=question.Autofill,
        )
    return None


def process_survey_question(question: dict) -> dict:
    """Process a single survey question to parse the answer from RawAns."""
    if question.get("Ans"):
        return question

    if question.get("QueCriteria") == "scale":
        scale_max = question["QueScale"]
        scale_list = list(range(1, int(scale_max) + 1))
        scale_list = list(map(str, scale_list))

        class Fill(BaseModel):
            answer: Optional[Literal[tuple(scale_list)]] = None
    elif question.get("QueCriteria") == "categorical":
        que_categories = question.get("QueCategories") or []

        class Fill(BaseModel):
            answer: Optional[Literal[tuple(que_categories)]] = None
    else:
        question["Ans"] = summarize(
            question.get("QueText", ""), question.get("RawAns", "") or ""
        )
        return question

    try:
        parsed = parse(
            question.get("QueText", ""),
            question.get("RawAns", "") or "",
            Fill,
        )
        question["Ans"] = parsed.answer if parsed and parsed.answer else "None of the above"
    except Exception as e:
        logger.warning(
            f"Error parsing answer for question {question.get('QueId')}: {str(e)}"
        )
        question["Ans"] = "None of the above"
    return question


def build_html_email(url: str) -> str:
    """Build HTML email body for survey link."""
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #4CAF50;">We'd love your input!</h2>
            <p>We value your feedback and would appreciate it if you could take a few moments to answer a survey:</p>
            <p>Click the link below to complete the survey:</p>
            <p><a href="{url}">Survey Link</a></p>
            <p>Thank you for your time and insights!</p>
        </body>
    </html>
    """


def build_text_email(url: str) -> str:
    """Build plain text email body for survey link."""
    return (
        "We'd love your input!\n\n"
        "We value your feedback and would appreciate it if you could take a few moments to answer a survey:\n\n"
        f"Click the link below to complete the survey:\n\n{url}\n\n"
        "Thank you for your time and insights!"
    )


def make_call_task(headers: dict, payload: dict, survey_id: str) -> dict:
    """Make VAPI call and update survey with call_id."""
    try:
        url = "https://api.vapi.ai/call"
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            call_id = response.json().get("id")
            try:
                sql_execute(
                    """UPDATE surveys SET call_id = :call_id, call_time = NOW() AT TIME ZONE 'UTC', call_number = :call_number WHERE id = :survey_id""",
                    {
                        "survey_id": survey_id,
                        "call_id": call_id,
                        "call_number": payload.get("customer", {}).get("number", ""),
                    },
                )
                logger.info(f"Call ID updated successfully: {call_id}")
            except Exception as e:
                logger.warning(f"Error updating surveys: {e}")

            return {"CallId": call_id}
        else:
            logger.error(f"Failed to create outbound call: {response.text}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create outbound call: {response.text}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create outbound call: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create outbound call: {str(e)}"
        )
