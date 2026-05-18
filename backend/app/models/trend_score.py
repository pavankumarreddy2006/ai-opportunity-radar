from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class TrendScore(TimestampMixin, Base):
    __tablename__ = "trend_scores"
    __table_args__ = (UniqueConstraint("raw_news_id", "scored_at", name="uq_trend_score_raw_news_scored_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_news_id: Mapped[int] = mapped_column(ForeignKey("raw_news.id", ondelete="CASCADE"), index=True)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source: Mapped[str] = mapped_column(String(80), index=True)
    trend_velocity: Mapped[float] = mapped_column(Float, default=0.0)
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)
    freshness_score: Mapped[float] = mapped_column(Float, default=0.0)
    reddit_activity_score: Mapped[float] = mapped_column(Float, default=0.0)
    github_star_score: Mapped[float] = mapped_column(Float, default=0.0)
    credibility_score: Mapped[float] = mapped_column(Float, default=0.0)
    composite_score: Mapped[int] = mapped_column(Integer, default=0)
    factors: Mapped[dict] = mapped_column(JSON, default=dict)

    raw_news = relationship("RawNews", back_populates="trend_scores")

