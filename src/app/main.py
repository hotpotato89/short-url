from fastapi import FastAPI

from src.app.core.lifespan import lifespan
from src.app.core.logging import setup_logging

from src.app.api.routers import health
from src.app.api.routers import auth

setup_logging("INFO")


app = FastAPI(title="Short Url", lifespan=lifespan)
app.include_router(health.router)
app.include_router(auth.router)
