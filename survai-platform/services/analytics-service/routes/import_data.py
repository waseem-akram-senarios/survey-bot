"""
Import routes: CSV upload for riders, bulk survey generation.
"""

import csv
import io
import logging
import os
from typing import List
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from db import sql_execute

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/import", tags=["import"])


def _parse_csv(content: bytes) -> List[dict]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


@router.post("/riders")
async def import_riders(file: UploadFile = File(...)):
    """
    CSV upload for riders. Parse CSV and insert into riders table.
    Expected columns: name, phone, email (optional: biodata as JSON string).
    """
    try:
        content = await file.read()
        rows = _parse_csv(content)
        if not rows:
            raise HTTPException(status_code=400, detail="CSV is empty or has no data rows")

        inserted = 0
        for row in rows:
            name = (row.get("name") or row.get("rider_name") or "").strip()
            if not name:
                continue
            phone = (row.get("phone") or "").strip()
            email = (row.get("email") or "").strip()
            rider_id = str(uuid4())
            sql_execute(
                """INSERT INTO riders (id, name, phone, email)
                   VALUES (:id, :name, :phone, :email)""",
                {"id": rider_id, "name": name, "phone": phone or None, "email": email or None},
            )
            inserted += 1

        return {"status": "imported", "count": inserted}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import riders error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-surveys")
async def import_bulk_surveys(file: UploadFile = File(...)):
    """
    Generate surveys in bulk from CSV.
    Columns: rider_name, phone, email, template_name
    """
    try:
        content = await file.read()
        rows = _parse_csv(content)
        if not rows:
            raise HTTPException(status_code=400, detail="CSV is empty or has no data rows")

        template_names = sql_execute("SELECT name FROM templates WHERE status = 'Published'", {})
        valid_templates = {t["name"] for t in template_names}

        created = []
        for row in rows:
            rider_name = (row.get("rider_name") or row.get("name") or "").strip()
            phone = (row.get("phone") or "").strip()
            email = (row.get("email") or "").strip()
            template_name = (row.get("template_name") or "").strip()
            if not template_name or template_name not in valid_templates:
                continue
            if not rider_name and not phone:
                continue

            survey_id = str(uuid4())
            from datetime import datetime, timezone
            launch_date = datetime.now(timezone.utc).isoformat()[:19].replace("T", " ")

            sql_execute(
                """INSERT INTO surveys (id, template_name, status, name, rider_name, phone, email, launch_date)
                   VALUES (:id, :template_name, 'In-Progress', :name, :rider_name, :phone, :email, :launch_date)""",
                {
                    "id": survey_id,
                    "template_name": template_name,
                    "name": template_name,
                    "rider_name": rider_name or None,
                    "phone": phone or None,
                    "email": email or None,
                    "launch_date": launch_date,
                },
            )

            # Create survey_response_items from template_questions
            tq = sql_execute(
                "SELECT question_id, ord FROM template_questions WHERE template_name = :tn ORDER BY ord",
                {"tn": template_name},
            )
            for t in tq:
                sql_execute(
                    """INSERT INTO survey_response_items (survey_id, question_id, ord)
                       VALUES (:survey_id, :question_id, :ord)""",
                    {"survey_id": survey_id, "question_id": t["question_id"], "ord": t["ord"]},
                )

            created.append({"survey_id": survey_id, "rider_name": rider_name, "phone": phone, "template_name": template_name})

        return {"status": "created", "count": len(created), "surveys": created}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk surveys import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
