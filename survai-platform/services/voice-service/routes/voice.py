"""
Voice Service API routes.

Handles LiveKit call lifecycle:
- Initiate calls via LiveKit SIP
- Transcript retrieval
- Email fallback
"""

import asyncio
import logging
import os
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import APIRouter, HTTPException

from db import (
    async_execute,
    get_survey_with_questions,
    get_template_config,
    get_transcript,
    store_transcript,
    record_answer as db_record_answer,
    update_survey_status,
)
from prompt_builder import build_greeter_prompt, build_questions_prompt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/voice", tags=["voice"])

_active_calls: dict[str, dict[str, float | str]] = {}
_active_surveys: dict[str, str] = {}
_active_calls_lock = asyncio.Lock()
ACTIVE_CALL_STALE_SECONDS = 4 * 60
ACTIVE_CALL_HARD_LIMIT = 10 * 60
LOCK_WATCHDOG_SECONDS = 75  # auto-release if agent never confirms the call connected


def _normalize_phone(phone: str) -> str:
    """Normalize a phone number for lock comparisons."""
    return (phone or "").strip().replace(" ", "")


def _lock_age(meta: dict) -> float:
    return time.monotonic() - float(meta.get("started_at", 0))


async def _is_lock_still_valid(survey_id: str, phone: str, age_seconds: float) -> bool:
    """Check if a call lock still represents a genuinely active call."""
    if age_seconds > ACTIVE_CALL_HARD_LIMIT:
        return False

    rows = await async_execute(
        "SELECT phone, status, end_reason FROM surveys WHERE id = :survey_id",
        {"survey_id": survey_id},
    )
    if not rows:
        return False

    row = rows[0]
    db_phone = _normalize_phone(str(row.get("phone") or ""))
    status = str(row.get("status") or "")
    end_reason = str(row.get("end_reason") or "")

    if status == "Completed" or end_reason:
        return False
    if not db_phone:
        return False
    if db_phone != _normalize_phone(phone):
        return False
    if age_seconds > ACTIVE_CALL_STALE_SECONDS:
        return False
    return True


async def _lock_watchdog(phone: str, survey_id: str) -> None:
    """Background task: release the lock if the call was never answered."""
    await asyncio.sleep(LOCK_WATCHDOG_SECONDS)
    async with _active_calls_lock:
        meta = _active_calls.get(phone)
        if not meta:
            return
        if str(meta.get("survey_id", "")) != survey_id:
            return
        if meta.get("confirmed"):
            return
        logger.info(
            f"Watchdog: releasing unconfirmed lock for {phone} "
            f"(survey {survey_id}, age={_lock_age(meta):.0f}s)"
        )
        del _active_calls[phone]
        _active_surveys.pop(survey_id, None)


async def _reserve_call(phone: str, survey_id: str) -> None:
    """Reserve a phone number while a live call is active."""
    async with _active_calls_lock:
        now = time.monotonic()

        expired = [
            number for number, meta in _active_calls.items()
            if now - float(meta.get("started_at", 0)) > ACTIVE_CALL_HARD_LIMIT
        ]
        for number in expired:
            sid = str(_active_calls[number].get("survey_id", ""))
            logger.info(f"Auto-releasing expired lock: {number} (survey {sid})")
            _active_surveys.pop(sid, None)
            del _active_calls[number]

        existing = _active_calls.get(phone)
        if existing:
            active_survey_id = str(existing.get("survey_id", ""))
            age = _lock_age(existing)

            if not await _is_lock_still_valid(active_survey_id, phone, age):
                logger.info(
                    f"Auto-releasing stale lock for {phone}: survey {active_survey_id}, "
                    f"age={age:.0f}s"
                )
                del _active_calls[phone]
                _active_surveys.pop(active_survey_id, None)
                existing = None

        if existing:
            active_survey_id = str(existing.get("survey_id", ""))
            age = _lock_age(existing)
            raise HTTPException(
                status_code=429,
                detail=(
                    f"A call to {phone} is already in progress "
                    f"(survey {active_survey_id}, started {age:.0f}s ago). "
                    f"It will auto-expire after {ACTIVE_CALL_STALE_SECONDS}s."
                ),
            )

        _active_calls[phone] = {"survey_id": survey_id, "started_at": now}
        _active_surveys[survey_id] = phone

    asyncio.create_task(_lock_watchdog(phone, survey_id))


async def _confirm_call(phone: str, survey_id: str) -> None:
    """Mark a lock as confirmed (call was answered), so the watchdog won't release it."""
    async with _active_calls_lock:
        meta = _active_calls.get(phone)
        if meta and str(meta.get("survey_id", "")) == survey_id:
            meta["confirmed"] = True


