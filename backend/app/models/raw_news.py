from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class RawNews(TimestampMixin, Base):
    __tablename__ = "raw_news"
    __table_args__ = (UniqueConstraint("dedupe_key", name="uq_raw_news_dedupe_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    link: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    summary_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    dedupe_key: Mapped[str] = mapped_column(String(128), index=True)
    credibility_score: Mapped[float] = mapped_column(Float, default=0.5)
    mention_count: Mapped[int] = mapped_column(Integer, default=0)

    signals = relationship("Signal", back_populates="raw_news")
    trend_scores = relationship("TrendScore", back_populates="raw_news", cascade="all, delete-orphan")
