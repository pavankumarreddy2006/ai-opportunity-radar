from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.interest import PreferenceResponse, PreferenceUpdateRequest
from app.services.interest_service import InterestService

router = APIRouter()


@router.get("", response_model=PreferenceResponse)
def get_preferences(email: str, db: Session = Depends(get_db)) -> PreferenceResponse:
    try:
        user = InterestService.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User preferences not found")
        return PreferenceResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to retrieve preferences") from exc


@router.post("", response_model=PreferenceResponse)
def upsert_preferences(payload: PreferenceUpdateRequest, db: Session = Depends(get_db)) -> PreferenceResponse:
    try:
        if not payload.email or not payload.email.strip():
            raise HTTPException(status_code=400, detail="Email is required")
        user = InterestService.upsert_preferences(db, payload)
        return PreferenceResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to save preferences") from exc

