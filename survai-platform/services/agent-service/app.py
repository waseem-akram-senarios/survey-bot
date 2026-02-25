"""
Agent Service -- Port 8050
Handles transcript retrieval and email fallback.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.agent import router as agent_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Agent Service starting up...")
    yield
    logger.info("Agent Service shutting down...")


app = FastAPI(
    title="Agent Service",
    description="Agent service -- transcripts, email fallback",
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

app.include_router(agent_router)


@app.get("/")
async def root():
    return {"service": "agent-service", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "OK", "service": "agent-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8050)
