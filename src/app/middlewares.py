from time import perf_counter
from typing import Callable
from uuid import uuid4

from fastapi import FastAPI, Request

from src.app.core.logging import get_logger, request_id_var


def register_middlewares(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_request_id(request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        client_ip = request.client.host if request.client else None

        token = request_id_var.set(request_id)

        logger = get_logger("http")
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
        )

        start_time = perf_counter()

        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)

        duration_ms = round((perf_counter() - start_time) * 1000, 2)
        logger.info(
            "Request finished",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        return response
