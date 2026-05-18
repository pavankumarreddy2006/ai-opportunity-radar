from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.signal import Signal
from app.models.user import User
from app.scraper.github_scraper import GitHubScraper
from app.scraper.hackernews_scraper import HackerNewsScraper
from app.scraper.reddit_scraper import RedditScraper
from app.scraper.rss_scraper import RssScraper
from app.scraper.tech_blog_scraper import TechBlogScraper
from app.scraper.youtube_scraper import YouTubeScraper
from app.services.dedupe_service import DedupeService
from app.services.ranking_service import RankingService
from app.services.summarization_service import SummarizationService

logger = get_logger(__name__)


class NewsPipelineService:
    def __init__(self) -> None:
        self.scrapers = [
            RedditScraper(),
            GitHubScraper(),
            RssScraper(),
            HackerNewsScraper(),
            YouTubeScraper(),
            TechBlogScraper(),
        ]
        self.ranking_service = RankingService()
        self.summarization_service = SummarizationService()

    def run(self, db: Session) -> dict[str, int | str]:
        collected = []
        for scraper in self.scrapers:
            try:
                fetched = scraper.collect()
                logger.info("Fetched %s items from %s", len(fetched), scraper.source_name)
                collected.extend(fetched)
            except Exception as exc:
                logger.warning("Collector failed for %s: %s", scraper.source_name, exc)

        changed_raw = DedupeService.persist_items(db, collected)

        users = list(db.scalars(select(User).options(joinedload(User.interests))).unique())
        signals = self.ranking_service.rank_for_user(db, None, changed_raw)
        for user in users:
            signals.extend(self.ranking_service.rank_for_user(db, user, changed_raw))

        signal_ids = [signal.id for signal in signals]
        hydrated_signals = []
        if signal_ids:
            hydrated_signals = list(
                db.scalars(
                    select(Signal)
                    .options(joinedload(Signal.raw_news), joinedload(Signal.summary))
                    .where(Signal.id.in_(signal_ids))
                ).unique()
            )
        summaries = self.summarization_service.generate_for_signals(db, hydrated_signals)
        status = "ok" if collected else "degraded"

        return {
            "inserted_raw_items": len(changed_raw),
            "generated_signals": len(signals),
            "generated_summaries": len(summaries),
            "status": status,
        }


def run_news_update() -> dict[str, int | str]:
    db = SessionLocal()
    try:
        return NewsPipelineService().run(db)
    finally:
        db.close()
