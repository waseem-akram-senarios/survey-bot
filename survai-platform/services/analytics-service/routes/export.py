"""
Export routes: CSV export for surveys, transcripts, campaigns.
"""

import csv
import io
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from db import sql_execute

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/export", tags=["export"])


def _stream_csv(rows: list, columns: list, filename: str):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([row.get(c, "") for c in columns])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/surveys")
async def export_surveys():
    """Export survey responses as CSV."""
    try:
        rows = sql_execute(
            """SELECT s.id, s.template_name, s.status, s.rider_name, s.phone, s.email,
                      s.launch_date, s.completion_date, s.channel,
                      sri.question_id, q.text AS question_text, sri.raw_answer, sri.answer
               FROM surveys s
               LEFT JOIN survey_response_items sri ON sri.survey_id = s.id
               LEFT JOIN questions q ON q.id = sri.question_id
               ORDER BY s.id, sri.ord""",
            {},
        )
        columns = ["id", "template_name", "status", "rider_name", "phone", "email", "launch_date", "completion_date", "channel", "question_id", "question_text", "raw_answer", "answer"]
        return _stream_csv(rows, columns, "survey_responses.csv")
    except Exception as e:
        logger.error(f"Export surveys error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcripts")
async def export_transcripts():
    """Export call transcripts as CSV."""
    try:
        rows = sql_execute(
            """SELECT id, survey_id, full_transcript, call_duration_seconds,
                      call_started_at, call_ended_at, call_status, call_attempts, channel
               FROM call_transcripts
               ORDER BY call_started_at DESC""",
            {},
        )
        columns = ["id", "survey_id", "full_transcript", "call_duration_seconds", "call_started_at", "call_ended_at", "call_status", "call_attempts", "channel"]
        return _stream_csv(rows, columns, "call_transcripts.csv")
    except Exception as e:
        logger.error(f"Export transcripts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/{campaign_id}")
async def export_campaign(campaign_id: str):
    """Export campaign data as CSV."""
    try:
        rows = sql_execute(
            """SELECT s.id, s.template_name, s.status, s.rider_name, s.phone, s.email,
                      s.launch_date, s.completion_date, s.channel,
                      sri.question_id, q.text AS question_text, sri.raw_answer, sri.answer
               FROM surveys s
               LEFT JOIN survey_response_items sri ON sri.survey_id = s.id
               LEFT JOIN questions q ON q.id = sri.question_id
               WHERE s.campaign_id = :campaign_id
               ORDER BY s.id, sri.ord""",
            {"campaign_id": campaign_id},
        )
        if not rows:
            raise HTTPException(status_code=404, detail=f"No data for campaign {campaign_id}")
        columns = ["id", "template_name", "status", "rider_name", "phone", "email", "launch_date", "completion_date", "channel", "question_id", "question_text", "raw_answer", "answer"]
        return _stream_csv(rows, columns, f"campaign_{campaign_id}.csv")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export campaign error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/survey/{survey_id}/responses")
async def export_survey_responses(survey_id: str):
    """Export single survey responses as CSV."""
    try:
        survey = sql_execute("SELECT * FROM surveys WHERE id = :id", {"id": survey_id})
        if not survey:
            raise HTTPException(status_code=404, detail=f"Survey {survey_id} not found")

        rows = sql_execute(
            """SELECT sri.question_id, q.text AS question_text, sri.raw_answer, sri.answer, sri.ord
               FROM survey_response_items sri
               JOIN questions q ON q.id = sri.question_id
               WHERE sri.survey_id = :survey_id
               ORDER BY sri.ord""",
            {"survey_id": survey_id},
        )
        columns = ["question_id", "question_text", "raw_answer", "answer", "ord"]
        return _stream_csv(rows, columns, f"survey_{survey_id}_responses.csv")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export survey responses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
