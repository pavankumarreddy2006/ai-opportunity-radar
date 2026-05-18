from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.signal import SignalResponse
from app.services.interest_service import InterestService
from app.services.ranking_service import RankingService

router = APIRouter()


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


@router.get("", response_model=list[SignalResponse])
def get_signals(email: str | None = None, limit: int = 5, db: Session = Depends(get_db)) -> list[SignalResponse]:
    user: User | None = InterestService.get_user_by_email(db, email) if email else None
    signals = RankingService.top_signals(db, user_id=getattr(user, "id", None), limit=limit)
    return [_to_signal_response(signal) for signal in signals]

