"""
Voice Service API routes.

Handles LiveKit call lifecycle:
- Initiate calls via LiveKit SIP
- Transcript retrieval
- Email fallback
"""

import logging
import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request

from db import (
    get_rider_data,
    get_survey_with_questions,
    get_template_config,
    get_transcript,
    record_answer,
    sql_execute,
    store_transcript,
    update_survey_status,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["voice"])

BRAIN_SERVICE_URL = os.getenv("BRAIN_SERVICE_URL", "http://brain-service:8016")


@router.post("/make-call")
async def make_call(
    survey_id: str,
    phone: str,
    provider: str = "livekit",
):
    """Initiate an AI-powered survey call via LiveKit SIP."""
    survey = get_survey_with_questions(survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")

    questions = survey.get("questions", [])
    if not questions:
        raise HTTPException(status_code=400, detail="Survey has no questions")

    livekit_url = os.getenv("LIVEKIT_URL", "")
    if not livekit_url:
        raise HTTPException(status_code=500, detail="LIVEKIT_URL not configured")

    template_name = survey.get("template_name", "")
    template_config = get_template_config(template_name) if template_name else {}
    rider_name = survey.get("rider_name") or survey.get("recipient") or ""
    rider_phone = survey.get("phone") or phone

    language = "en"
    if template_name:
        tname_lower = template_name.lower()
        if "spanish" in tname_lower or "_es" in tname_lower:
            language = "es"

    company_name = template_config.get("company_name") or os.getenv("ORGANIZATION_NAME", "IT Curves")
    callback_url = os.getenv("SURVEY_SUBMIT_URL", "http://survey-service:8020/api/answers/qna_phone")

    survey_context = {
        "recipient_name": rider_name or "Customer",
        "template_name": template_name,
        "organization_name": company_name,
        "language": language,
        "questions": questions,
        "callback_url": callback_url,
    }

    try:
        rider_data = get_rider_data(rider_name=rider_name, phone=rider_phone)
        if not rider_data:
            rider_data = {}
        if not rider_data.get("name") and rider_name:
            rider_data["name"] = rider_name
        if not rider_data.get("phone") and rider_phone:
            rider_data["phone"] = rider_phone
        survey_biodata = survey.get("biodata", "")
        if survey_biodata and not rider_data.get("biodata"):
            rider_data["biodata"] = survey_biodata

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{BRAIN_SERVICE_URL}/api/brain/build-system-prompt",
                json={
                    "survey_name": template_name or f"Survey {survey_id}",
                    "questions": questions,
                    "rider_data": rider_data,
                    "company_name": company_name,
                },
            )
            if resp.status_code == 200:
                survey_context["system_prompt"] = resp.json().get("system_prompt", "")
                logger.info(f"Built brain-service prompt for LiveKit call ({len(survey_context['system_prompt'])} chars)")
            else:
                logger.warning(f"Brain-service prompt failed ({resp.status_code}), agent will use defaults")
    except Exception as e:
        logger.warning(f"Brain-service unreachable for LiveKit prompt: {e}, agent will use defaults")

    try:
        from livekit_dispatcher import dispatch_livekit_call
        result = await dispatch_livekit_call(
            phone_number=phone,
            survey_id=survey_id,
            survey_context=survey_context,
        )

        call_id = result.get("call_id", "")
        if call_id:
            try:
                sql_execute(
                    "UPDATE surveys SET call_id = :call_id WHERE id = :sid",
                    {"call_id": call_id, "sid": survey_id},
                )
            except Exception as e:
                logger.warning(f"Failed to save LiveKit call_id: {e}")

        return {
            "status": "call_initiated",
            "call_id": call_id,
            "survey_id": survey_id,
            "provider": "livekit",
        }
    except Exception as e:
        logger.error(f"LiveKit call failed: {e}")
        raise HTTPException(status_code=500, detail=f"LiveKit call failed: {str(e)}")


@router.get("/transcript/{survey_id}")
async def get_survey_transcript(survey_id: str):
    """Get the stored transcript for a survey."""
    transcript = get_transcript(survey_id)
    if not transcript:
        raise HTTPException(
            status_code=404,
            detail=f"No transcript found for survey {survey_id}",
        )
    return transcript


@router.post("/send-email-fallback")
async def send_email_fallback(
    survey_id: str,
    email: str,
    survey_url: str,
):
    """Send an email survey link as fallback when call fails or is declined."""
    try:
        from mailersend import emails

        api_key = os.getenv("MAILERSEND_API_KEY", "")
        sender_email = os.getenv("MAILERSEND_SENDER_EMAIL", "")

        if not api_key or api_key.startswith("<"):
            logger.warning("MailerSend not configured, skipping email")
            return {
                "status": "skipped",
                "reason": "MailerSend not configured",
                "survey_url": survey_url,
            }

        mailer = emails.NewEmail(api_key)
        mail_body = {}

        mail_from = {"name": "Survey Team", "email": sender_email}
        recipients = [{"name": "Rider", "email": email}]

        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        mailer.set_subject("We'd love your feedback!", mail_body)
        mailer.set_html_content(
            f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #4CAF50;">We'd love your input!</h2>
                <p>We value your feedback and would appreciate it if you could take a few moments to complete a brief survey.</p>
                <p><a href="{survey_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Take the Survey</a></p>
                <p>Thank you for your time!</p>
            </body>
            </html>
            """,
            mail_body,
        )

        mailer.send(mail_body)
        logger.info(f"Email fallback sent for survey {survey_id} to {email}")

        return {"status": "sent", "email": email, "survey_id": survey_id}

    except Exception as e:
        logger.error(f"Email fallback failed: {e}")
        return {"status": "failed", "error": str(e), "survey_url": survey_url}


# ─── Backward Compatibility Aliases ──────────────────────────────────────────

agent_router = APIRouter(prefix="/api/agent", tags=["agent-compat"])


@agent_router.post("/make-call")
async def agent_make_call(survey_id: str, phone: str, provider: str = "livekit"):
    return await make_call(survey_id=survey_id, phone=phone, provider=provider)


@agent_router.get("/transcript/{survey_id}")
async def agent_get_transcript(survey_id: str):
    return await get_survey_transcript(survey_id)


@agent_router.post("/send-email-fallback")
async def agent_send_email(survey_id: str, email: str, survey_url: str):
    return await send_email_fallback(survey_id=survey_id, email=email, survey_url=survey_url)