async def _release_call(*, survey_id: str | None = None, phone: str | None = None) -> None:
    """Release an active call reservation after the call finishes or fails."""
    async with _active_calls_lock:
        resolved_phone = phone
        if survey_id:
            resolved_phone = resolved_phone or _active_surveys.pop(survey_id, None)
        if resolved_phone:
            meta = _active_calls.get(resolved_phone)
            if meta:
                meta_survey_id = str(meta.get("survey_id", ""))
                if not survey_id or meta_survey_id == survey_id:
                    del _active_calls[resolved_phone]
                    if meta_survey_id:
                        _active_surveys.pop(meta_survey_id, None)
                    logger.info(f"Released call lock: {resolved_phone} (survey {meta_survey_id})")


def _extract_rider_first_name(rider_name: str) -> str:
    """Return the first word of a name, stripped and validated."""
    if not rider_name:
        return ""
    first = rider_name.strip().split()[0]
    _placeholders = {"customer", "unknown", "user", "recipient", "test", "n/a", "na", "none", "name"}
    if first.lower() in _placeholders or len(first.replace("-", "").replace("'", "")) < 2:
        return ""
    return first


def _with_language_query(url: str, language: str) -> str:
    """Force a survey URL into a specific language when requested."""
    if language not in {"en", "es"} or not url:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["lang"] = language
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


