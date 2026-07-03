from typing import Callable
from uuid import uuid4

from fastapi import FastAPI, Request

from src.app.core.logging import get_logger


def register_middlewares(app: FastAPI) -> None:

    @app.middleware("http")
    async def add_request_id(request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        client_ip = request.client.host if request.client else None

        logger = get_logger("http").bind(request_id=request_id)

        logger.info("Request started", method=request.method, path=request.url.path)

        request.state.request_id = request_id
        request.state.logger = logger

        response = await call_next(request)

        logger.info(
            "Request finished", status_code=response.status_code, client_ip=client_ip
        )

        return response
