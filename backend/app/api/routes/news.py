from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.models.user import User
from app.schemas.signal import SignalResponse
from app.services.fallback_data import fallback_signals
from app.services.image_service import category_fallback_image, first_payload_image
from app.services.interest_service import InterestService
from app.services.ranking_service import RankingService

router = APIRouter()
logger = get_logger(__name__)


def _to_signal_response(signal) -> SignalResponse:
    image_url = first_payload_image(signal.raw_news.raw_payload) or category_fallback_image(signal.category)
    return SignalResponse(
        id=signal.id,
        category=signal.category,
        importance_score=signal.importance_score,
        opportunity_score=signal.opportunity_score,
        trend_score=round(signal.trend_velocity * 100),
        action_recommendation=signal.action_recommendation,
        created_at=signal.created_at,
        raw_title=signal.raw_news.title,
        source=signal.raw_news.source,
        link=signal.raw_news.link,
        tags=signal.raw_news.tags,
        published_at=signal.raw_news.published_at,
        image_url=image_url,
        image_alt=f"{signal.category} news image for {signal.raw_news.title}",
        summary=signal.summary,
    )


@router.get("/news", response_model=list[SignalResponse])
def get_news(
    email: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[SignalResponse]:
    try:
        user: User | None = InterestService.get_user_by_email(db, email) if email else None
        signals = RankingService.top_signals(db, user_id=getattr(user, "id", None), limit=limit)
        if not signals:
            return fallback_signals(limit)
        return [_to_signal_response(signal) for signal in signals]
    except Exception as exc:
        logger.exception("Failed to load news; returning fallback signals: %s", exc)
        return fallback_signals(limit)


@router.get("/top5", response_model=list[SignalResponse])
def get_top5(email: str | None = None, db: Session = Depends(get_db)) -> list[SignalResponse]:
    try:
        user: User | None = InterestService.get_user_by_email(db, email) if email else None
        signals = RankingService.top_signals(db, user_id=getattr(user, "id", None), limit=5)
        if not signals:
            return fallback_signals(5)
        return [_to_signal_response(signal) for signal in signals]
    except Exception as exc:
        logger.exception("Failed to load top AI updates; returning fallback signals: %s", exc)
        return fallback_signals(5)
