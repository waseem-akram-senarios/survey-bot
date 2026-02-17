FROM python:3.10-slim

RUN apt-get update && apt-get install -y build-essential python3-dev && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY ["requirements.txt", "requirements.txt"]

RUN uv pip install -r requirements.txt --system --python 3.10

EXPOSE 8081

COPY ["routes", "/app/routes"]

COPY ["*.py", "/app/"]

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081"]