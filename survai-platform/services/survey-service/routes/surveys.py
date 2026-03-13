"""
Survey routes for the Survey Service.
"""

import json
import logging
import os
import smtplib
import resend
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from concurrent.futures import ThreadPoolExecutor
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import List, Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Body
from mailersend import EmailBuilder, MailerSendClient
from pydantic import BaseModel

from shared.models.common import (
    CallbackRequest,
    Email,
    MakeCallRequest,
    SurveyCreateP,
    SurveyCSATUpdateP,
    SurveyDurationUpdateP,
    SurveyFromTemplateP,
    SurveyP,
    SurveyQnAP,
    SurveyQnAPhone,
    SurveyQuestionAnswerP,
    SurveyQuestionsP,
    SurveyStats,
    SurveyStatusUpdateP,
)
from shared.service_client import service_client

from db import (
    build_html_email,
    build_text_email,
    get_current_time,
    process_question_sync,
    process_survey_question,
    sql_execute,
)

logger = logging.getLogger(__name__)
router = APIRouter()

VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://voice-service:8017")
SCHEDULER_SERVICE_URL = os.getenv("SCHEDULER_SERVICE_URL", "http://scheduler-service:8070")


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def get_template_questions(template_name: str) -> dict:
    """Fetch template questions from template-service."""
    try:
        return await service_client.post(
            "template-service",
            "/api/templates/getquestions",
            json={"TemplateName": template_name},
        )
    except Exception as e:
        logger.error(f"Failed to fetch template questions: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Template service error: {str(e)}",
        )


async def get_survey_questions(survey_id: str) -> dict:
    """Get survey questions with answers from DB."""
    survey_row = sql_execute(
        "SELECT template_name, name FROM surveys WHERE id = :survey_id",
        {"survey_id": survey_id},
    )
    template_name = ""
    if survey_row:
        template_name = survey_row[0].get("template_name") or survey_row[0].get("name") or ""
    sql_query = """SELECT
  q.id AS id,
  q.text,
  q.criteria,
  q.scales,
  q.parent_id,
  sri.ord AS "order",
  sri.answer,
  sri.raw_answer,
  sri.autofill,
  COALESCE(qc.categories, null::json) AS categories,
  COALESCE(pm.parent_category_texts, null::json) AS parent_category_texts
 FROM survey_response_items sri
 JOIN questions q ON sri.question_id = q.id
 LEFT JOIN (
   SELECT question_id, json_agg(text ORDER BY CASE WHEN lower(text) = 'none of the above' THEN 1 ELSE 0 END, text) AS categories
   FROM question_categories GROUP BY question_id
 ) qc ON qc.question_id = q.id
 LEFT JOIN (
   SELECT m.child_question_id, json_agg(qc2.text ORDER BY qc2.text) AS parent_category_texts
   FROM question_category_mappings m
   JOIN question_categories qc2 ON qc2.id = m.parent_category_id
   GROUP BY m.child_question_id
 ) pm ON pm.child_question_id = q.id
 WHERE sri.survey_id = :survey_id
 ORDER BY sri.ord;"""
    rows = sql_execute(sql_query, {"survey_id": survey_id})
    return {"SurveyId": survey_id, "TemplateName": template_name, "Questions": rows}


TENANT_DISPLAY_NAMES: dict = {
    "itcurves": "IT Curves",
}


def _resolve_company_name(row: dict) -> str:
    """Resolve company name: DB field > tenant lookup > env var."""
    # 1. Explicit company_name on the survey
    if row.get("company_name"):
        return row["company_name"]
    # 2. Lookup from tenant_id
    tenant_id = row.get("tenant_id") or ""
    if tenant_id:
        name = TENANT_DISPLAY_NAMES.get(tenant_id.lower())
        if name:
            return name
    # 3. Env fallback
    return os.getenv("ORGANIZATION_NAME", "SurvAI")

async def get_survey_recipient(survey_id: str) -> dict:
    """Get recipient info for a survey."""
    rows = sql_execute(
        "SELECT recipient, name, ride_id, tenant_id, rider_name, biodata, bilingual, company_name FROM surveys WHERE id = :survey_id",
        {"survey_id": survey_id},
    )
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    
    r = rows[0]
    company_name = _resolve_company_name(r)
    return {
        "SurveyId": survey_id,
        "Recipient": r["recipient"],
        "Name": r["name"],
        "RideID": r["ride_id"],
        "TenantID": r.get("tenant_id") or "",
        "CompanyName": company_name,
        "Biodata": r.get("biodata", ""),
        "RiderName": r["rider_name"],
        "Bilingual": r.get("bilingual", True),
    }


def transform_qna(qna_data: dict) -> List[dict]:
    """Transform qna payload to question list."""
    result = []
    for key, value in qna_data.items():
        if key == "SurveyId" or not isinstance(value, str):
            continue
        if value.startswith("{"):
            continue
        result.append({"QueId": key, "RawAns": value, "Ans": value})
    return result


