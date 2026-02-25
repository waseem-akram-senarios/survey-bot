"""
Agent Service API routes.
Handles transcript retrieval and email fallback.
"""

import logging
import os

from fastapi import APIRouter, HTTPException

from db import (
    get_transcript,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agent", tags=["agent"])


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
