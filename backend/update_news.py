import sys

from app.core.logging import configure_logging, get_logger
from app.services.news_pipeline import run_news_update

configure_logging()
logger = get_logger(__name__)


if __name__ == "__main__":
    try:
        result = run_news_update()
        logger.info("Hourly news update completed: %s", result)
    except Exception:
        logger.exception("Hourly news update failed")
        sys.exit(1)
