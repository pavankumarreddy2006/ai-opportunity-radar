from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.signal import UpdateResponse
from app.services.news_pipeline import NewsPipelineService

router = APIRouter()


@router.post("", response_model=UpdateResponse)
def update_news(db: Session = Depends(get_db)) -> UpdateResponse:
    try:
        result = NewsPipelineService().run(db)
        return UpdateResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="News update failed") from exc


@router.get("", response_model=UpdateResponse)
def update_news_get(db: Session = Depends(get_db)) -> UpdateResponse:
    return update_news(db)
