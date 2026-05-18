from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

from app.core.logging import get_logger
from app.scraper.utils import build_dedupe_key, is_ai_related, normalize_url

logger = get_logger(__name__)


@dataclass(slots=True)
class ScrapedItem:
    title: str
    source: str
    link: str
    published_at: datetime | None
    engagement_score: float
    tags: list[str] = field(default_factory=list)
    summary_snippet: str | None = None
    raw_payload: dict = field(default_factory=dict)
    credibility_score: float = 0.5
    mention_count: int = 0


class BaseScraper:
    source_name: str = "unknown"

    def fetch(self) -> Iterable[ScrapedItem]:
        raise NotImplementedError

    def collect(self) -> list[ScrapedItem]:
        items: list[ScrapedItem] = []
        seen: set[str] = set()

        for item in self.fetch():
            cleaned = self._clean_item(item)
            if cleaned is None:
                continue

            dedupe_key = build_dedupe_key(cleaned.title, cleaned.link)
            if dedupe_key in seen:
                continue

            seen.add(dedupe_key)
            items.append(cleaned)

        logger.info("Collector %s returned %s validated items", self.source_name, len(items))
        return items

    def _clean_item(self, item: ScrapedItem) -> ScrapedItem | None:
        title = " ".join((item.title or "").split())
        link = normalize_url(item.link or "")
        snippet = " ".join(item.summary_snippet.split()) if item.summary_snippet else None
        tags = [tag.strip().lower() for tag in item.tags if tag and tag.strip()]

        if not title or not link:
            logger.debug("Dropping invalid %s item with missing title/link", self.source_name)
            return None

        if not link.startswith(("http://", "https://")):
            logger.debug("Dropping invalid %s item with non-http link: %s", self.source_name, link)
            return None

        if not is_ai_related(" ".join([title, snippet or "", " ".join(tags)])):
            logger.debug("Dropping non-AI %s item: %s", self.source_name, title)
            return None

        return ScrapedItem(
            title=title[:500],
            source=item.source or self.source_name,
            link=link,
            published_at=item.published_at,
            engagement_score=max(float(item.engagement_score or 0), 0.0),
            tags=tags[:12],
            summary_snippet=snippet[:500] if snippet else None,
            raw_payload=item.raw_payload or {},
            credibility_score=min(max(float(item.credibility_score or 0.5), 0.0), 1.0),
            mention_count=max(int(item.mention_count or 0), 0),
        )
