from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class News(TimestampMixin, Base):
    __tablename__ = "news"
    __table_args__ = (UniqueConstraint("url", name="uq_news_url"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    source: Mapped[str] = mapped_column(String(120), index=True)
    url: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    importance_score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    category: Mapped[str] = mapped_column(String(100), default="general", index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    source_record = relationship("Source", back_populates="news_items")
    category_record = relationship("Category", back_populates="news_items")
    summaries = relationship("Summary", back_populates="news")
