from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.settings import get_settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", environment=settings.app_env, timestamp=datetime.now(timezone.utc))

