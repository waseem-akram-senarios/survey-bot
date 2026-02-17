"""
Agent Service API routes.
Handles call initiation, VAPI callbacks, transcript retrieval, and email fallback.
"""

import json
import logging
import os
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

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
from workflow import VAPISurveyWorkflowGenerator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/make-call")
async def make_call(
    survey_id: str,
    phone: str,
    provider: str = "vapi",
    background_tasks: BackgroundTasks = None,
):
    """
    Initiate an AI-powered survey call.

    1. Load survey + questions
    2. Build multi-node VAPI workflow (proven working format)
    3. Create workflow in VAPI
    4. Make the outbound call
    """
    api_key = os.getenv("VAPI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="VAPI_API_KEY not configured")

    phone_number_id = os.getenv("PHONE_NUMBER_ID")
    if not phone_number_id:
        raise HTTPException(status_code=500, detail="PHONE_NUMBER_ID not configured")

    survey = get_survey_with_questions(survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")

    questions = survey.get("questions", [])
    if not questions:
        raise HTTPException(status_code=400, detail="Survey has no questions")

    if provider != "vapi":
        raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported. Use 'vapi'.")

    # Build survey_data in the format the workflow generator expects
    survey_data = {
        "SurveyId": survey_id,
        "Questions": questions,
    }

    # Determine the callback URL for the API request tool node
    submit_url = os.getenv(
        "SURVEY_SUBMIT_URL",
        f"http://survey-service:8010/api/answers/qna_phone",
    )

    # Load template config for time limits, restricted topics, greeting
    template_name = survey.get("template_name", "")
    template_config = get_template_config(template_name) if template_name else {}

    # Load rider data for smarter conversations
    rider_name = survey.get("rider_name") or survey.get("recipient") or ""
    rider_phone = survey.get("phone") or phone
    rider_data = get_rider_data(rider_name=rider_name, phone=rider_phone)

    # Detect language from template name (e.g. "Demo_Spanish" or templates with _es suffix)
    language = "en"
    if template_name:
        tname_lower = template_name.lower()
        if "spanish" in tname_lower or "_es" in tname_lower or "español" in tname_lower:
            language = "es"

    generator = VAPISurveyWorkflowGenerator(api_key)

    # Generate and create workflow with full context
    try:
        workflow_config = generator.generate_workflow_from_survey(
            survey_data,
            callback_url=submit_url,
            template_config=template_config,
            rider_data=rider_data,
            language=language,
        )
        workflow_id = generator.create_workflow(workflow_config)
        if not workflow_id:
            raise RuntimeError("Workflow creation returned no ID")
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow creation failed: {str(e)}")

    # Prepare workflow variables
    workflow_variables = {
        "SurveyId": survey_id,
        "Recipient": survey.get("recipient") or survey.get("rider_name") or "Customer",
        "Name": survey.get("name") or "Survey",
        "RideID": survey.get("ride_id") or "N/A",
    }

    # Save workflow_id to the survey
    try:
        sql_execute(
            "UPDATE surveys SET workflow_id = :workflow_id WHERE id = :sid",
            {"workflow_id": workflow_id, "sid": survey_id},
        )
        logger.info(f"Workflow ID saved: {workflow_id}")
    except Exception as e:
        logger.warning(f"Failed to save workflow_id: {e}")

    # Make the call
    try:
        call_result = generator.make_call(
            workflow_id=workflow_id,
            phone_number_id=phone_number_id,
            customer_phone=phone,
            workflow_variables=workflow_variables,
        )
        call_id = call_result.get("id", "")

        # Update survey with call_id
        if call_id:
            try:
                sql_execute(
                    "UPDATE surveys SET call_id = :call_id WHERE id = :sid",
                    {"call_id": call_id, "sid": survey_id},
                )
                logger.info(f"Call ID saved: {call_id}")
            except Exception as e:
                logger.warning(f"Failed to save call_id: {e}")

        return {
            "status": "call_initiated",
            "call_id": call_id,
            "workflow_id": workflow_id,
            "survey_id": survey_id,
            "provider": "vapi",
        }
    except Exception as e:
        logger.error(f"Failed to make call: {e}")
        raise HTTPException(status_code=500, detail=f"Call failed: {str(e)}")


@router.post("/make-workflow")
async def make_workflow(
    survey_id: str,
    company_name: str = "the transit agency",
):
    """Generate and return the workflow config (for debugging/preview)."""
    api_key = os.getenv("VAPI_API_KEY", "")
    survey = get_survey_with_questions(survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")

    questions = survey.get("questions", [])
    survey_data = {
        "SurveyId": survey_id,
        "Questions": questions,
    }

    submit_url = os.getenv(
        "SURVEY_SUBMIT_URL",
        f"http://survey-service:8010/api/answers/qna_phone",
    )

    template_name = survey.get("template_name", "")
    template_config = get_template_config(template_name) if template_name else {}
    rider_data = get_rider_data(rider_name=survey.get("rider_name"), phone=survey.get("phone"))
    language = "es" if template_name and ("spanish" in template_name.lower() or "_es" in template_name.lower()) else "en"

    generator = VAPISurveyWorkflowGenerator(api_key)
    workflow_config = generator.generate_workflow_from_survey(
        survey_data, callback_url=submit_url,
        template_config=template_config, rider_data=rider_data, language=language,
    )

    return {"workflow": workflow_config}


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


@router.post("/tool-callback")
async def tool_callback(request: Request):
    """
    Handle VAPI function tool callbacks.
    VAPI calls this when the agent uses record_answer or end_survey tools.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    message = body.get("message", {})
    tool_calls = message.get("toolCalls", [])

    metadata = message.get("metadata", {})
    if not metadata:
        metadata = body.get("metadata", {})
    survey_id = metadata.get("survey_id", "")

    results = []
    for tc in tool_calls:
        func_name = tc.get("function", {}).get("name", "")
        args_str = tc.get("function", {}).get("arguments", "{}")

        try:
            args = json.loads(args_str) if isinstance(args_str, str) else args_str
        except json.JSONDecodeError:
            args = {}

        if func_name == "record_answer":
            question_id = args.get("question_id", "")
            raw_answer = args.get("raw_answer", "")
            success = record_answer(survey_id, question_id, raw_answer)
            results.append({
                "toolCallId": tc.get("id"),
                "result": "Answer recorded." if success else "Failed to record answer.",
            })

        elif func_name == "end_survey":
            summary = args.get("summary", "")
            status = args.get("status", "completed")

            if status in ("completed", "partial"):
                update_survey_status(survey_id, "Completed" if status == "completed" else "In-Progress")

            store_transcript(
                survey_id=survey_id,
                full_transcript=summary,
                call_status=status,
            )

            results.append({
                "toolCallId": tc.get("id"),
                "result": f"Survey ended with status: {status}",
            })

        else:
            results.append({
                "toolCallId": tc.get("id"),
                "result": f"Unknown function: {func_name}",
            })

    return {"results": results}


@router.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    """
    Handle VAPI end-of-call webhooks.
    Stores the full transcript and updates survey status.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event_type = body.get("message", {}).get("type", "")

    if event_type == "end-of-call-report":
        msg = body.get("message", {})
        call_data = msg.get("call", {})
        survey_id = call_data.get("metadata", {}).get("survey_id", "")
        call_id = call_data.get("id", "")

        transcript_parts = msg.get("transcript", [])
        if isinstance(transcript_parts, list):
            full_transcript = "\n".join(
                f"{t.get('role', 'unknown')}: {t.get('content', '')}"
                for t in transcript_parts
            )
        elif isinstance(transcript_parts, str):
            full_transcript = transcript_parts
        else:
            full_transcript = str(transcript_parts)

        duration = msg.get("durationSeconds", 0)

        if survey_id:
            store_transcript(
                survey_id=survey_id,
                full_transcript=full_transcript,
                call_duration_seconds=int(duration),
                call_status=msg.get("endedReason", "completed"),
                call_id=call_id,
            )
            logger.info(f"Stored end-of-call transcript for survey {survey_id}")

    return {"status": "ok"}


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
