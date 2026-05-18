from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.router import api_router
from app.core.logging import configure_logging, get_logger
from app.core.settings import get_settings

configure_logging()
logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def _build_dashboard_context() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "service_name": "AI News Collector API",
        "service_status": "ONLINE",
        "api_health": "Checking",
        "total_news_count": "Loading",
        "trending_topics_count": "Loading",
        "last_update_time": now,
        "top_news": [],
        "trending_topics": [],
        "latest_updates": [
            "Root dashboard is live with Jinja2 templates.",
            "API routes remain available for automation and integrations.",
            "Swagger documentation is available at /docs.",
        ],
        "endpoints": [
            {"label": "Health Check", "path": "/health", "description": "Runtime status and environment metadata."},
            {"label": "News Feed", "path": "/news", "description": "Ranked AI news signals."},
            {"label": "Top 5 AI News", "path": "/top5", "description": "Highest-priority AI updates."},
            {"label": "Trending Topics", "path": "/trending", "description": "Signals grouped by trend section."},
            {"label": "Dashboard API", "path": "/dashboard", "description": "Combined API payload for dashboard clients."},
            {"label": "Weekly Report", "path": "/weekly-report", "description": "Executive weekly summary payload."},
        ],
    }


@app.get("/", response_model=None)
def root(request: Request):
    return templates.TemplateResponse(request, "index.html", _build_dashboard_context())


app.include_router(api_router)
