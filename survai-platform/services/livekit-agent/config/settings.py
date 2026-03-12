"""
Configuration settings for the survey bot.
All environment variables and constants are centralized here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ===========================================
# ORGANIZATION SETTINGS
# ===========================================
# Caller ID / display name: must be "IT Curves" (with s) — normalize if mis-set as "IT Curve"
_def = (os.getenv("ORGANIZATION_NAME") or "IT Curves").strip()
ORGANIZATION_NAME = "IT Curves" if _def == "IT Curve" else (_def or "IT Curves")

# ===========================================
# DEFAULT RIDER (fallback when not found in DB)
# ===========================================
DEFAULT_RIDER = {
    "first_name": "Jason",
    "last_name": "Smith",
    "phone": "unknown",
    "mobility_needs": "Unknown",
    "user_since": "2024"
}

# ===========================================
# AI MODEL SETTINGS
# ===========================================
# Speech-to-Text (Deepgram)
STT_MODEL = os.getenv("STT_MODEL", "nova-3")
STT_LANGUAGE = os.getenv("STT_LANGUAGE", "multi")
STT_DETECT_LANGUAGE = os.getenv("STT_DETECT_LANGUAGE", "false").lower() == "true"
STT_ENDPOINTING_MS = int(os.getenv("STT_ENDPOINTING_MS", "300"))

# Large Language Model (OpenAI)
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_TEMPERATURE_ES = float(os.getenv("LLM_TEMPERATURE_ES", "0.4"))

# Text-to-Speech
TTS_MODEL = os.getenv("TTS_MODEL", "eleven_flash_v2_5")
TTS_MODEL_ES = os.getenv("TTS_MODEL_ES", "eleven_flash_v2_5")
TTS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "cgSgspJ2msm6clMCkdW9")
TTS_VOICE_ID_ES = os.getenv("ELEVENLABS_VOICE_ID_ES", os.getenv("ELEVENLABS_VOICE_ID", "cgSgspJ2msm6clMCkdW9"))

# ===========================================
# SESSION SETTINGS
# ===========================================
PREEMPTIVE_GENERATION = True
RESUME_FALSE_INTERRUPTION = True
FALSE_INTERRUPTION_TIMEOUT = 0.2
MAX_TOOL_STEPS = 15

# VAD tuning for phone calls
# min_silence_duration: 0.35s reduces "stuck waiting" after the caller stops speaking
# min_speech_duration: 0.08s allows short "yes"/"no" to pass through (200ms was too aggressive)
# activation_threshold: 0.3 — lower threshold captures quieter/softer short responses
VAD_MIN_SILENCE_DURATION = float(os.getenv("VAD_MIN_SILENCE_DURATION", "0.35"))
VAD_MIN_SPEECH_DURATION = float(os.getenv("VAD_MIN_SPEECH_DURATION", "0.08"))
VAD_ACTIVATION_THRESHOLD = float(os.getenv("VAD_ACTIVATION_THRESHOLD", "0.3"))

# ===========================================
# FILE/DIRECTORY PATHS
# ===========================================
LOG_DIR = os.getenv("LOG_DIR", "survey_logs")
RESPONSES_DIR = os.getenv("RESPONSES_DIR", "survey_responses")

# ===========================================
# TELEPHONY SETTINGS
# ===========================================
SIP_OUTBOUND_TRUNK_ID = os.getenv("SIP_OUTBOUND_TRUNK_ID", "")

# ===========================================
# CALL RECORDING (LiveKit Egress → S3)
# ===========================================
RECORDING_ENABLED = os.getenv("RECORDING_ENABLED", "false").lower() == "true"
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "")

# ===========================================
# WORKER SETTINGS
# ===========================================
WORKER_INITIALIZE_TIMEOUT = 600.0
JOB_MEMORY_WARN_MB = 1200
JOB_MEMORY_LIMIT_MB = 1500

INACTIVITY_TIMEOUT = int(os.getenv("INACTIVITY_TIMEOUT", "6"))
MAX_INACTIVITY_REPROMPTS = int(os.getenv("MAX_INACTIVITY_REPROMPTS", "2"))

AGENT_NAME = os.getenv("AGENT_NAME", "survey-agent")