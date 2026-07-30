import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.api.routers import admin, auth, credits, health, url
from src.app.core.exception_handlers import register_handlers
from src.app.core.lifespan import lifespan
from src.app.core.limiter import limiter
from src.app.core.settings import settings
from src.app.middlewares import register_middlewares

logging.getLogger("uvicorn").handlers.clear()
logging.getLogger("uvicorn.access").handlers.clear()
logging.getLogger("uvicorn.error").handlers.clear()
logging.getLogger("aiormq").setLevel(logging.WARNING)
logging.getLogger("aio_pika").setLevel(logging.WARNING)
logging.getLogger("taskiq_aio_pika").setLevel(logging.WARNING)


app = FastAPI(title="Short Url", lifespan=lifespan)
app.state.limiter = limiter
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_methods=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

register_handlers(app)
register_middlewares(app)

app.include_router(health.router)
app.include_router(admin.router)
app.include_router(credits.router)
app.include_router(auth.router)
app.include_router(url.redirect_router)
app.include_router(url.router)
