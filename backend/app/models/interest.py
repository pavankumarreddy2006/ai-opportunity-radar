from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Interest(TimestampMixin, Base):
    __tablename__ = "interests"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_interest_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)

    user = relationship("User", back_populates="interests")

