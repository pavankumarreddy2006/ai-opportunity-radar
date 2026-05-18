from collections.abc import Iterable

from app.scraper.base import BaseScraper, ScrapedItem


class FakeScraper(BaseScraper):
    source_name = "fake"

    def fetch(self) -> Iterable[ScrapedItem]:
        return [
            ScrapedItem(
                title="OpenAI releases a new GPT model",
                source="fake",
                link="https://example.com/story?utm_source=test#section",
                published_at=None,
                engagement_score=10,
                tags=["AI", "Models"],
            ),
            ScrapedItem(
                title="OpenAI releases a new GPT model",
                source="fake",
                link="https://example.com/story",
                published_at=None,
                engagement_score=5,
                tags=["ai"],
            ),
            ScrapedItem(
                title="Local restaurant opens downtown",
                source="fake",
                link="https://example.com/food",
                published_at=None,
                engagement_score=100,
                tags=["food"],
            ),
        ]


def test_collect_normalizes_dedupes_and_filters_non_ai_items() -> None:
    items = FakeScraper().collect()

    assert len(items) == 1
    assert items[0].title == "OpenAI releases a new GPT model"
    assert items[0].link == "https://example.com/story"
    assert items[0].tags == ["ai", "models"]
