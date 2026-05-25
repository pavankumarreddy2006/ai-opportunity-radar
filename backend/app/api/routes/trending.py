from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.signal import SignalResponse, TrendingGroup
from app.services.fallback_data import fallback_trending
from app.services.ranking_service import RankingService
from app.services.signal_serializer import to_signal_response

router = APIRouter()
logger = get_logger(__name__)


@router.get("", response_model=list[TrendingGroup])
def get_trending(db: Session = Depends(get_db)) -> list[TrendingGroup]:
    try:
        grouped = RankingService.grouped_trending(db)
        response = [
            TrendingGroup(section=section, signals=[to_signal_response(signal) for signal in signals])
            for section, signals in grouped.items()
        ]
        if not response or not any(group.signals for group in response):
            return fallback_trending()
        return response
    except Exception as exc:
        logger.exception("Failed to load trending groups; returning fallback groups: %s", exc)
        try:
            return fallback_trending()
        except Exception as fallback_err:
            logger.error("Fallback trending also failed: %s", fallback_err)
            return []
