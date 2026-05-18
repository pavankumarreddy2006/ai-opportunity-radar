from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.interest import PreferenceResponse, PreferenceUpdateRequest
from app.services.interest_service import InterestService

router = APIRouter()


@router.get("", response_model=PreferenceResponse)
def get_preferences(email: str, db: Session = Depends(get_db)) -> PreferenceResponse:
    user = InterestService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User preferences not found")
    return PreferenceResponse.model_validate(user)


@router.post("", response_model=PreferenceResponse)
def upsert_preferences(payload: PreferenceUpdateRequest, db: Session = Depends(get_db)) -> PreferenceResponse:
    user = InterestService.upsert_preferences(db, payload)
    return PreferenceResponse.model_validate(user)

