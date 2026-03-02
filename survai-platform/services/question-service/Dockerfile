FROM python:3.10-slim
RUN apt-get update && apt-get install -y build-essential python3-dev && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY shared /app/shared
RUN cd /app/shared && uv pip install -e . --system --python 3.10
COPY services/question-service/requirements.txt /app/requirements.txt
RUN uv pip install -r /app/requirements.txt --system --python 3.10
COPY services/question-service/ /app/
EXPOSE 8030
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8030", "--timeout-keep-alive", "75"]