@router.post("/make-call")
async def make_call(
    survey_id: str,
    phone: str,
    provider: str = "livekit",
    greetings: str = "",
    language: str = "bilingual",
):
    """Initiate an AI-powered survey call via LiveKit SIP."""
    normalized_phone = phone.strip().replace(" ", "")
    survey = await get_survey_with_questions(survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")

    questions = survey.get("questions", [])
    if not questions:
        raise HTTPException(status_code=400, detail="Survey has no questions")

    livekit_url = os.getenv("LIVEKIT_URL", "")
    if not livekit_url:
        raise HTTPException(status_code=500, detail="LIVEKIT_URL not configured")

    template_name = survey.get("template_name", "")
    rider_name = survey.get("rider_name") or survey.get("recipient") or ""

    if template_name:
        template_config = await get_template_config(template_name)
    else:
        template_config = {}

    if language not in ("en", "es", "bilingual"):
        language = "bilingual"

    company_name = template_config.get("company_name") or os.getenv("ORGANIZATION_NAME", "IT Curves")
    callback_url = os.getenv("SURVEY_SUBMIT_URL", "http://survey-service:8020/api/answers/qna_phone")

    rider_first_name = _extract_rider_first_name(rider_name)
    public_url = os.getenv("NEXT_PUBLIC_API_BASE_URL", os.getenv("PUBLIC_URL", ""))
    survey_url = f"{public_url}/survey/{survey_id}" if public_url else ""
    rider_email = survey.get("email", "")

    try:
        await async_execute(
            "UPDATE surveys SET phone = :phone WHERE id = :sid",
            {"phone": normalized_phone, "sid": survey_id},
        )
    except Exception as e:
        logger.warning(f"Failed to persist phone {normalized_phone} on survey {survey_id}: {e}")

    await _reserve_call(normalized_phone, survey_id)

    survey_context = {
        "recipient_name": rider_name or "",
        "template_name": template_name,
        "organization_name": company_name,
        "language": language,
        "questions": questions,
        "callback_url": callback_url,
        "survey_url": survey_url,
        "rider_email": rider_email,
        "time_limit_minutes": template_config.get("time_limit_minutes", 30),
    }

    try:
        # For prompt building: bilingual uses the bilingual greeter,
        # en/es use their respective fixed-language prompts
        prompt_language = language  # "en", "es", or "bilingual"
        greeter_prompt = build_greeter_prompt(
            organization_name=company_name,
            rider_first_name=rider_first_name,
            language=prompt_language,
        )

        # For questions prompt: bilingual and en both default to English questions
        questions_lang = "es" if language == "es" else "en"
        questions_prompt, translated_questions_map = await build_questions_prompt(
            organization_name=company_name,
            rider_first_name=rider_first_name,
            survey_name=template_name or f"Survey {survey_id}",
            questions=questions,
            language=questions_lang,
        )
        survey_context["greeter_prompt"] = greeter_prompt
        survey_context["questions_prompt"] = questions_prompt
        survey_context["translated_questions"] = translated_questions_map
        survey_context["system_prompt"] = greeter_prompt  # backward compat
        # For bilingual calls, also build Spanish prompts so user can switch
        if language == "bilingual":
            questions_prompt_es, questions_es_map = await build_questions_prompt(
                organization_name=company_name,
                rider_first_name=rider_first_name,
                survey_name=template_name or f"Survey {survey_id}",
                questions=questions,
                language="es",
            )
            survey_context["questions_prompt_es"] = questions_prompt_es
            survey_context["questions_es_map"] = questions_es_map
        logger.info(
            f"Built prompts for LiveKit call — greeter: {len(greeter_prompt)} chars, "
            f"questions: {len(questions_prompt)} chars"
        )
    except Exception as e:
        logger.warning(f"Local prompt build failed: {e}, agent will use defaults")

    try:
        from livekit_dispatcher import dispatch_livekit_call
        result = await dispatch_livekit_call(
            phone_number=phone,
            survey_id=survey_id,
            survey_context=survey_context,
            greetings=greetings,
        )

        call_id = result.get("call_id", "")
        if call_id:
            try:
                await async_execute(
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
        await _release_call(survey_id=survey_id, phone=normalized_phone)
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


@router.post("/store-transcript")
async def api_store_transcript(
    survey_id: str,
    full_transcript: str,
    call_duration_seconds: int = 0,
    call_status: str = "completed",
    audio_url: str = "",
):
    """Store a call transcript (and optional audio URL) after the voice call ends."""
    try:
        tid = store_transcript(
            survey_id=survey_id,
            full_transcript=full_transcript,
            call_duration_seconds=call_duration_seconds,
            call_status=call_status,
            audio_url=audio_url or None,
        )
        return {"status": "stored", "transcript_id": tid}
    except Exception as e:
        logger.error(f"Failed to store transcript: {e}")
        raise HTTPException(status_code=500, detail="Failed to store transcript")


@router.post("/send-email-fallback")
async def send_email_fallback(
    survey_id: str,
    email: str,
    survey_url: str,
    language: str = "en",
):
    """Send an email survey link as fallback when call fails or is declined."""
    from db import build_html_email, build_text_email
    subject = "We'd love your feedback! / ¡Nos encantaría conocer su opinión!" if language == "bilingual" else (
        "¡Su Encuesta Está Lista!" if language == "es" else "We'd love your feedback!"
    )
    survey_url = _with_language_query(survey_url, language)
    html_body = build_html_email(survey_url, language=language)
    text_body = build_text_email(survey_url, language=language)
    smtp_host = (os.getenv("SMTP_HOST", "") or "").lower()
    prefer_smtp = "amazonaws.com" in smtp_host or "mailjet.com" in smtp_host

    if prefer_smtp:
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER", "")
            smtp_pass = os.getenv("SMTP_PASSWORD", "")
            smtp_from = os.getenv("SMTP_FROM_EMAIL") or smtp_user or "noreply@aidevlab.com"
            smtp_from_name = os.getenv("SMTP_FROM_NAME", "SurvAI")

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{smtp_from_name} <{smtp_from}>"
            msg["To"] = email
            msg["Reply-To"] = smtp_from

            import email.utils as _eu
            msg["Message-ID"] = _eu.make_msgid(domain=smtp_from.split("@")[-1] if "@" in smtp_from else "aidevlab.com")
            msg["Date"] = _eu.formatdate(localtime=True)
            msg["X-Priority"] = "3"
            msg["List-Unsubscribe"] = f"<mailto:{smtp_from}?subject=unsubscribe>"

            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            if smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
                try:
                    server.starttls()
                except smtplib.SMTPNotSupportedError:
                    pass
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, [email], msg.as_string())
            server.quit()
            logger.info(f"Email fallback sent via SMTP for survey {survey_id} to {email}")
            return {"status": "sent", "email": email, "survey_id": survey_id}
        except Exception as e:
            logger.warning(f"SMTP fallback failed for {email}: {e}")

    # 1) Try MailerSend
    try:
        from mailersend import emails as ms_emails
        api_key = os.getenv("MAILERSEND_API_KEY", "")
        sender_email = os.getenv("MAILERSEND_SENDER_EMAIL", "")
        if api_key and not api_key.startswith("<"):
            mailer = ms_emails.NewEmail(api_key)
            mail_body = {}
            mailer.set_mail_from({"name": "SurvAI", "email": sender_email}, mail_body)
            mailer.set_mail_to([{"name": "Recipient", "email": email}], mail_body)
            mailer.set_subject(subject, mail_body)
            mailer.set_html_content(html_body, mail_body)
            mailer.send(mail_body)
            logger.info(f"Email fallback sent via MailerSend for survey {survey_id} to {email}")
            return {"status": "sent", "email": email, "survey_id": survey_id}
    except Exception as e:
        logger.warning(f"MailerSend fallback failed for {email}: {e}")

    # 2) Try Resend
    try:
        import resend as _resend
        resend_key = os.getenv("RESEND_API_KEY", "")
        resend_from = os.getenv("RESEND_FROM_EMAIL", "")
        if resend_key and resend_from:
            _resend.api_key = resend_key
            _resend.Emails.send({"from": resend_from, "to": email, "subject": subject, "html": html_body})
            logger.info(f"Email fallback sent via Resend for survey {survey_id} to {email}")
            return {"status": "sent", "email": email, "survey_id": survey_id}
    except Exception as e:
        logger.warning(f"Resend fallback failed for {email}: {e}")

    # 3) Try SMTP as a final fallback when SES was not preferred above
    if not prefer_smtp:
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            smtp_host = os.getenv("SMTP_HOST", "")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER", "")
            smtp_pass = os.getenv("SMTP_PASSWORD", "")
            smtp_from = os.getenv("SMTP_FROM_EMAIL") or smtp_user or "noreply@aidevlab.com"
            smtp_from_name = os.getenv("SMTP_FROM_NAME", "SurvAI")

            if smtp_host:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{smtp_from_name} <{smtp_from}>"
                msg["To"] = email
                msg["Reply-To"] = smtp_from

                import email.utils as _eu
                msg["Message-ID"] = _eu.make_msgid(domain=smtp_from.split("@")[-1] if "@" in smtp_from else "aidevlab.com")
                msg["Date"] = _eu.formatdate(localtime=True)
                msg["X-Priority"] = "3"
                msg["List-Unsubscribe"] = f"<mailto:{smtp_from}?subject=unsubscribe>"

                msg.attach(MIMEText(text_body, "plain"))
                msg.attach(MIMEText(html_body, "html"))

                if smtp_port == 465:
                    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
                else:
                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
                    try:
                        server.starttls()
                    except smtplib.SMTPNotSupportedError:
                        pass
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_from, [email], msg.as_string())
                server.quit()
                logger.info(f"Email fallback sent via SMTP for survey {survey_id} to {email}")
                return {"status": "sent", "email": email, "survey_id": survey_id}
        except Exception as e:
            logger.warning(f"SMTP fallback failed for {email}: {e}")

    logger.error(f"All email fallback methods failed for survey {survey_id} to {email}")
    return {"status": "failed", "error": "All email providers failed", "survey_url": survey_url}


