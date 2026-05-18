from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.schemas.signal import SignalResponse, TrendingGroup
from app.services.fallback_data import fallback_trending
from app.services.ranking_service import RankingService

router = APIRouter()
logger = get_logger(__name__)


def _to_signal_response(signal) -> SignalResponse:
    return SignalResponse(
        id=signal.id,
        category=signal.category,
        importance_score=signal.importance_score,
        opportunity_score=signal.opportunity_score,
        action_recommendation=signal.action_recommendation,
        created_at=signal.created_at,
        raw_title=signal.raw_news.title,
        source=signal.raw_news.source,
        link=signal.raw_news.link,
        tags=signal.raw_news.tags,
        published_at=signal.raw_news.published_at,
        summary=signal.summary,
    )


@router.get("", response_model=list[TrendingGroup])
def get_trending(db: Session = Depends(get_db)) -> list[TrendingGroup]:
    try:
        grouped = RankingService.grouped_trending(db)
        response = [
            TrendingGroup(section=section, signals=[_to_signal_response(signal) for signal in signals])
            for section, signals in grouped.items()
        ]
        if not response or not any(group.signals for group in response):
            return fallback_trending()
        return response
    except Exception as exc:
        logger.exception("Failed to load trending groups; returning fallback groups: %s", exc)
        return fallback_trending()
