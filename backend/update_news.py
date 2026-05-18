import sys

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.logging import configure_logging, get_logger
from app.db import base as _models  # noqa: F401 - register SQLAlchemy model relationships for cron runs.
from app.services.news_pipeline import run_news_update

configure_logging()
logger = get_logger(__name__)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=20), reraise=True)
def run_with_retries() -> dict[str, int | str]:
    return run_news_update()


if __name__ == "__main__":
    try:
        result = run_with_retries()
        logger.info("Hourly news update completed: %s", result)
    except Exception:
        logger.exception("Hourly news update failed")
        sys.exit(1)
