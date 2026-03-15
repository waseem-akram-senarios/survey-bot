"""
LiveKit pipeline metrics logger.

Formats and logs every AgentMetrics event emitted by AgentSession so that
latency across each stage (VAD -> EOU -> STT -> LLM -> TTS) is visible in
docker compose logs and per-call log files.

Usage:
    from utils.metrics_logger import log_pipeline_metrics
    session.on("metrics_collected")(lambda ev: log_pipeline_metrics(ev.metrics))
"""

import logging
from typing import Union

from livekit.agents.metrics import (
    STTMetrics,
    LLMMetrics,
    TTSMetrics,
    EOUMetrics,
)

try:
    from livekit.agents.metrics import VADMetrics as _VADMetrics
    _HAS_VAD = True
except ImportError:
    _HAS_VAD = False

logger = logging.getLogger("demo-agent")


def _model_tag(metrics) -> str:
    """Return '[provider/model]' suffix when metadata is available."""
    meta = getattr(metrics, "metadata", None)
    if not meta:
        return ""
    parts = []
    if getattr(meta, "model_provider", None):
        parts.append(meta.model_provider)
    if getattr(meta, "model_name", None):
        parts.append(meta.model_name)
    return f" [{'/'.join(parts)}]" if parts else ""


def log_pipeline_metrics(metrics) -> None:
    """
    Dispatch on metrics type and emit a single INFO line per event.

    Log prefixes allow easy grepping:
      docker logs demo-bot | grep METRICS
      docker logs demo-bot | grep "METRICS:LLM"
    """
    tag = _model_tag(metrics)

    if isinstance(metrics, EOUMetrics):
        logger.info(
            "[METRICS:EOU]%s "
            "eou_delay=%.3fs  transcription_delay=%.3fs  turn_cb_delay=%.3fs",
            tag,
            metrics.end_of_utterance_delay,
            metrics.transcription_delay,
            getattr(metrics, "on_user_turn_completed_delay", 0.0),
        )

    elif isinstance(metrics, STTMetrics):
        logger.info(
            "[METRICS:STT]%s "
            "audio=%.2fs  req_duration=%.3fs  streamed=%s",
            tag,
            metrics.audio_duration,
            metrics.duration,
            metrics.streamed,
        )

    elif isinstance(metrics, LLMMetrics):
        logger.info(
            "[METRICS:LLM]%s "
            "ttft=%.3fs  duration=%.2fs  tokens/s=%.1f  "
            "prompt=%d  cached=%d  completion=%d  total=%d  cancelled=%s",
            tag,
            metrics.ttft,
            metrics.duration,
            metrics.tokens_per_second,
            metrics.prompt_tokens,
            metrics.prompt_cached_tokens,
            metrics.completion_tokens,
            metrics.total_tokens,
            metrics.cancelled,
        )

    elif isinstance(metrics, TTSMetrics):
        logger.info(
            "[METRICS:TTS]%s "
            "ttfb=%.3fs  duration=%.2fs  audio=%.2fs  "
            "chars=%d  streamed=%s  cancelled=%s",
            tag,
            metrics.ttfb,
            metrics.duration,
            metrics.audio_duration,
            metrics.characters_count,
            metrics.streamed,
            metrics.cancelled,
        )

    elif _HAS_VAD and isinstance(metrics, _VADMetrics):
        logger.info(
            "[METRICS:VAD]%s %s",
            tag,
            metrics,
        )

    else:
        logger.info("[METRICS:UNKNOWN] type=%s  data=%s", type(metrics).__name__, metrics)
