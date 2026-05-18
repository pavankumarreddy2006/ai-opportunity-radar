from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.signal import UpdateResponse
from app.services.news_pipeline import NewsPipelineService

router = APIRouter()


@router.post("", response_model=UpdateResponse)
def update_news(db: Session = Depends(get_db)) -> UpdateResponse:
    result = NewsPipelineService().run(db)
    return UpdateResponse(**result)
