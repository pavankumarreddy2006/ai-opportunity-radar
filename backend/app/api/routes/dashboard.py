from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.models.user import User
from app.schemas.signal import DashboardResponse, SignalResponse, WeeklyReportResponse
from app.services.fallback_data import fallback_dashboard, fallback_trending, fallback_weekly_report
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


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(email: str | None = None, db: Session = Depends(get_db)) -> DashboardResponse:
    try:
        user: User | None = InterestService.get_user_by_email(db, email) if email else None
        top_signals = RankingService.top_signals(db, user_id=getattr(user, "id", None), limit=5)
        grouped = RankingService.grouped_trending(db)
        if not top_signals:
            return fallback_dashboard()
        return DashboardResponse(
            top_signals=[_to_signal_response(signal) for signal in top_signals],
            trending=[
                {"section": section, "signals": [_to_signal_response(signal) for signal in signals] or fallback_trending()[0].signals}
                for section, signals in grouped.items()
            ],
            interests=[interest.name for interest in user.interests] if user else ["ai", "coding", "startups"],
        )
    except Exception as exc:
        logger.exception("Failed to load dashboard; returning fallback dashboard: %s", exc)
        return fallback_dashboard()


@router.get("/weekly-report", response_model=WeeklyReportResponse)
def weekly_report(email: str | None = None, db: Session = Depends(get_db)) -> WeeklyReportResponse:
    try:
        user: User | None = InterestService.get_user_by_email(db, email) if email else None
        signals = RankingService.top_signals(db, user_id=getattr(user, "id", None), limit=12)
        if not signals:
            return fallback_weekly_report()
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
    except Exception as exc:
        logger.exception("Failed to load weekly report; returning fallback report: %s", exc)
        return fallback_weekly_report()
