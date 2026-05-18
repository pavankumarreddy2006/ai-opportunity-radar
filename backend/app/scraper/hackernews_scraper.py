from collections.abc import Iterable
from datetime import datetime, timezone

import httpx

from app.core.logging import get_logger
from app.scraper.base import BaseScraper, ScrapedItem
from app.scraper.utils import resilient_get

logger = get_logger(__name__)


class HackerNewsScraper(BaseScraper):
    source_name = "hackernews"

    def fetch(self) -> Iterable[ScrapedItem]:
        with httpx.Client(timeout=20) as client:
            story_ids = resilient_get(client, "https://hacker-news.firebaseio.com/v0/topstories.json").json()[:50]
            items: list[ScrapedItem] = []
            for story_id in story_ids:
                try:
                    payload = resilient_get(client, f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json").json()
                except Exception as exc:
                    logger.warning("Hacker News item fetch failed for %s: %s", story_id, exc)
                    continue
                if not payload or payload.get("type") != "story":
                    continue
                title = payload.get("title", "")
                if not title:
                    continue
                items.append(
                    ScrapedItem(
                        title=title,
                        source=self.source_name,
                        link=payload.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        published_at=datetime.fromtimestamp(payload.get("time", 0), tz=timezone.utc),
                        engagement_score=float(payload.get("score", 0) + payload.get("descendants", 0)),
                        tags=["hacker-news", "startup", "coding"],
                        summary_snippet=None,
                        raw_payload=payload,
                        credibility_score=0.86,
                        mention_count=int(payload.get("descendants", 0)),
                    )
                )
        return items
