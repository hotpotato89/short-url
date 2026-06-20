from fastapi import FastAPI

from src.app.core.lifespan import lifespan


app = FastAPI(title="Short Url", lifespan=lifespan)
