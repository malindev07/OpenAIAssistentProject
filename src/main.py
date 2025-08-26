import os

import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from dotenv import load_dotenv

from config.config import settings
from src.api.health.handlers import health_router
from src.domain.logger.logger import setup_logging, get_logger

load_dotenv()

setup_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("app start")
        yield
    finally:
        logger.info("app ended")


app = FastAPI(lifespan=lifespan, version=settings.app_version, title=settings.app_name)
app.include_router(health_router)


@app.middleware("http")
async def log_info(request: Request, call_next):
    api_logger = get_logger("src.api")

    response = await call_next(request)

    api_logger.info(
        f"Response: {response.status_code} for {request.method} {request.url.path}"
    )
    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
