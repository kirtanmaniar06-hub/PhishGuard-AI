"""
PhishGuard AI — HTTP Request Logging Middleware

Captures performance metrics, status codes, and client details for
each incoming request, funneling reports to structured Loguru sinks.
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Intercepts and logs duration/errors of all HTTP transactions."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            duration = (time.perf_counter() - start_time) * 1000
            
            # Formulate structured message
            log_msg = (
                f"{client_ip} | '{method} {path}' | "
                f"Status: {response.status_code} | Duration: {duration:.2f}ms"
            )
            
            if response.status_code >= 400:
                logger.warning(log_msg)
            else:
                logger.info(log_msg)

            return response
        except Exception as err:
            duration = (time.perf_counter() - start_time) * 1000
            logger.exception(
                f"{client_ip} | '{method} {path}' | "
                f"Failed after {duration:.2f}ms | Error: {err}"
            )
            raise err
