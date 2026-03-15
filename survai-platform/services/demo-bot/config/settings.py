"""
Configuration settings for the demo bot.
English-only, simplified from livekit-agent config.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ===========================================
# ORGANIZATION SETTINGS
# ===========================================
ORGANIZATION_NAME = (os.getenv("ORGANIZATION_NAME") or "IT Curves").strip() or "IT Curves"

# ===========================================
# AI MODEL SETTINGS
# ===========================================
# Speech-to-Text (Deepgram) — English only
STT_MODEL = os.getenv("STT_MODEL", "nova-3")
STT_ENDPOINTING_MS = int(os.getenv("STT_ENDPOINTING_MS", "300"))

# Large Language Model (OpenAI)
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))

# Text-to-Speech (ElevenLabs) — English only
TTS_MODEL = os.getenv("TTS_MODEL", "eleven_flash_v2_5")
TTS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "cgSgspJ2msm6clMCkdW9")

# ===========================================
# SESSION SETTINGS
# ===========================================
PREEMPTIVE_GENERATION = True
RESUME_FALSE_INTERRUPTION = True
FALSE_INTERRUPTION_TIMEOUT = 0.2
MAX_TOOL_STEPS = 15

# VAD tuning for phone calls
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
# WORKER SETTINGS
# ===========================================
WORKER_INITIALIZE_TIMEOUT = 600.0
JOB_MEMORY_WARN_MB = 1200
JOB_MEMORY_LIMIT_MB = 1500

INACTIVITY_TIMEOUT = int(os.getenv("INACTIVITY_TIMEOUT", "6"))
MAX_INACTIVITY_REPROMPTS = int(os.getenv("MAX_INACTIVITY_REPROMPTS", "2"))

AGENT_NAME = os.getenv("AGENT_NAME_DEMO", "demo-agent")

# ===========================================
# RAFFLE / EXTERNAL SERVICE
# ===========================================
RAFFLE_SERVICE_URL = os.getenv("RAFFLE_SERVICE_URL", "")
