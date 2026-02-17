"""
Template Service -- Port 8040
Manages templates, template-question associations, and translations.
"""

import sys

sys.path.insert(0, "/app")

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.templates import router as templates_router
from routes.template_questions import router as template_questions_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Template Service starting up...")
    yield
    logger.info("Template Service shutting down...")


app = FastAPI(
    title="Template Service",
    description="Manages templates, template-question associations, and translations",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(template_questions_router, prefix="/api")
app.include_router(templates_router, prefix="/api")


@app.get("/")
async def root():
    return {"service": "template-service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "OK", "service": "template-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8040)
