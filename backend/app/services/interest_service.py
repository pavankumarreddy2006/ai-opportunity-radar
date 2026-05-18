from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.interest import Interest
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.interest import PreferenceUpdateRequest


class InterestService:
    @staticmethod
    def upsert_preferences(db: Session, payload: PreferenceUpdateRequest) -> User:
        user = db.scalar(
            select(User).options(selectinload(User.interests)).where(User.email == payload.email.lower())
        )

        if not user:
            user = User(email=payload.email.lower(), name=payload.name)
            db.add(user)
            db.flush()
            user.preference = UserPreference()
        else:
            user.name = payload.name
            if not user.preference:
                user.preference = UserPreference()

        user.interests.clear()
        cleaned_interests = sorted({item.strip().lower() for item in payload.interests if item.strip()})
        for name in cleaned_interests:
            user.interests.append(Interest(name=name))

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        return db.scalar(select(User).options(selectinload(User.interests)).where(User.email == email.lower()))
