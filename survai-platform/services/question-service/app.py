import sys

sys.path.insert(0, "/app")  # so shared package at /app/shared can be found

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.questions import router as questions_router

app = FastAPI(title="Question Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions_router, prefix="/api", tags=["questions"])


@app.get("/")
async def root():
    return {"service": "question-service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "OK"}
