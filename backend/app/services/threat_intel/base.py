"""
PhishGuard AI — Threat Intelligence Base Service Interface

Defines the abstract base class and contract that all threat intelligence
providers must satisfy, including resilient request handling with retries
and centralized utility functions.
"""

import asyncio
from abc import ABC, abstractmethod
import logging
import socket
from typing import Any, Type
from urllib.parse import urlparse
import httpx
from pydantic import BaseModel
from app.core.config import settings

logger = logging.getLogger("phishguard")


class BaseThreatIntelService(ABC):
    """Abstract base class establishing the interface for Threat Intelligence providers."""

    def __init__(self, api_key: str):
        """
        Initialize the threat intelligence service with its API key.
        """
        self.api_key = api_key.strip() if api_key else ""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the lower-case unique name of the threat intelligence provider."""
        pass

    @property
    @abstractmethod
    def response_schema(self) -> Type[BaseModel]:
        """Return the Pydantic schema class associated with this provider's report."""
        pass

    def is_configured(self) -> bool:
        """
        Verify if the service is properly configured with an API key.
        """
        return bool(self.api_key)

    @abstractmethod
    async def scan_url(self, client: httpx.AsyncClient, url: str) -> BaseModel:
        """
        Query the threat intelligence provider for reputation/maliciousness of a URL.
        """
        pass

    @abstractmethod
    async def scan_ip(self, client: httpx.AsyncClient, ip: str) -> BaseModel:
        """
        Query the threat intelligence provider for reputation/maliciousness of an IP address.
        """
        pass

    def _extract_domain(self, target: str) -> str:
        """Extract domain hostname from a target URL (shared utility)."""
        if not target:
            return ""
        try:
            if "://" not in target:
                parsed = urlparse(f"http://{target}")
            else:
                parsed = urlparse(target)
            domain = parsed.netloc or parsed.path.split("/")[0]
            if ":" in domain:
                domain = domain.split(":")[0]
            return domain
        except Exception:
            return target

    def _resolve_ip(self, domain: str) -> str:
        """Resolve a domain hostname to its IPv4 address via DNS lookup (shared utility)."""
        if not domain:
            return ""
        try:
            return socket.gethostbyname(domain)
        except socket.gaierror:
            return ""

    def _check_status(self, response: httpx.Response) -> None:
        """Central check for response success to raise appropriate HTTP errors."""
        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                f"Provider {self.provider_name} returned status HTTP {response.status_code}",
                request=response.request,
                response=response,
            )

    async def _request_with_retry(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Execute an HTTP request with exponential backoff on transient errors (429, 5xx)
        and connection/timeout failures.
        """
        retries = 0
        delay = 1.0
        while True:
            try:
                response = await client.request(
                    method,
                    url,
                    timeout=settings.THREAT_INTEL_TIMEOUT_SECONDS,
                    **kwargs
                )
                if response.status_code == 429 or 500 <= response.status_code < 600:
                    if retries >= max_retries:
                        logger.error(
                            f"Max retries reached for {self.provider_name} (HTTP {response.status_code})."
                        )
                        return response
                    logger.warning(
                        f"Provider {self.provider_name} returned status {response.status_code}. "
                        f"Retrying request to {url} in {delay:.2f}s..."
                    )
                else:
                    return response
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if retries >= max_retries:
                    logger.error(
                        f"Max retries reached for {self.provider_name} due to network/timeout exception: {exc}."
                    )
                    raise exc
                logger.warning(
                    f"Transient network exception querying {self.provider_name}: {exc}. "
                    f"Retrying request to {url} in {delay:.2f}s..."
                )

            await asyncio.sleep(delay)
            retries += 1
            delay *= backoff_factor
