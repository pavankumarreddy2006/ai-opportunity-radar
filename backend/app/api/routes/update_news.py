from threading import Thread

from fastapi import APIRouter, Header, HTTPException

from app.core.logging import get_logger
from app.core.settings import get_settings
from app.db.session import SessionLocal
from app.schemas.signal import UpdateResponse
from app.services.news_pipeline import NewsPipelineService

router = APIRouter()
logger = get_logger(__name__)


def _run_update_in_background() -> None:
    db = SessionLocal()
    try:
        result = NewsPipelineService().run(db)
        logger.info("Background news update completed: %s", result)
    except Exception as exc:
        logger.exception("Background news update failed: %s", exc)
    finally:
        db.close()


def _authorize_update(x_update_token: str | None) -> None:
    token = get_settings().update_news_token
    if token and x_update_token != token:
        raise HTTPException(status_code=403, detail="Invalid update token")


@router.post("", response_model=UpdateResponse)
def update_news(x_update_token: str | None = Header(default=None)) -> UpdateResponse:
    _authorize_update(x_update_token)
    try:
        Thread(target=_run_update_in_background, daemon=True).start()
        return UpdateResponse(
            inserted_raw_items=0,
            generated_signals=0,
            generated_summaries=0,
            status="queued",
        )
    except Exception as exc:
        logger.exception("News update could not be queued; returning degraded update response: %s", exc)
        return UpdateResponse(
            inserted_raw_items=0,
            generated_signals=0,
            generated_summaries=0,
            status="degraded",
        )


@router.get("", response_model=UpdateResponse)
def update_news_get(x_update_token: str | None = Header(default=None)) -> UpdateResponse:
    return update_news(x_update_token)
