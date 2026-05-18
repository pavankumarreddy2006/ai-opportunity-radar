from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.logging import configure_logging, get_logger
from app.core.settings import get_settings

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    logger.info("Starting AI News Collector in %s mode", settings.app_env)
    yield
    logger.info("Shutting down AI News Collector")


app = FastAPI(
    title="AI News Collector API",
    description="AI-powered news intelligence dashboard backend.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_credentials="*" not in get_settings().cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str | list[str]]:
    return {
        "status": "ok",
        "service": "AI News Collector API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": ["/news", "/top5", "/trending", "/dashboard", "/weekly-report"],
    }


app.include_router(api_router)
