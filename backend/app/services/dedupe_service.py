from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.raw_news import RawNews
from app.scraper.base import ScrapedItem
from app.scraper.utils import build_dedupe_key


class DedupeService:
    @staticmethod
    def persist_items(db: Session, items: list[ScrapedItem]) -> list[RawNews]:
        inserted: list[RawNews] = []

        for item in items:
            dedupe_key = build_dedupe_key(item.title, item.link)
            existing = db.scalar(select(RawNews).where(RawNews.dedupe_key == dedupe_key))
            if existing:
                existing.mention_count = max(existing.mention_count, item.mention_count)
                existing.engagement_score = max(existing.engagement_score, item.engagement_score)
                continue

            model = RawNews(
                source=item.source,
                title=item.title,
                link=item.link,
                published_at=item.published_at,
                engagement_score=item.engagement_score,
                tags=item.tags,
                summary_snippet=item.summary_snippet,
                raw_payload=item.raw_payload,
                dedupe_key=dedupe_key,
                credibility_score=item.credibility_score,
                mention_count=item.mention_count,
            )
            db.add(model)
            inserted.append(model)

        db.commit()
        for record in inserted:
            db.refresh(record)
        return inserted

