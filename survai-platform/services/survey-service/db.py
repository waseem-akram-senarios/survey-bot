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

import httpx
import requests
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text

from shared.models.common import SurveyQuestionAnswerP

logger = logging.getLogger(__name__)

BRAIN_SERVICE_URL = os.getenv("BRAIN_SERVICE_URL", "http://brain-service:8016")


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
    """Determine if a question is relevant. Currently always returns 'Yes'."""
    return "Yes"


def parse_via_brain(question: str, response: str, options: list, criteria: str = "categorical") -> Optional[str]:
    """Parse user response via brain-service."""
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(
                f"{BRAIN_SERVICE_URL}/api/brain/parse",
                json={"question": question, "response": response, "options": options, "criteria": criteria},
            )
            if resp.status_code == 200:
                return resp.json().get("answer")
    except Exception as e:
        logger.warning(f"Brain service parse error: {e}")
    return None


def autofill_via_brain(context: str, question: str, options: list, criteria: str = "categorical") -> Optional[str]:
    """Autofill answer via brain-service."""
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(
                f"{BRAIN_SERVICE_URL}/api/brain/autofill",
                json={"context": context, "question": question, "options": options, "criteria": criteria},
            )
            if resp.status_code == 200:
                return resp.json().get("answer")
    except Exception as e:
        logger.warning(f"Brain service autofill error: {e}")
    return None


def summarize(question: str, response: str) -> str:
    """Summarize long responses via brain-service."""
    if len(response) <= 300:
        return response
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(
                f"{BRAIN_SERVICE_URL}/api/brain/summarize",
                json={"question": question, "response": response},
            )
            if resp.status_code == 200:
                return resp.json().get("summary", response)
    except Exception as e:
        logger.warning(f"Brain service summarize error: {e}")
    return response


def process_question_sync(question_data, biodata: str) -> Optional[SurveyQuestionAnswerP]:
    """Synchronous wrapper for process_question."""
    return asyncio.run(process_question(question_data, biodata))


async def process_question(question, biodata: str) -> Optional[SurveyQuestionAnswerP]:
    """Process a single question with filtering and autofill via brain-service."""
    que_id = question.QueId
    choice = filtering(biodata, question.QueText)

    if choice == "Yes":
        que_criteria = question.QueCriteria
        filled = None

        if que_criteria == "scale":
            scale_max = question.QueScale
            scale_list = [str(i) for i in range(1, int(scale_max) + 1)]
            filled = autofill_via_brain(biodata, question.QueText, scale_list, "scale")

        elif que_criteria == "categorical":
            que_categories = list(question.QueCategories or [])
            if "None of the above" in que_categories:
                que_categories.remove("None of the above")
            filled = autofill_via_brain(biodata, question.QueText, que_categories, "categorical")

        elif que_criteria == "open":
            filled = autofill_via_brain(biodata, question.QueText, [], "open")

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
    """Process a single survey question to parse the answer from RawAns via brain-service."""
    if question.get("Ans"):
        return question

    raw_ans = question.get("RawAns", "") or ""

    if question.get("QueCriteria") == "scale":
        scale_max = question["QueScale"]
        scale_list = [str(i) for i in range(1, int(scale_max) + 1)]
        answer = parse_via_brain(question.get("QueText", ""), raw_ans, scale_list, "scale")
        question["Ans"] = answer if answer else "None of the above"

    elif question.get("QueCriteria") == "categorical":
        que_categories = question.get("QueCategories") or []
        answer = parse_via_brain(question.get("QueText", ""), raw_ans, que_categories, "categorical")
        question["Ans"] = answer if answer else "None of the above"

    else:
        question["Ans"] = summarize(question.get("QueText", ""), raw_ans)

    return question


