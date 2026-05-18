from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Signal(TimestampMixin, Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_news_id: Mapped[int] = mapped_column(ForeignKey("raw_news.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    importance_score: Mapped[int] = mapped_column(Integer, index=True)
    opportunity_score: Mapped[int] = mapped_column(Integer, default=0)
    trend_velocity: Mapped[float] = mapped_column(Float, default=0.0)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    source_credibility: Mapped[float] = mapped_column(Float, default=0.0)
    freshness_score: Mapped[float] = mapped_column(Float, default=0.0)
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)
    ranking_factors: Mapped[dict] = mapped_column(JSON, default=dict)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    action_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    raw_news = relationship("RawNews", back_populates="signals")
    user = relationship("User", back_populates="signals")
    summary = relationship("Summary", back_populates="signal", uselist=False, cascade="all, delete-orphan")

