"""
Analytics Service -- Port 8060
MVP metrics, campaign analytics, AI analysis, export/import.
"""

import sys

sys.path.insert(0, "/app")

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.analytics import router as analytics_router
from routes.export import router as export_router
from routes.import_data import router as import_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Analytics Service starting up...")
    yield
    logger.info("Analytics Service shutting down...")


app = FastAPI(
    title="Analytics Service",
    description="MVP metrics, campaign analytics, AI analysis, export/import",
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

app.include_router(analytics_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(import_router, prefix="/api")


@app.get("/")
async def root():
    return {"service": "analytics-service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "OK", "service": "analytics-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8060)
