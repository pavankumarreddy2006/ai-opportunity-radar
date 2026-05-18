from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class UserPreference(TimestampMixin, Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    digest_frequency: Mapped[str] = mapped_column(String(40), default="daily")
    minimum_importance_score: Mapped[int] = mapped_column(Integer, default=55)
    minimum_opportunity_score: Mapped[int] = mapped_column(Integer, default=4)
    enable_weekly_report: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_email_digest: Mapped[bool] = mapped_column(Boolean, default=False)
    source_weights: Mapped[dict] = mapped_column(JSON, default=dict)
    interest_weights: Mapped[dict] = mapped_column(JSON, default=dict)
    exploration_rate: Mapped[float] = mapped_column(Float, default=0.15)

    user = relationship("User", back_populates="preference")

