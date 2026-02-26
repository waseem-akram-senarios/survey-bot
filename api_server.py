"""
Survey Bot Call API

FastAPI server that exposes HTTP endpoints to trigger outbound survey calls
and query call records from the database.

Usage:
    uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

Endpoints:
    POST /call                    — dispatch the survey agent and place an outbound call
    GET  /calls/{phone_number}    — retrieve all call records for a phone number
    GET  /health                  — liveness check
"""

import json
import os
import random

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from livekit import api as lkapi_module
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Survey Bot Call API")


class CallRequest(BaseModel):
    phone_number: str  # E.164 format, e.g. "+15555550123"


@app.post("/call")
async def trigger_call(req: CallRequest):
    """Dispatch the survey agent and place an outbound call to the given phone number."""
    trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID", "")
    if not trunk_id.startswith("ST_"):
        raise HTTPException(status_code=500, detail="SIP_OUTBOUND_TRUNK_ID is not configured")

    room_name = f"outbound-{''.join(str(random.randint(0, 9)) for _ in range(10))}"
    lkapi = lkapi_module.LiveKitAPI()
    try:
        await lkapi.agent_dispatch.create_dispatch(
            lkapi_module.CreateAgentDispatchRequest(
                agent_name="survey-agent",
                room=room_name,
                metadata=json.dumps({"phone_number": req.phone_number}),
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await lkapi.aclose()

    return {
        "status": "dispatched",
        "room_name": room_name,
        "phone_number": req.phone_number,
    }


@app.get("/calls/{phone_number}")
def get_calls(phone_number: str):
    """Return all call records for a given phone number, newest first."""
    from db.database import get_connection
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, recipient_number, call_start_time,
                       call_duration_seconds, completed, call_transcript
                FROM calls
                WHERE recipient_number = %s
                ORDER BY call_start_time DESC
                """,
                (phone_number,),
            )
            rows = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return [
        {
            "id": r[0],
            "recipient_number": r[1],
            "call_start_time": r[2].isoformat() if r[2] else None,
            "call_duration_seconds": float(r[3]) if r[3] else None,
            "completed": r[4],
            "call_transcript": r[5],
        }
        for r in rows
    ]


@app.get("/health")
def health():
    """Liveness check."""
    return {"status": "ok"}
