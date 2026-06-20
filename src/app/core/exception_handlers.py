from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.app.core.exceptions import (
    InvalidTokenError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    SlugNotFoundError,
    SlugAlreadyExistsError,
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
