from fastapi import FastAPI

from src.app.core.exception_handlers import register_handlers
from src.app.core.lifespan import lifespan
from src.app.core.logging import setup_logging

from src.app.api.routers import health
from src.app.api.routers import auth
from src.app.api.routers import url

setup_logging("INFO")


app = FastAPI(title="Short Url", lifespan=lifespan)
register_handlers(app)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(url.router)
