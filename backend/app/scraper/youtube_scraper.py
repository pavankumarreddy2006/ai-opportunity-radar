from collections.abc import Iterable

import feedparser
import httpx
from dateutil import parser

from app.core.logging import get_logger
from app.core.settings import get_settings
from app.scraper.base import BaseScraper, ScrapedItem
from app.scraper.utils import resilient_get

logger = get_logger(__name__)


class YouTubeScraper(BaseScraper):
    source_name = "youtube"

    def fetch(self) -> Iterable[ScrapedItem]:
        settings = get_settings()
        items: list[ScrapedItem] = []
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            for feed_url in settings.youtube_feed_list:
                try:
                    feed = feedparser.parse(resilient_get(client, feed_url).text)
                except Exception as exc:
                    logger.warning("YouTube feed fetch failed for %s: %s", feed_url, exc)
                    continue
                feed_title = getattr(feed.feed, "title", "youtube")
                for entry in feed.entries[:8]:
                    try:
                        published = parser.parse(entry.published) if getattr(entry, "published", None) else None
                    except (TypeError, ValueError):
                        published = None
                    title = getattr(entry, "title", "")
                    link = getattr(entry, "link", "")
                    if not title or not link:
                        continue
                    items.append(
                        ScrapedItem(
                            title=title,
                            source=self.source_name,
                            link=link,
                            published_at=published,
                            engagement_score=15.0,
                            tags=["youtube", feed_title.lower().replace(" ", "-")],
                            summary_snippet=getattr(entry, "summary", "")[:280] or None,
                            raw_payload={"channel": feed_title},
                            credibility_score=0.7,
                            mention_count=2,
                        )
                    )
        return items