async def process_survey_questions_background(qna_data: dict):
    """Background task to process survey questions from phone submission."""
    try:
        survey_id = qna_data.pop("SurveyId", None)
        if not survey_id:
            return

        questions = transform_qna(qna_data)
        survey_data = await get_survey_questions(survey_id)
        survey_questions = survey_data.get("Questions", [])
        survey_questions_dict = {str(q.get("id")): q for q in survey_questions}

        questions_dicts = []
        for q in questions:
            detailed = survey_questions_dict.get(q["QueId"])
            if detailed:
                questions_dicts.append({
                    "QueId": q["QueId"],
                    "QueText": detailed.get("text", ""),
                    "QueCriteria": detailed.get("criteria", ""),
                    "QueScale": detailed.get("scales"),
                    "QueCategories": detailed.get("categories") or [],
                    "Ans": q.get("Ans"),
                    "RawAns": q.get("RawAns"),
                    "Order": detailed.get("order", 0),
                })

        with ThreadPoolExecutor() as executor:
            processed = list(executor.map(process_survey_question, questions_dicts))

        for i, q in enumerate(questions_dicts):
            if not q.get("Ans") and processed[i].get("Ans"):
                q["Ans"] = processed[i]["Ans"]

        for item in questions_dicts:
            sql_execute(
                """INSERT INTO survey_response_items (survey_id, question_id, answer, raw_answer, ord)
                VALUES (:survey_id, :question_id, :answer, :raw_answer, :ord)
                ON CONFLICT (survey_id, question_id)
                DO UPDATE SET answer = EXCLUDED.answer, raw_answer = EXCLUDED.raw_answer, ord = EXCLUDED.ord""",
                {
                    "survey_id": survey_id,
                    "question_id": item["QueId"],
                    "answer": item.get("Ans"),
                    "raw_answer": item.get("RawAns"),
                    "ord": item.get("Order", 0),
                },
            )

        sql_execute(
            """UPDATE surveys SET status = :status, completion_date = :completion_date WHERE id = :survey_id""",
            {
                "survey_id": survey_id,
                "status": "Completed",
                "completion_date": str(get_current_time())[:19].replace("T", " "),
            },
        )
        logger.info(f"Processed survey questions for survey {survey_id}")
    except Exception as e:
        logger.warning(f"Error processing survey questions: {e}")


class _QuestionObj:
    """Simple object for process_question_sync."""
    def __init__(self, d):
        for k, v in d.items():
            setattr(self, k, v)


