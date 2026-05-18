from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.signal import DashboardResponse, SignalResponse, WeeklyReportResponse
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


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(email: str | None = None, db: Session = Depends(get_db)) -> DashboardResponse:
    user: User | None = InterestService.get_user_by_email(db, email) if email else None
    top_signals = RankingService.top_signals(db, user_id=getattr(user, "id", None), limit=5)
    grouped = RankingService.grouped_trending(db)
    return DashboardResponse(
        top_signals=[_to_signal_response(signal) for signal in top_signals],
        trending=[
            {"section": section, "signals": [_to_signal_response(signal) for signal in signals]}
            for section, signals in grouped.items()
        ],
        interests=[interest.name for interest in user.interests] if user else ["ai", "coding", "startups"],
    )


@router.get("/weekly-report", response_model=WeeklyReportResponse)
def weekly_report(email: str | None = None, db: Session = Depends(get_db)) -> WeeklyReportResponse:
    user: User | None = InterestService.get_user_by_email(db, email) if email else None
    signals = RankingService.top_signals(db, user_id=getattr(user, "id", None), limit=12)
    categories = sorted({signal.category for signal in signals})
    return WeeklyReportResponse(
        headline="Your highest-value opportunity signals this week",
        executive_summary=(
            "The radar prioritizes the strongest signals by importance, opportunity, freshness, "
            "engagement, and fit with your saved interests."
        ),
        top_categories=categories,
        signals=[_to_signal_response(signal) for signal in signals],
    )
