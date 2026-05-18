from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.core.settings import get_settings
from app.db.session import SessionLocal
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    database_status = "ok"
    try:
        with SessionLocal() as db:
            db.execute(text("select 1"))
    except Exception:
        database_status = "degraded"
    return HealthResponse(
        status="ok",
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc),
        database=database_status,
    )
