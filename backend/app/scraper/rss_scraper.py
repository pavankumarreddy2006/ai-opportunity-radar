from collections.abc import Iterable
from datetime import datetime

import feedparser
import httpx
from dateutil import parser

from app.core.logging import get_logger
from app.scraper.base import BaseScraper, ScrapedItem
from app.scraper.utils import resilient_get

logger = get_logger(__name__)


class RssScraper(BaseScraper):
    source_name = "rss"
    feeds = {
        "google-ai": "https://blog.google/technology/ai/rss/",
        "hugging-face": "https://huggingface.co/blog/feed.xml",
        "techcrunch": "https://techcrunch.com/feed/",
        "openai-blog": "https://openai.com/news/rss.xml",
        "github-blog": "https://github.blog/feed/",
    }

    def fetch(self) -> Iterable[ScrapedItem]:
        items: list[ScrapedItem] = []
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            for label, url in self.feeds.items():
                try:
                    feed = feedparser.parse(resilient_get(client, url).text)
                except Exception as exc:
                    logger.warning("RSS fetch failed for %s: %s", label, exc)
                    continue
                for entry in feed.entries[:10]:
                    try:
                        published = parser.parse(entry.published) if getattr(entry, "published", None) else datetime.utcnow()
                    except (TypeError, ValueError):
                        published = datetime.utcnow()
                    link = getattr(entry, "link", "")
                    title = getattr(entry, "title", "")
                    if not title or not link:
                        continue
                    tags = [label]
                    tags.extend([tag.term.lower() for tag in getattr(entry, "tags", [])[:4]])
                    items.append(
                        ScrapedItem(
                            title=title,
                            source=self.source_name,
                            link=link,
                            published_at=published,
                            engagement_score=float(len(getattr(entry, "tags", [])) * 5),
                            tags=tags,
                            summary_snippet=getattr(entry, "summary", "")[:280] or None,
                            raw_payload={"feed": label},
                            credibility_score=0.82,
                            mention_count=max(1, len(tags) - 1),
                        )
                    )
        return items
