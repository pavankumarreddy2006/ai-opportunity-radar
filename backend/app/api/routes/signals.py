from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.signal import SignalResponse
from app.services.interest_service import InterestService
from app.services.ranking_service import RankingService
from app.services.signal_serializer import to_signal_response

router = APIRouter()


@router.get("", response_model=list[SignalResponse])
def get_signals(email: str | None = None, limit: int = 5, db: Session = Depends(get_db)) -> list[SignalResponse]:
    try:
        user: User | None = InterestService.get_user_by_email(db, email) if email else None
        signals = RankingService.top_signals(db, user_id=getattr(user, "id", None), limit=limit)
        if not signals:
            from app.services.fallback_data import fallback_signals
            return fallback_signals(limit)
        return [to_signal_response(signal) for signal in signals]
    except Exception as exc:
        from app.services.fallback_data import fallback_signals
        return fallback_signals(limit)
