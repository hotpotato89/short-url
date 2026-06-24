from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from src.app.core.exception_handlers import register_handlers
from src.app.core.lifespan import lifespan
from src.app.core.logging import setup_logging
from src.app.core.limiter import limiter
from src.app.core.settings import settings

from src.app.api.routers import health
from src.app.api.routers import auth
from src.app.api.routers import url

setup_logging(settings.app.log_level)


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

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(url.router)
