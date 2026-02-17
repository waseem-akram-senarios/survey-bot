"""
HTTP client for inter-service communication.
Each service uses this to call other services by name.
"""

import os
import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

# Service registry - maps service names to their base URLs
# In Docker, services resolve by container name; locally, use localhost + port
SERVICE_URLS = {
    "survey-service": os.getenv("SURVEY_SERVICE_URL", "http://survey-service:8020"),
    "question-service": os.getenv("QUESTION_SERVICE_URL", "http://question-service:8030"),
    "template-service": os.getenv("TEMPLATE_SERVICE_URL", "http://template-service:8040"),
    "agent-service": os.getenv("AGENT_SERVICE_URL", "http://agent-service:8050"),
    "analytics-service": os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8060"),
    "scheduler-service": os.getenv("SCHEDULER_SERVICE_URL", "http://scheduler-service:8070"),
}


class ServiceClient:
    """Async HTTP client for calling other microservices."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    def _get_base_url(self, service: str) -> str:
        url = SERVICE_URLS.get(service)
        if not url:
            raise ValueError(f"Unknown service: {service}")
        return url

    async def get(self, service: str, path: str, params: Optional[Dict] = None) -> Any:
        client = await self._get_client()
        url = f"{self._get_base_url(service)}{path}"
        logger.debug(f"GET {url}")
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def post(self, service: str, path: str, json: Optional[Dict] = None) -> Any:
        client = await self._get_client()
        url = f"{self._get_base_url(service)}{path}"
        logger.debug(f"POST {url}")
        resp = await client.post(url, json=json)
        resp.raise_for_status()
        return resp.json()

    async def put(self, service: str, path: str, json: Optional[Dict] = None) -> Any:
        client = await self._get_client()
        url = f"{self._get_base_url(service)}{path}"
        logger.debug(f"PUT {url}")
        resp = await client.put(url, json=json)
        resp.raise_for_status()
        return resp.json()

    async def delete(self, service: str, path: str) -> Any:
        client = await self._get_client()
        url = f"{self._get_base_url(service)}{path}"
        logger.debug(f"DELETE {url}")
        resp = await client.delete(url)
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Singleton instance for use across services
service_client = ServiceClient()
