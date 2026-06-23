from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded

from src.app.core.exceptions import (
    InvalidTokenError,
    InvalidCredentialsError,
    PermissionDeniedError,
    UserAlreadyExistsError,
    SlugNotFoundError,
    SlugAlreadyExistsError,
    UserNotFoundError,
)


def register_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidTokenError)
    async def invalid_token_handler(
        request: Request, exc: InvalidTokenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc) or "Invalid token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(
        request: Request, exc: UserAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(SlugNotFoundError)
    async def slug_not_found_handler(
        request: Request, exc: SlugNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(SlugAlreadyExistsError)
    async def slug_already_exists_handler(
        request: Request, exc: SlugAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(
        request: Request, exc: PermissionDeniedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)}
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(
        request: Request, exc: UserNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limited_handler(
        request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        retry_after = getattr(exc, "retry_after", 60)
        limit = getattr(exc, "limit", "unknown")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Toomany requests, try later", "limit": f"{limit}"},
            headers={"Retry-After": f"{retry_after}"},
        )
