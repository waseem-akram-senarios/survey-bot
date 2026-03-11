"""
Call audio recording via LiveKit Egress API.

Starts a room-composite egress (audio-only) when the call connects,
and stops it when the call ends.  Recorded files are uploaded to S3.

Set RECORDING_ENABLED=true and provide S3_* env vars to activate.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from livekit import api
from livekit.protocol import egress as egress_proto

from config.settings import (
    RECORDING_ENABLED,
    S3_ACCESS_KEY,
    S3_SECRET_KEY,
    S3_BUCKET,
    S3_REGION,
    S3_ENDPOINT,
)

logger = logging.getLogger("survey-agent.recording")


@dataclass
class RecordingHandle:
    egress_id: str = ""
    room_name: str = ""
    active: bool = False
    audio_url: str = ""


def is_recording_configured() -> bool:
    return RECORDING_ENABLED and bool(S3_ACCESS_KEY) and bool(S3_BUCKET)


async def start_call_recording(
    room_name: str,
    survey_id: str,
    lk_api: api.LiveKitAPI,
) -> Optional[RecordingHandle]:
    """Start an audio-only room composite egress and return a handle."""
    if not is_recording_configured():
        logger.debug("Recording not enabled or S3 not configured — skipping")
        return None

    filepath = f"call-recordings/{survey_id}/{room_name}.ogg"

    s3_upload = egress_proto.S3Upload(
        access_key=S3_ACCESS_KEY,
        secret=S3_SECRET_KEY,
        bucket=S3_BUCKET,
        region=S3_REGION,
    )
    if S3_ENDPOINT:
        s3_upload.endpoint = S3_ENDPOINT
        s3_upload.force_path_style = True

    request = egress_proto.RoomCompositeEgressRequest(
        room_name=room_name,
        audio_only=True,
        file_outputs=[
            egress_proto.EncodedFileOutput(
                file_type=egress_proto.EncodedFileType.OGG,
                filepath=filepath,
                s3=s3_upload,
            ),
        ],
    )

    try:
        info = await lk_api.egress.start_room_composite_egress(request)
        handle = RecordingHandle(
            egress_id=info.egress_id,
            room_name=room_name,
            active=True,
        )
        logger.info(f"Recording started — egress_id={info.egress_id}, path={filepath}")
        return handle
    except Exception as e:
        logger.warning(f"Failed to start recording for room {room_name}: {e}")
        return None


async def stop_call_recording(
    handle: Optional[RecordingHandle],
    lk_api: api.LiveKitAPI,
) -> str:
    """Stop an active egress and return the final S3 URL.  Returns '' on failure."""
    if not handle or not handle.active:
        return ""

    try:
        info = await lk_api.egress.stop_egress(
            egress_proto.StopEgressRequest(egress_id=handle.egress_id)
        )
        handle.active = False

        file_results = list(info.file_results or [])
        if file_results:
            location = file_results[0].location
            handle.audio_url = location
            logger.info(f"Recording stopped — url={location}")
            return location

        logger.info(f"Recording stopped — egress_id={handle.egress_id} (no file result yet)")
        return ""
    except Exception as e:
        logger.warning(f"Failed to stop recording egress {handle.egress_id}: {e}")
        handle.active = False
        return ""