# ─── Agent callback endpoints (livekit-agent writes answers back to DB) ───────

@router.post("/record-answer")
async def api_record_answer(survey_id: str, question_id: str, answer: str):
    """Record a single answer from the voice agent into the database."""
    ok = db_record_answer(survey_id, question_id, answer)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to record answer")
    return {"status": "recorded", "survey_id": survey_id, "question_id": question_id}


@router.post("/complete-survey")
async def api_complete_survey(survey_id: str, reason: str = "completed"):
    """Mark a voice survey as completed (or other status) in the database."""
    status = "Completed" if reason == "completed" else "In-Progress"
    ok = update_survey_status(survey_id, status)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to update survey status")
    try:
        from db import async_execute
        await async_execute(
            "UPDATE surveys SET end_reason = :reason WHERE id = :sid",
            {"reason": reason, "sid": survey_id},
        )
    except Exception:
        pass
    await _release_call(survey_id=survey_id)
    return {"status": status, "survey_id": survey_id, "end_reason": reason}


@router.post("/confirm-call")
async def api_confirm_call(survey_id: str, phone: str | None = None):
    """Agent confirms the call was answered — prevents the watchdog from releasing the lock."""
    normalized_phone = _normalize_phone(phone or "")
    await _confirm_call(normalized_phone, survey_id)
    return {"status": "confirmed", "survey_id": survey_id}


@router.post("/release-call")
async def api_release_call(survey_id: str | None = None, phone: str | None = None):
    """Release an in-memory active call lock when an agent job exits."""
    normalized_phone = _normalize_phone(phone or "")
    await _release_call(survey_id=survey_id, phone=normalized_phone or None)
    return {"status": "released", "survey_id": survey_id, "phone": normalized_phone}


# ─── Direct call endpoint (dashboard calls this via gateway, skipping survey-service hop)

@router.post("/direct-call")
async def direct_call(to: str, survey_id: str, provider: str = "livekit", greetings: str = "", language: str = "bilingual"):
    """Dashboard-compatible endpoint: accepts 'to' param instead of 'phone'."""
    return await make_call(survey_id=survey_id, phone=to, provider=provider, greetings=greetings, language=language)


# ─── Backward Compatibility Aliases ──────────────────────────────────────────

agent_router = APIRouter(prefix="/api/agent", tags=["agent-compat"])


@agent_router.post("/make-call")
async def agent_make_call(survey_id: str, phone: str, provider: str = "livekit", greetings: str = ""):
    return await make_call(survey_id=survey_id, phone=phone, provider=provider, greetings=greetings)


@agent_router.get("/transcript/{survey_id}")
async def agent_get_transcript(survey_id: str):
    return await get_survey_transcript(survey_id)


@agent_router.post("/send-email-fallback")
async def agent_send_email(survey_id: str, email: str, survey_url: str):
    return await send_email_fallback(survey_id=survey_id, email=email, survey_url=survey_url)
