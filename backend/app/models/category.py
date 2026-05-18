from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Category(TimestampMixin, Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("name", name="uq_categories_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    news_items = relationship("News", back_populates="category_record")
