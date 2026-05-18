from collections.abc import Iterable
from datetime import datetime, timezone

import httpx

from app.core.logging import get_logger
from app.core.settings import get_settings
from app.scraper.base import BaseScraper, ScrapedItem
from app.scraper.utils import resilient_get

logger = get_logger(__name__)


class RedditScraper(BaseScraper):
    source_name = "reddit"
    subreddits = ["artificial", "machinelearning", "localllama", "openai", "singularity", "mlops", "programming"]

    def fetch(self) -> Iterable[ScrapedItem]:
        settings = get_settings()
        headers = {"User-Agent": settings.reddit_user_agent}
        items: list[ScrapedItem] = []

        with httpx.Client(timeout=20, headers=headers) as client:
            for subreddit in self.subreddits:
                try:
                    response = resilient_get(client, f"https://www.reddit.com/r/{subreddit}/hot.json?limit=15")
                    data = response.json()
                except Exception as exc:
                    logger.warning("Reddit fetch failed for r/%s: %s", subreddit, exc)
                    continue

                for child in data.get("data", {}).get("children", []):
                    payload = child.get("data", {})
                    title = payload.get("title", "")
                    permalink = payload.get("permalink", "")
                    if not title or not permalink:
                        continue
                    tags = [subreddit]
                    flair = payload.get("link_flair_text")
                    if flair:
                        tags.append(flair.lower())

                    items.append(
                        ScrapedItem(
                            title=title,
                            source=self.source_name,
                            link=f"https://www.reddit.com{permalink}",
                            published_at=datetime.fromtimestamp(payload.get("created_utc", 0), tz=timezone.utc),
                            engagement_score=float(payload.get("score", 0) + payload.get("num_comments", 0)),
                            tags=tags,
                            summary_snippet=payload.get("selftext", "")[:280] or None,
                            raw_payload=payload,
                            credibility_score=0.55,
                            mention_count=int(payload.get("num_comments", 0)),
                        )
                    )
        return items
