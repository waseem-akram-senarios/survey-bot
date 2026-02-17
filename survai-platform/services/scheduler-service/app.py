"""
Scheduler Service -- Port 8070
APScheduler for delayed calls and recurring campaigns.
"""

import sys

sys.path.insert(0, "/app")

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.scheduler import router as scheduler_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Scheduler Service starting up...")
    from routes.scheduler import get_scheduler
    sched = get_scheduler()
    sched.start()
    yield
    logger.info("Scheduler Service shutting down...")
    sched.shutdown(wait=False)


app = FastAPI(
    title="Scheduler Service",
    description="Schedule delayed calls and recurring campaigns",
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

app.include_router(scheduler_router, prefix="/api")


@app.get("/")
async def root():
    return {"service": "scheduler-service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "OK", "service": "scheduler-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8070)
