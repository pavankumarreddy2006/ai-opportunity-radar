from sqlalchemy import Boolean, Float, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Source(TimestampMixin, Base):
    __tablename__ = "sources"
    __table_args__ = (UniqueConstraint("name", name="uq_sources_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    source_type: Mapped[str] = mapped_column(String(60), index=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    credibility_score: Mapped[float] = mapped_column(Float, default=0.5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    news_items = relationship("News", back_populates="source_record")
