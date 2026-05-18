from threading import Thread

from fastapi import APIRouter

from app.core.logging import get_logger
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


@router.post("", response_model=UpdateResponse)
def update_news() -> UpdateResponse:
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
def update_news_get() -> UpdateResponse:
    return update_news()
