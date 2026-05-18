from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Summary(TimestampMixin, Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    signal_id: Mapped[int | None] = mapped_column(
        ForeignKey("signals.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
        index=True,
    )
    news_id: Mapped[int | None] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"), nullable=True, index=True)
    headline: Mapped[str] = mapped_column(Text)
    what_happened: Mapped[str] = mapped_column(Text)
    why_it_matters: Mapped[str] = mapped_column(Text)
    why_you_should_care: Mapped[str] = mapped_column(Text)
    action_recommendation: Mapped[str] = mapped_column(Text)
    opportunity_score: Mapped[int] = mapped_column(Integer, default=0)

    signal = relationship("Signal", back_populates="summary")
    news = relationship("News", back_populates="summaries")
