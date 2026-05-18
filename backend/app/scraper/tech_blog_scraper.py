from collections.abc import Iterable
from datetime import datetime

import feedparser
import httpx
from dateutil import parser

from app.core.logging import get_logger
from app.scraper.base import BaseScraper, ScrapedItem
from app.scraper.utils import resilient_get

logger = get_logger(__name__)


class TechBlogScraper(BaseScraper):
    source_name = "tech-blog"
    feeds = {
        "anthropic": "https://www.anthropic.com/news/rss.xml",
        "deepmind": "https://deepmind.google/discover/blog/rss.xml",
        "hugging-face": "https://huggingface.co/blog/feed.xml",
        "nvidia-ai": "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
        "vercel": "https://vercel.com/atom",
        "render": "https://render.com/blog/rss.xml",
    }

    def fetch(self) -> Iterable[ScrapedItem]:
        items: list[ScrapedItem] = []
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            for label, url in self.feeds.items():
                try:
                    feed = feedparser.parse(resilient_get(client, url).text)
                except Exception as exc:
                    logger.warning("AI blog fetch failed for %s: %s", label, exc)
                    continue
                for entry in feed.entries[:8]:
                    try:
                        published = parser.parse(entry.published) if getattr(entry, "published", None) else datetime.utcnow()
                    except (TypeError, ValueError):
                        published = datetime.utcnow()
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
                            engagement_score=12.0,
                            tags=[label, "tech-blog"],
                            summary_snippet=getattr(entry, "summary", "")[:280] or None,
                            raw_payload={"feed": label},
                            credibility_score=0.84,
                            mention_count=1,
                        )
                    )
        return items
