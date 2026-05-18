from collections.abc import Iterable
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from app.core.logging import get_logger
from app.scraper.base import BaseScraper, ScrapedItem
from app.scraper.utils import parse_int, resilient_get

logger = get_logger(__name__)


class GitHubScraper(BaseScraper):
    source_name = "github"
    trending_urls = [
        "https://github.com/trending/python?since=daily",
        "https://github.com/trending/typescript?since=daily",
        "https://github.com/trending?since=daily",
    ]

    def fetch(self) -> Iterable[ScrapedItem]:
        items: list[ScrapedItem] = []
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            for trending_url in self.trending_urls:
                try:
                    response = resilient_get(client, trending_url)
                except Exception as exc:
                    logger.warning("GitHub trending fetch failed for %s: %s", trending_url, exc)
                    continue
                items.extend(self._parse_trending_page(response.text))
        return items

    def _parse_trending_page(self, html: str) -> list[ScrapedItem]:
        soup = BeautifulSoup(html, "html.parser")
        items: list[ScrapedItem] = []
        for article in soup.select("article.Box-row"):
            title_node = article.select_one("h2 a")
            description = article.select_one("p")
            star_node = article.select_one("a[href$='/stargazers']")
            trend_node = article.select_one("span.d-inline-block.float-sm-right")

            if not title_node:
                continue

            repo_path = " ".join(title_node.get_text(" ", strip=True).split())
            repo_url = f"https://github.com{title_node.get('href', '').strip()}"
            stars = float(parse_int(star_node.get_text(strip=True) if star_node else "0"))

            tags = ["open-source", "github-trending"]
            if description:
                tags.extend([word.lower() for word in description.get_text(strip=True).split()[:3]])

            items.append(
                ScrapedItem(
                    title=f"{repo_path} is trending on GitHub",
                    source=self.source_name,
                    link=repo_url,
                    published_at=datetime.now(timezone.utc),
                    engagement_score=stars,
                    tags=tags,
                    summary_snippet=description.get_text(" ", strip=True)[:280] if description else None,
                    raw_payload={"trend_text": trend_node.get_text(" ", strip=True) if trend_node else None},
                    credibility_score=0.9,
                    mention_count=int(stars // 100),
                )
            )
        return items