def build_html_email(url: str, language: str = "en") -> str:
    """Build HTML email body for survey link with bilingual support."""
    if language == "bilingual":
        return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Arial,Helvetica,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;">
    <tr><td align="center" style="padding:40px 20px;">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <tr><td style="background-color:#1958F7;padding:30px 40px;text-align:center;">
          <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:600;">We'd Love Your Feedback</h1>
          <h2 style="margin:8px 0 0;color:#ffffffcc;font-size:18px;font-weight:500;">Nos Encantaría Conocer Su Opinión</h2>
        </td></tr>
        <tr><td style="padding:32px 40px;">
          <p style="margin:0 0 12px;font-size:16px;color:#333333;line-height:1.6;">
            We value your opinion and would appreciate a few minutes of your time to complete a short survey.
          </p>
          <p style="margin:0 0 20px;font-size:16px;color:#666666;line-height:1.6;font-style:italic;">
            Valoramos su opinión y le agradeceríamos unos minutos de su tiempo para completar una breve encuesta.
          </p>
          <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto;">
            <tr><td style="background-color:#1958F7;border-radius:8px;text-align:center;">
              <a href="{url}" style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:16px;font-weight:600;text-decoration:none;">Take the Survey / Realizar la Encuesta</a>
            </td></tr>
          </table>
          <p style="margin:24px 0 0;font-size:14px;color:#666666;line-height:1.5;">
            If the button above doesn't work, copy and paste this link into your browser:
            <br><span style="color:#999;font-style:italic;">Si el botón no funciona, copie y pegue este enlace:</span>
            <br><a href="{url}" style="color:#1958F7;word-break:break-all;">{url}</a>
          </p>
        </td></tr>
        <tr><td style="padding:20px 40px;background-color:#f9f9f9;text-align:center;">
          <p style="margin:0;font-size:12px;color:#999999;">Thank you for your time. / Gracias por su tiempo.</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

    if language == "es":
        heading = "Nos Encantaría Conocer Su Opinión"
        intro = "Valoramos su opinión y le agradeceríamos unos minutos de su tiempo para completar una breve encuesta."
        body2 = "Sus respuestas nos ayudan a mejorar nuestros productos y servicios."
        cta = "Realizar la Encuesta"
        fallback = "Si el botón de arriba no funciona, copie y pegue este enlace en su navegador:"
        footer = "Gracias por su tiempo y sus comentarios."
    else:
        heading = "We'd Love Your Feedback"
        intro = "We value your opinion and would appreciate a few minutes of your time to complete a short survey."
        body2 = "Your responses help us improve our products and services."
        cta = "Take the Survey"
        fallback = "If the button above doesn't work, copy and paste this link into your browser:"
        footer = "Thank you for your time and insights."

    html_lang = "es" if language == "es" else "en"
    return f"""\
<!DOCTYPE html>
<html lang="{html_lang}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Arial,Helvetica,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;">
    <tr><td align="center" style="padding:40px 20px;">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <tr><td style="background-color:#1958F7;padding:30px 40px;text-align:center;">
          <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:600;">{heading}</h1>
        </td></tr>
        <tr><td style="padding:32px 40px;">
          <p style="margin:0 0 16px;font-size:16px;color:#333333;line-height:1.6;">
            {intro}
          </p>
          <p style="margin:0 0 24px;font-size:16px;color:#333333;line-height:1.6;">
            {body2}
          </p>
          <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto;">
            <tr><td style="background-color:#1958F7;border-radius:8px;text-align:center;">
              <a href="{url}" style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:16px;font-weight:600;text-decoration:none;">{cta}</a>
            </td></tr>
          </table>
          <p style="margin:24px 0 0;font-size:14px;color:#666666;line-height:1.5;">
            {fallback}
            <br><a href="{url}" style="color:#1958F7;word-break:break-all;">{url}</a>
          </p>
        </td></tr>
        <tr><td style="padding:20px 40px;background-color:#f9f9f9;text-align:center;">
          <p style="margin:0;font-size:12px;color:#999999;">{footer}</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def build_text_email(url: str, language: str = "en") -> str:
    """Build plain text email body for survey link with bilingual support."""
    if language == "bilingual":
        return (
            "We'd Love Your Feedback / Nos Encantaría Conocer Su Opinión\n\n"
            "We value your opinion and would appreciate a few minutes of your time "
            "to complete a short survey.\n"
            "Valoramos su opinión y le agradeceríamos unos minutos de su "
            "tiempo para completar una breve encuesta.\n\n"
            f"Take the survey / Realizar la encuesta: {url}\n\n"
            "Thank you / Gracias"
        )
    if language == "es":
        return (
            "Nos Encantaría Conocer Su Opinión\n\n"
            "Valoramos su opinión y le agradeceríamos unos minutos de su "
            "tiempo para completar una breve encuesta.\n\n"
            "Sus respuestas nos ayudan a mejorar nuestros productos y servicios.\n\n"
            f"Realizar la encuesta: {url}\n\n"
            "Gracias por su tiempo y sus comentarios."
        )
    return (
        "We'd Love Your Feedback\n\n"
        "We value your opinion and would appreciate a few minutes of your time "
        "to complete a short survey.\n\n"
        "Your responses help us improve our products and services.\n\n"
        f"Take the survey: {url}\n\n"
        "Thank you for your time and insights!"
    )


