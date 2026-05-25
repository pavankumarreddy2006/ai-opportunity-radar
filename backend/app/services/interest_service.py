from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.interest import Interest
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.interest import InteractionTrackRequest, PreferenceUpdateRequest


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

    @staticmethod
    def track_interaction(db: Session, payload: InteractionTrackRequest) -> None:
        user = InterestService.get_user_by_email(db, payload.email)
        if not user:
            user = User(email=payload.email.lower())
            db.add(user)
            db.flush()

        if not user.preference:
            user.preference = UserPreference()

        interest_weights = dict(user.preference.interest_weights or {})
        source_weights = dict(user.preference.source_weights or {})
        action_key = f"action:{payload.action.strip().lower()}"
        source_weights[action_key] = source_weights.get(action_key, 0) + 1

        if payload.category:
            category_key = payload.category.strip().lower()
            interest_weights[category_key] = interest_weights.get(category_key, 0) + 1

        for topic in payload.topics[:20]:
            key = topic.strip().lower()
            if key:
                interest_weights[key] = interest_weights.get(key, 0) + 1

        if payload.query:
            query_key = f"search:{payload.query.strip().lower()[:80]}"
            source_weights[query_key] = source_weights.get(query_key, 0) + 1

        if payload.reading_seconds > 0:
            source_weights["reading_seconds"] = source_weights.get("reading_seconds", 0) + max(payload.reading_seconds, 0)

        user.preference.interest_weights = interest_weights
        user.preference.source_weights = source_weights
        db.commit()
