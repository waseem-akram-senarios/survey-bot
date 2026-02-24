FROM python:3.11-slim

WORKDIR /app

# System packages needed for audio processing (silero VAD, PyAV, soundfile)
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    python3-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies before copying code (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories for persistent data (also created via volume mounts at runtime)
RUN mkdir -p survey_logs survey_responses

# Pre-download plugin models (silero VAD weights) so the container starts instantly
RUN python agent.py download-files

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# LiveKit agents HTTP health/metrics endpoint
EXPOSE 8083

CMD ["python", "agent.py", "start"]
