from fastapi import FastAPI

from src.app.core.lifespan import lifespan
from src.app.core.logging import setup_logging

setup_logging("INFO")


app = FastAPI(title="Short Url", lifespan=lifespan)