def _row_to_survey(r: dict) -> SurveyP:
    """Convert a database row to a SurveyP model."""
    return SurveyP(
        SurveyId=r["id"],
        Biodata=r["biodata"],
        Recipient=r["recipient"],
        Name=r["name"],
        RiderName=r["rider_name"],
        RideId=r["ride_id"],
        TenantId=r["tenant_id"],
        URL=r["url"],
        Status=r["status"],
        LaunchDate=str(r["launch_date"])[:19] if r.get("launch_date") else "",
        CompletionDate=str(r.get("completion_date") or "")[:19],
        EndReason=r.get("end_reason") or "",
        Bilingual=r.get("bilingual", True),
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────
# IMPORTANT: Literal GET paths MUST be defined before parameterized GET paths
# to prevent FastAPI from matching e.g. /surveys/stat as /surveys/{survey_id}

# ─── Static/literal GET routes (before any {survey_id} routes) ───────────────

@router.get("/surveys/stat", response_model=SurveyStats)
async def survey_stat(tenant_id: Optional[str] = None):
    """Survey stats (dashboard uses /surveys/stat)."""
    return await get_survey_stats(tenant_id)


@router.get("/surveys/stats", response_model=SurveyStats)
async def get_survey_stats(tenant_id: Optional[str] = None):
    """Get survey statistics. Optionally filter by tenant_id."""
    if tenant_id:
        rows = sql_execute("""
            SELECT
                COUNT(*) FILTER (WHERE TRUE) AS total_surveys,
                COUNT(*) FILTER (WHERE status = 'Completed') AS total_completed_surveys,
                COUNT(*) FILTER (WHERE status = 'In-Progress') AS total_active_surveys,
                COUNT(*) FILTER (WHERE status = 'Completed' AND DATE(completion_date) = CURRENT_DATE) AS completed_surveys_today,
                COALESCE(ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY completion_duration) FILTER (WHERE status = 'Completed')), 0) AS durations_median,
                COALESCE(ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY completion_duration) FILTER (WHERE status = 'Completed' AND DATE(completion_date) = CURRENT_DATE)), 0) AS durations_today_median,
                COALESCE(ROUND(AVG(csat) FILTER (WHERE status = 'Completed')), 0) AS csat_avg
            FROM surveys
            WHERE tenant_id = :tid
        """, {"tid": tenant_id})
    else:
        rows = sql_execute("""
            SELECT
                COUNT(*) FILTER (WHERE TRUE) AS total_surveys,
                COUNT(*) FILTER (WHERE status = 'Completed') AS total_completed_surveys,
                COUNT(*) FILTER (WHERE status = 'In-Progress') AS total_active_surveys,
                COUNT(*) FILTER (WHERE status = 'Completed' AND DATE(completion_date) = CURRENT_DATE) AS completed_surveys_today,
                COALESCE(ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY completion_duration) FILTER (WHERE status = 'Completed')), 0) AS durations_median,
                COALESCE(ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY completion_duration) FILTER (WHERE status = 'Completed' AND DATE(completion_date) = CURRENT_DATE)), 0) AS durations_today_median,
                COALESCE(ROUND(AVG(csat) FILTER (WHERE status = 'Completed')), 0) AS csat_avg
            FROM surveys
        """, {})
    if not rows:
        return SurveyStats(
            Total_Surveys=0, Total_Active_Surveys=0, Total_Completed_Surveys=0,
            Total_Completed_Surveys_Today=0, Median_Completion_Duration=0,
            Median_Completion_Duration_Today=0, AverageCSAT=0.0,
        )
    r = rows[0]
    return SurveyStats(
        Total_Surveys=r["total_surveys"] or 0,
        Total_Active_Surveys=r["total_active_surveys"] or 0,
        Total_Completed_Surveys=r["total_completed_surveys"] or 0,
        Total_Completed_Surveys_Today=r["completed_surveys_today"] or 0,
        Median_Completion_Duration=int(r["durations_median"] or 0),
        Median_Completion_Duration_Today=int(r["durations_today_median"] or 0),
        AverageCSAT=float(r["csat_avg"] or 0),
    )


@router.get("/surveys/canary")
async def survey_canary():
    return {"version": "1.0.1", "status": "deployed", "feature": "incentive_tracking_fix"}


@router.get("/surveys", response_model=List[SurveyP])
async def list_surveys(tenant_id: Optional[str] = None):
    """List all surveys. Optionally filter by tenant_id."""
    if tenant_id:
        rows = sql_execute("SELECT * FROM surveys WHERE tenant_id = :tid", {"tid": tenant_id})
    else:
        rows = sql_execute("SELECT * FROM surveys", {})
    return [_row_to_survey(r) for r in rows]


@router.get("/surveys/list", response_model=List[SurveyP])
async def list_surveys_alias(tenant_id: Optional[str] = None):
    """Alias: /surveys/list (dashboard expects this path)."""
    return await list_surveys(tenant_id)


@router.get("/surveys/list_completed", response_model=List[SurveyP])
async def list_completed_surveys(tenant_id: Optional[str] = None):
    """List only completed surveys."""
    if tenant_id:
        rows = sql_execute("SELECT * FROM surveys WHERE status = 'Completed' AND tenant_id = :tid", {"tid": tenant_id})
    else:
        rows = sql_execute("SELECT * FROM surveys WHERE status = 'Completed'", {})
    return [_row_to_survey(r) for r in rows]


@router.get("/surveys/list_inprogress", response_model=List[SurveyP])
async def list_inprogress_surveys(tenant_id: Optional[str] = None):
    """List only in-progress surveys."""
    if tenant_id:
        rows = sql_execute("SELECT * FROM surveys WHERE status = 'In-Progress' AND tenant_id = :tid", {"tid": tenant_id})
    else:
        rows = sql_execute("SELECT * FROM surveys WHERE status = 'In-Progress'", {})
    return [_row_to_survey(r) for r in rows]


@router.get("/surveys/fromtemplate/{template_name}", response_model=SurveyFromTemplateP)
async def get_surveys_from_template(template_name: str):
    """Get survey stats for template."""
    rows = sql_execute("""
        SELECT
            COUNT(*) FILTER (WHERE template_name = :template_name) AS total_surveys,
            SUM(CASE WHEN status = 'Completed' AND template_name = :template_name THEN 1 ELSE 0 END) AS total_completed_surveys,
            SUM(CASE WHEN status != 'Completed' AND template_name = :template_name THEN 1 ELSE 0 END) AS total_active_surveys
        FROM surveys
    """, {"template_name": template_name})
    if not rows:
        return SurveyFromTemplateP(Total=0, Completed=0, InProgress=0)
    r = rows[0]
    return SurveyFromTemplateP(
        Total=r["total_surveys"] or 0,
        Completed=r["total_completed_surveys"] or 0,
        InProgress=r["total_active_surveys"] or 0,
    )


# ─── Parameterized GET routes ({survey_id}) ──────────────────────────────────

@router.get("/surveys/{survey_id}", response_model=SurveyP)
async def get_survey(survey_id: str):
    """Get survey by ID."""
    rows = sql_execute("SELECT * FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    return _row_to_survey(rows[0])


@router.get("/surveys/{survey_id}/status")
async def get_survey_status(survey_id: str):
    """Get survey status (recipient app expects this)."""
    rows = sql_execute("SELECT * FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    r = rows[0]
    return {
        "SurveyId": survey_id,
        "Status": r["status"],
        "LaunchDate": str(r["launch_date"])[:19] if r.get("launch_date") else "",
        "CompletionDate": str(r.get("completion_date") or "")[:19],
        "CSAT": r.get("csat"),
    }


@router.get("/surveys/{survey_id}/recipient")
async def get_survey_recipient_endpoint(survey_id: str):
    """Get recipient info."""
    return await get_survey_recipient(survey_id)


@router.get("/surveys/{survey_id}/recipient_info")
async def get_survey_recipient_info(survey_id: str):
    """Alias for recipient info (LiveKit agent uses this)."""
    return await get_survey_recipient(survey_id)


@router.get("/surveys/{survey_id}/questions")
async def get_survey_questions_endpoint(survey_id: str):
    """Get survey questions with answers."""
    rows = sql_execute("SELECT id FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    return await get_survey_questions(survey_id)


@router.get("/surveys/{survey_id}/questions_unanswered")
async def get_survey_questions_unanswered(survey_id: str):
    """Get only unanswered questions for a survey."""
    rows = sql_execute("SELECT id FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    questions = sql_execute("""
        SELECT q.id AS id, q.text, q.criteria, q.scales, q.parent_id,
               sri.ord AS "order", sri.answer, sri.raw_answer, sri.autofill,
               COALESCE(qc.categories, null::json) AS categories,
               COALESCE(pm.parent_category_texts, null::json) AS parent_category_texts
        FROM survey_response_items sri
        JOIN questions q ON sri.question_id = q.id
        LEFT JOIN (SELECT question_id, json_agg(text ORDER BY CASE WHEN lower(text) = 'none of the above' THEN 1 ELSE 0 END, text) AS categories FROM question_categories GROUP BY question_id) qc ON qc.question_id = q.id
        LEFT JOIN (SELECT m.child_question_id, json_agg(qc2.text ORDER BY qc2.text) AS parent_category_texts FROM question_category_mappings m JOIN question_categories qc2 ON qc2.id = m.parent_category_id GROUP BY m.child_question_id) pm ON pm.child_question_id = q.id
        WHERE sri.survey_id = :survey_id AND sri.answer IS NULL AND sri.raw_answer IS NULL
        ORDER BY sri.ord
    """, {"survey_id": survey_id})
    return {"SurveyId": survey_id, "Questions": questions}


@router.get("/surveys/{survey_id}/questionsonly")
async def get_survey_questions_only(survey_id: str):
    """Get just question texts for a survey."""
    rows = sql_execute(
        "SELECT q.text FROM survey_response_items sri JOIN questions q ON sri.question_id = q.id WHERE sri.survey_id = :survey_id",
        {"survey_id": survey_id},
    )
    return [r["text"] for r in rows]


@router.get("/surveys/{survey_id}/transcript")
async def get_transcript(survey_id: str):
    """Get call transcript."""
    rows = sql_execute("SELECT call_id FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    call_id = rows[0].get("call_id")
    if not call_id:
        raise HTTPException(status_code=404, detail=f"No call for Survey {survey_id}")

    try:
        from livekit_caller import get_livekit_transcript
        transcript = await get_livekit_transcript(call_id)
        return {"transcript": transcript, "provider": "livekit"}
    except ImportError:
        raise HTTPException(status_code=500, detail="LiveKit transcript module not available")


# ─── POST/PATCH/DELETE routes ────────────────────────────────────────────────

@router.post("/surveys/generate", response_model=SurveyQuestionsP)
async def generate_survey(survey_data: SurveyCreateP):
    """Generate survey from template."""
    try:
        res = sql_execute("SELECT * FROM surveys WHERE id = :survey_id", {"survey_id": survey_data.SurveyId})
        if res:
            raise HTTPException(status_code=400, detail=f"Survey with ID {survey_data.SurveyId} already exists")

        res = sql_execute("SELECT * FROM templates WHERE name = :template_name", {"template_name": survey_data.Name})
        if not res:
            raise HTTPException(status_code=404, detail=f"Template with Name {survey_data.Name} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        # Resolve company name: from request > template (if column exists) > env
        req_company = getattr(survey_data, "CompanyName", None) or ""
        if not req_company:
            try:
                tpl_rows = sql_execute("SELECT company_name FROM templates WHERE name = :tn", {"tn": survey_data.Name})
                if tpl_rows and tpl_rows[0].get("company_name"):
                    req_company = tpl_rows[0]["company_name"]
            except Exception:
                pass  # templates.company_name may not exist on older DBs

        sql_execute(
            """INSERT INTO surveys (id, template_name, url, biodata, status, name, recipient, launch_date, rider_name, ride_id, tenant_id, phone, bilingual, company_name)
            VALUES (:id, :template_name, :url, :biodata, :status, :name, :recipient, :launch_date, :rider_name, :ride_id, :tenant_id, :phone, :bilingual, :company_name)""",
            {
                "id": survey_data.SurveyId,
                "template_name": survey_data.Name,
                "url": survey_data.URL,
                "biodata": survey_data.Biodata,
                "status": "In-Progress",
                "name": survey_data.Name,
                "recipient": survey_data.Recipient,
                "launch_date": str(get_current_time())[:19].replace("T", " "),
                "rider_name": survey_data.RiderName,
                "ride_id": survey_data.RideId,
                "tenant_id": survey_data.TenantId,
                "phone": survey_data.Phone,
                "bilingual": getattr(survey_data, "Bilingual", True),
                "company_name": req_company or None,
            },
        )

        template_response = await get_template_questions(survey_data.Name)
        template_questions = template_response.get("Questions", [])

        if isinstance(template_questions, dict):
            template_questions = list(template_questions.values()) if template_questions else []
        template_questions = list(template_questions) if template_questions else []

        template_questions.sort(key=lambda q: int(q.get("ord", 0) or 0))
        que_data_lookup = {str(q.get("id")): q for q in template_questions}

        questions = []
        for tq in template_questions:
            qid = str(tq.get("id", ""))
            qdata = que_data_lookup.get(qid, {})
            cats = qdata.get("categories")
            if isinstance(cats, str):
                try:
                    cats = json.loads(cats) if cats else []
                except (json.JSONDecodeError, TypeError):
                    cats = []
            elif cats is None:
                cats = []

            questions.append({
                "QueId": qid,
                "QueText": qdata.get("text", ""),
                "Order": tq.get("ord", 0),
                "QueScale": qdata.get("scales"),
                "QueCriteria": qdata.get("criteria", ""),
                "QueCategories": cats,
                "ParentId": qdata.get("parent_id"),
                "ParentCategoryTexts": qdata.get("parent_category_texts") or [],
                "Autofill": qdata.get("autofill", "No"),
            })

        autofill_questions = [q for q in questions if q.get("Autofill") == "Yes"]
        biodata = survey_data.Biodata or ""

        if autofill_questions and biodata:
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(
                    lambda q: process_question_sync(_QuestionObj(q), biodata),
                    autofill_questions,
                ))
            autofill_lookup = {item.QueId: item for item in results if item is not None}
        else:
            autofill_lookup = {}

        insert_params = []
        for q in questions:
            af = autofill_lookup.get(q["QueId"])
            insert_params.append({
                "survey_id": survey_data.SurveyId,
                "question_id": q["QueId"],
                "answer": af.Ans if af else None,
                "ord": q["Order"],
                "autofill": q.get("Autofill", "No"),
            })

        if insert_params:
            sql_execute(
                """INSERT INTO survey_response_items (survey_id, question_id, answer, ord, autofill)
                VALUES (:survey_id, :question_id, :answer, :ord, :autofill)
                ON CONFLICT (survey_id, question_id)
                DO UPDATE SET answer = EXCLUDED.answer, autofill = EXCLUDED.autofill""",
                insert_params,
            )

        return SurveyQuestionsP(SurveyId=survey_data.SurveyId, QuestionswithAns=questions)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/surveys/create")
async def create_survey(survey_data: SurveyQuestionsP):
    """Create survey questions and autofill where needed (dashboard uses this after generate)."""
    try:
        # Ensure survey exists (from generate step)
        rows = sql_execute("SELECT id FROM surveys WHERE id = :survey_id", {"survey_id": survey_data.SurveyId})
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Survey {survey_data.SurveyId} not found. Generate the survey first, then launch.",
            )

        autofill_questions = [q for q in survey_data.QuestionswithAns if getattr(q, "Autofill", "No") == "Yes"]

        biodata = ""
        try:
            rows = sql_execute("SELECT biodata FROM surveys WHERE id = :survey_id", {"survey_id": survey_data.SurveyId})
            if rows:
                biodata = rows[0]["biodata"] or ""
        except Exception:
            pass

        autofill_lookup = {}
        if autofill_questions and biodata:
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(
                    lambda q: process_question_sync(_QuestionObj(q.model_dump()), biodata),
                    autofill_questions,
                ))
            autofill_lookup = {item.QueId: item for item in results if item is not None}

        insert_params = []
        for item in survey_data.QuestionswithAns:
            autofill = autofill_lookup.get(item.QueId)
            autofill_val = getattr(item, "Autofill", None) or getattr(item, "AutoFill", "No")
            insert_params.append({
                "survey_id": survey_data.SurveyId,
                "question_id": item.QueId,
                "answer": autofill.Ans if autofill else None,
                "ord": item.Order,
                "autofill": autofill_val if autofill_val in ("Yes", "No") else "No",
            })

        if insert_params:
            sql_execute(
                """INSERT INTO survey_response_items (survey_id, question_id, answer, ord, autofill)
                VALUES (:survey_id, :question_id, :answer, :ord, :autofill)
                ON CONFLICT (survey_id, question_id)
                DO UPDATE SET answer = EXCLUDED.answer, autofill = EXCLUDED.autofill""",
                insert_params,
            )

        try:
            sql_execute(
                "UPDATE surveys SET ai_augmented = :ai_augmented WHERE id = :survey_id",
                {"ai_augmented": survey_data.AiAugmented, "survey_id": survey_data.SurveyId},
            )
        except Exception:
            pass

        return {"message": f"Questions added to SurveyId {survey_data.SurveyId}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/surveys/{survey_id}/status")
async def update_survey_status(survey_id: str, status_update: SurveyStatusUpdateP):
    """Update survey status."""
    rows = sql_execute("SELECT * FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    if rows[0]["status"] == "Completed":
        raise HTTPException(status_code=400, detail=f"Survey {survey_id} already completed")

    comp_date = str(get_current_time())[:19].replace("T", " ") if status_update.Status == "Completed" else None
    sql_execute(
        "UPDATE surveys SET status = :status, completion_date = :completion_date WHERE id = :survey_id",
        {"survey_id": survey_id, "status": status_update.Status, "completion_date": comp_date},
    )
    return {"message": f"Status updated for SurveyId {survey_id}"}


@router.patch("/surveys/{survey_id}/csat")
async def update_survey_csat(survey_id: str, csat_update: SurveyCSATUpdateP):
    """Update CSAT score."""
    rows = sql_execute("SELECT * FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    if rows[0]["status"] == "In-Progress":
        raise HTTPException(status_code=400, detail=f"Survey {survey_id} is In-Progress")
    if rows[0].get("csat"):
        raise HTTPException(status_code=400, detail=f"Survey {survey_id} already has CSAT")

    sql_execute(
        "UPDATE surveys SET csat = :csat WHERE id = :survey_id",
        {"survey_id": survey_id, "csat": csat_update.CSAT},
    )
    return {"message": f"CSAT updated for SurveyId {survey_id}"}


@router.patch("/surveys/{survey_id}/duration")
async def update_survey_duration(survey_id: str, duration_update: SurveyDurationUpdateP):
    """Update completion duration."""
    rows = sql_execute("SELECT * FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    if rows[0]["status"] == "In-Progress":
        raise HTTPException(status_code=400, detail=f"Survey {survey_id} is In-Progress")
    if rows[0].get("completion_duration"):
        raise HTTPException(status_code=400, detail=f"Survey {survey_id} already has duration")

    sql_execute(
        "UPDATE surveys SET completion_duration = :completion_duration WHERE id = :survey_id",
        {"survey_id": survey_id, "completion_duration": duration_update.CompletionDuration},
    )
    return {"message": f"Duration updated for SurveyId {survey_id}"}


@router.patch("/surveys/{survey_id}/details")
async def update_survey_details(survey_id: str, recipient: str = None, rider_name: str = None, phone: str = None):
    """Update editable survey fields (recipient, rider_name, phone)."""
    rows = sql_execute("SELECT * FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    if rows[0]["status"] == "Completed":
        raise HTTPException(status_code=400, detail="Cannot edit a completed survey")

    updates = []
    params = {"survey_id": survey_id}
    if recipient is not None:
        updates.append("recipient = :recipient")
        params["recipient"] = recipient
    if rider_name is not None:
        updates.append("rider_name = :rider_name")
        params["rider_name"] = rider_name
    if phone is not None:
        updates.append("phone = :phone")
        params["phone"] = phone

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    sql_execute(f"UPDATE surveys SET {', '.join(updates)} WHERE id = :survey_id", params)
    return {"message": f"Survey {survey_id} updated"}


@router.post("/surveys/getquestions")
async def get_survey_questions_with_answers(body: SurveyQuestionsP):
    """Get survey questions with answers."""
    return await get_survey_questions(body.SurveyId)


@router.post("/surveys/submit", response_model=SurveyQnAP)
async def submit_survey(qna_data: SurveyQnAP):
    """Submit/update survey answers. Uses process_survey_question in parallel."""
    survey_id = qna_data.SurveyId
    questions = [q.model_dump() for q in qna_data.QuestionswithAns]

    with ThreadPoolExecutor() as executor:
        processed = list(executor.map(process_survey_question, questions))

    for i, q in enumerate(questions):
        if not q.get("Ans") and processed[i].get("Ans"):
            q["Ans"] = processed[i]["Ans"]

    for item in questions:
        sql_execute(
            """INSERT INTO survey_response_items (survey_id, question_id, answer, raw_answer, ord)
            VALUES (:survey_id, :question_id, :answer, :raw_answer, :ord)
            ON CONFLICT (survey_id, question_id)
            DO UPDATE SET answer = EXCLUDED.answer, raw_answer = EXCLUDED.raw_answer, ord = EXCLUDED.ord""",
            {
                "survey_id": survey_id,
                "question_id": item["QueId"],
                "answer": item.get("Ans"),
                "raw_answer": item.get("RawAns"),
                "ord": item.get("Order", 0),
            },
        )

    # Update survey status to Completed after submission
    sql_execute(
        """UPDATE surveys SET status = :status, completion_date = :completion_date WHERE id = :survey_id""",
        {
            "survey_id": survey_id,
            "status": "Completed",
            "completion_date": str(get_current_time())[:19].replace("T", " "),
        },
    )

    return SurveyQnAP(SurveyId=survey_id, QuestionswithAns=[SurveyQuestionAnswerP(**q) for q in questions])


@router.post("/surveys/submitphone")
async def submit_phone_answers(qna_data: SurveyQnAPhone, background_tasks: BackgroundTasks):
    """Submit phone answers. Processes raw answers in background."""
    data = qna_data.model_dump()
    background_tasks.add_task(process_survey_questions_background, data)
    return "Processing Started"


@router.post("/surveys/makecall")
async def makecall(request: MakeCallRequest):
    """Make call via voice-service /api/voice/make-call."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{VOICE_SERVICE_URL}/api/voice/make-call",
                params={
                    "survey_id": request.survey_id,
                    "phone": request.phone,
                    "provider": request.provider,
                    "language": request.language,
                },
            )
            if resp.status_code != 200:
                try:
                    err = resp.json().get("detail", resp.text)
                except Exception:
                    err = resp.text
                raise HTTPException(status_code=resp.status_code, detail=err)
            return resp.json()
    except httpx.RequestError as e:
        logger.error(f"Voice service call failed: {e}")
        raise HTTPException(status_code=502, detail=f"Voice service unreachable: {str(e)}")




def _send_via_smtp(to_email: str, subject: str, html_body: str, text_body: str):
    """Send email via SMTP. Supports both authenticated (Gmail/Brevo) and
    unauthenticated (local Postfix/boky) SMTP servers."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM_EMAIL") or smtp_user or "noreply@aidevlab.com"
    smtp_from_name = os.getenv("SMTP_FROM_NAME", "SurvAI")

    if not smtp_host:
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{smtp_from_name} <{smtp_from}>"
    msg["To"] = to_email
    msg["Reply-To"] = smtp_from
    msg["X-Mailer"] = "SurvAI Platform"

    # Deliverability headers — help land in inbox instead of spam
    import email.utils
    msg["Message-ID"] = email.utils.make_msgid(domain=smtp_from.split("@")[-1] if "@" in smtp_from else "aidevlab.com")
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["X-Priority"] = "3"  # Normal priority
    msg["X-PM-Message-Stream"] = "outbound"  # Postmark compatibility
    msg["Precedence"] = "bulk"  # Transactional/bulk
    # List-Unsubscribe header (improves deliverability with Gmail/Outlook)
    msg["List-Unsubscribe"] = f"<mailto:{smtp_from}?subject=unsubscribe>"

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    use_ssl = smtp_port == 465
    if use_ssl:
        server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
    else:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        try:
            server.starttls()
        except smtplib.SMTPNotSupportedError:
            pass
    if smtp_user and smtp_pass:
        server.login(smtp_user, smtp_pass)
    server.sendmail(smtp_from, [to_email], msg.as_string())
    server.quit()
    return True


def _send_via_resend(to_email: str, subject: str, html_body: str):
    """Send email via Resend. Returns True on success, False if not configured."""
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        return False

    resend.api_key = api_key
    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")

    resend.Emails.send({
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "html": html_body,
    })
    return True


def _with_language_query(url: str, language: str) -> str:
    """Force a survey URL into a specific language when requested."""
    if language not in {"en", "es"} or not url:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["lang"] = language
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


@router.post("/surveys/sendemail")
async def sendemail(email: Email):
    """Send email survey, preferring SMTP when AWS SES is configured."""
    lang = getattr(email, "Language", "en") or "en"
    url = _with_language_query(email.SurveyURL, lang)
    html_body = build_html_email(url, language=lang)
    text_body = build_text_email(url, language=lang)
    if lang == "es":
        subject = "¡Su Encuesta Está Lista!"
    elif lang == "bilingual":
        subject = "Your Survey is Ready! / ¡Su Encuesta Está Lista!"
    else:
        subject = "Your Survey is Ready!"
    errors = []
    smtp_host = (os.getenv("SMTP_HOST") or "").lower()
    prefer_smtp = "amazonaws.com" in smtp_host or "mailjet.com" in smtp_host

    if prefer_smtp:
        try:
            if _send_via_smtp(email.EmailTo, subject, html_body, text_body):
                logger.info(f"Survey email sent via SMTP to {email.EmailTo}")
                return {"message": "Email sent successfully"}
        except Exception as e:
            errors.append(f"SMTP: {e}")
            logger.warning(f"SMTP failed for {email.EmailTo}: {e}")

    # 1. Try MailerSend
    api_key = os.getenv("MAILERSEND_API_KEY")
    if api_key:
        try:
            sender_email = os.getenv("MAILERSEND_SENDER_EMAIL", "noreply@aidevlab.com")
            ms = MailerSendClient(api_key=api_key)
            msg = (
                EmailBuilder()
                .from_email(sender_email, "SurvAI")
                .to_many([{"email": email.EmailTo, "name": "Recipient"}])
                .subject(subject)
                .html(html_body)
                .text(text_body)
                .build()
            )
            ms.emails.send(msg)
            logger.info(f"Survey email sent via MailerSend to {email.EmailTo}")
            return {"message": "Email sent successfully"}
        except Exception as e:
            errors.append(f"MailerSend: {e}")
            logger.warning(f"MailerSend failed for {email.EmailTo}: {e}")

    # 2. Try Resend
    try:
        if _send_via_resend(email.EmailTo, subject, html_body):
            logger.info(f"Survey email sent via Resend to {email.EmailTo}")
            return {"message": "Email sent successfully"}
    except Exception as e:
        errors.append(f"Resend: {e}")
        logger.warning(f"Resend failed for {email.EmailTo}: {e}")

    # 3. Try SMTP (last resort unless SES was configured above)
    if not prefer_smtp:
        try:
            if _send_via_smtp(email.EmailTo, subject, html_body, text_body):
                logger.info(f"Survey email sent via SMTP to {email.EmailTo}")
                return {"message": "Email sent successfully"}
        except Exception as e:
            errors.append(f"SMTP: {e}")
            logger.warning(f"SMTP failed for {email.EmailTo}: {e}")

    if not errors:
        raise HTTPException(status_code=503, detail="No email provider configured. Set MAILERSEND_API_KEY, RESEND_API_KEY, or SMTP credentials.")
    raise HTTPException(status_code=500, detail=f"All email providers failed: {'; '.join(errors)}")


@router.post("/surveys/callback")
async def schedule_callback(request: CallbackRequest):
    """Schedule callback via scheduler-service (single scheduler instance)."""
    delay_seconds = request.delay_minutes * 60
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{SCHEDULER_SERVICE_URL}/api/scheduler/schedule-call",
                params={
                    "survey_id": request.survey_id,
                    "phone": request.phone,
                    "delay_seconds": delay_seconds,
                },
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Failed to schedule callback via scheduler-service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Translation endpoint (for text survey in Spanish) ───────────────────────

@router.get("/surveys/{survey_id}/questions_translated")
async def get_questions_translated(survey_id: str, lang: str = "es"):
    """Return survey questions with text translated to the target language."""
    rows = sql_execute("SELECT id FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")

    result = await get_survey_questions(survey_id)
    questions = [dict(q) for q in result.get("Questions", [])]

    if lang == "en" or not questions:
        return result

    texts = [q.get("text", "") for q in questions]
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        prompt = (
            "Translate each survey question below from English to Spanish. "
            "Return a JSON object with key \"translations\" containing an array of translated strings in the same order. "
            "Keep them natural and conversational.\n\n"
            + json.dumps(texts, ensure_ascii=False)
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(raw)
        translated = parsed if isinstance(parsed, list) else parsed.get("translations", parsed.get("questions", list(parsed.values())[0] if parsed else []))
        if isinstance(translated, list) and len(translated) == len(questions):
            for i, q in enumerate(questions):
                q["text_es"] = translated[i]
                q["text_original"] = q["text"]
                q["text"] = translated[i]
    except Exception as e:
        logger.warning(f"Translation failed for survey {survey_id}: {e}")

    return {**result, "Questions": questions, "Language": lang}


# ─── Aliases for frontend backward compatibility ─────────────────────────────

@router.post("/surveys/{survey_id}/csat")
async def update_survey_csat_post(survey_id: str, csat_update: SurveyCSATUpdateP):
    """POST alias for CSAT update (recipient app uses POST)."""
    return await update_survey_csat(survey_id, csat_update)


@router.post("/surveys/{survey_id}/duration")
async def update_survey_duration_post(survey_id: str, duration_update: SurveyDurationUpdateP):
    """POST alias for duration update (recipient app uses POST)."""
    return await update_survey_duration(survey_id, duration_update)


@router.delete("/surveys/{survey_id}")
async def delete_survey(survey_id: str):
    """Delete a survey and all its responses, transcripts, and analytics."""
    rows = sql_execute("SELECT * FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")
    
    # Delete related records in other tables first to avoid FK constraints
    sql_execute("DELETE FROM survey_analytics WHERE survey_id = :survey_id", {"survey_id": survey_id})
    sql_execute("DELETE FROM call_transcripts WHERE survey_id = :survey_id", {"survey_id": survey_id})
    sql_execute("DELETE FROM survey_response_items WHERE survey_id = :survey_id", {"survey_id": survey_id})
    # Finally delete the survey record
    sql_execute("DELETE FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    return {"message": f"Survey {survey_id} and all related data deleted successfully"}


@router.delete("/templates/delete")
async def delete_template_proxy(request: dict = Body(...)):
    """Proxy template deletion to template-service."""
    template_name = request.get("TemplateName")
    if not template_name:
        raise HTTPException(status_code=400, detail="TemplateName is required")
        
    try:
        # Check if there are any surveys using this template
        surveys = sql_execute("SELECT id FROM surveys WHERE template_name = :name LIMIT 1", {"name": template_name})
        if surveys:
            # If there are surveys, we can either block or delete them.
            # Usually better to block to prevent accidental massive data loss.
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete template '{template_name}' because it has existing surveys. Delete surveys first."
            )

        # Forward the delete request to template-service
        return await service_client.delete(
            "template-service",
            "/api/templates/delete",
            json={"TemplateName": template_name}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to proxy template deletion: {e}")
        raise HTTPException(status_code=502, detail=f"Template service error: {str(e)}")


@router.post("/surveys/email")
async def sendemail_alias(email: Email):
    """Alias: /surveys/email -> /surveys/sendemail (dashboard expects this)."""
    return await sendemail(email)


class SMSRequest(BaseModel):
    phone: str
    survey_id: str
    survey_url: Optional[str] = None
    rider_name: Optional[str] = None
    language: str = "en"


@router.post("/surveys/sendsms")
async def send_sms_survey(request: SMSRequest):
    """Send SMS with survey link - backup for missed calls."""
    from sms import send_survey_link_sms
    
    survey_url = request.survey_url
    if not survey_url:
        survey_url = f"{os.getenv('RECIPIENT_URL', 'http://localhost:8080')}/survey/{request.survey_id}"
    
    result = send_survey_link_sms(
        to_phone=request.phone,
        survey_url=survey_url,
        rider_name=request.rider_name,
        language=request.language
    )
    
    if result.get("success"):
        return {"status": "sent", "message_sid": result.get("message_sid")}
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "SMS send failed"))


@router.post("/surveys/sms")
async def send_sms_alias(request: SMSRequest):
    """Alias: /surveys/sms -> /surveys/sendsms."""
    return await send_sms_survey(request)


@router.post("/surveys/make-call")
async def make_call_alias(to: str, survey_id: str, run_at: Optional[str] = None, provider: str = "livekit", language: str = "bilingual"):
    """Alias: /surveys/make-call (dashboard expects hyphenated version)."""
    return await makecall(MakeCallRequest(survey_id=survey_id, phone=to, provider=provider, language=language))


@router.post("/answers/qna", response_model=SurveyQnAP)
async def update_survey_qna(qna_data: SurveyQnAP):
    """Submit answers (recipient app uses /answers/qna path)."""
    return await submit_survey(qna_data)


@router.post("/answers/qna_phone")
async def update_survey_qna_phone(qna_data: SurveyQnAPhone, background_tasks: BackgroundTasks):
    """Submit phone answers (voice agent callback path)."""
    return await submit_phone_answers(qna_data, background_tasks)


@router.post("/surveys/list_surveys_from_templates", response_model=SurveyFromTemplateP)
async def list_surveys_from_templates(template_name: dict):
    """Get survey stats from template (POST version)."""
    name = template_name.get("TemplateName", "")
    return await get_surveys_from_template(name)


# ─── Template Service Proxy Routes ───────────────────────────────────────────

@router.get("/templates/stat")
async def get_template_stat_proxy():
    """Proxy template stats to template-service."""
    return await service_client.get("template-service", "/api/templates/stat")


@router.get("/templates/list")
async def list_templates_proxy():
    """Proxy template list to template-service."""
    return await service_client.get("template-service", "/api/templates/list")


@router.get("/templates/list_drafts")
async def list_draft_templates_proxy():
    """Proxy draft template list to template-service."""
    return await service_client.get("template-service", "/api/templates/list_drafts")


@router.post("/templates/getquestions")
async def get_template_questions_proxy(request: dict = Body(...)):
    """Proxy get template questions to template-service."""
    return await service_client.post("template-service", "/api/templates/getquestions", json=request)


@router.post("/templates/clone")
async def clone_template_proxy(request: dict = Body(...)):
    """Proxy clone template to template-service."""
    return await service_client.post("template-service", "/api/templates/clone", json=request)


@router.post("/templates/create")
async def create_template_proxy(request: dict = Body(...)):
    """Proxy create template to template-service."""
    return await service_client.post("template-service", "/api/templates/create", json=request)


@router.patch("/templates/status")
async def update_template_status_proxy(request: dict = Body(...)):
    """Proxy update template status to template-service."""
    return await service_client.patch("template-service", "/api/templates/status", json=request)


@router.patch("/templates/update")
async def update_template_config_proxy(request: dict = Body(...)):
    """Proxy update template config to template-service."""
    return await service_client.patch("template-service", "/api/templates/update", json=request)


@router.post("/templates/addquestions")
async def add_question_to_template_proxy(request: dict = Body(...)):
    """Proxy add question to template-service."""
    return await service_client.post("template-service", "/api/templates/addquestions", json=request)


@router.delete("/templates/deletequestionbyidwithparentchild")
async def delete_question_proxy(request: dict = Body(...)):
    """Proxy delete question to template-service."""
    return await service_client.delete("template-service", "/api/templates/deletequestionbyidwithparentchild", json=request)


@router.post("/templates/translate")
async def translate_template_proxy(request: dict = Body(...)):
    """Proxy translate template to template-service."""
    return await service_client.post("template-service", "/api/templates/translate", json=request)


@router.post("/surveys/get-transcript")
async def get_transcript_post(survey_id: str):
    """POST alias for transcript (original monolith used POST)."""
    return await get_transcript(survey_id)


@router.post("/surveys/{survey_id}/question_answer")
async def get_survey_question_answer(survey_id: str, request: dict):
    """Get a specific question's answer within a survey."""
    que_id = request.get("QueId", "")
    rows = sql_execute("SELECT id FROM surveys WHERE id = :survey_id", {"survey_id": survey_id})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")

    question_rows = sql_execute("""
        SELECT q.id, q.text, q.criteria, q.scales, q.parent_id,
               sri.ord AS "order", sri.answer, sri.raw_answer, sri.autofill,
               COALESCE(qc.categories, null::json) AS categories,
               COALESCE(pm.parent_category_texts, null::json) AS parent_category_texts
        FROM survey_response_items sri
        JOIN questions q ON sri.question_id = q.id
        LEFT JOIN (SELECT question_id, json_agg(text ORDER BY CASE WHEN lower(text) = 'none of the above' THEN 1 ELSE 0 END, text) AS categories FROM question_categories GROUP BY question_id) qc ON qc.question_id = q.id
        LEFT JOIN (SELECT m.child_question_id, json_agg(qc2.text ORDER BY qc2.text) AS parent_category_texts FROM question_category_mappings m JOIN question_categories qc2 ON qc2.id = m.parent_category_id GROUP BY m.child_question_id) pm ON pm.child_question_id = q.id
        WHERE sri.survey_id = :survey_id AND sri.question_id = :question_id LIMIT 1
    """, {"survey_id": survey_id, "question_id": que_id})
    if not question_rows:
        raise HTTPException(status_code=404, detail=f"Question {que_id} not found for Survey {survey_id}")
    return question_rows[0]
