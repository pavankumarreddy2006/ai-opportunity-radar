from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.raw_news import RawNews
from app.scraper.base import ScrapedItem
from app.scraper.utils import build_dedupe_key, normalize_url, tokenize


def _title_similarity(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    overlap = len(left_tokens.intersection(right_tokens)) / len(left_tokens.union(right_tokens))
    sequence = SequenceMatcher(None, left.lower(), right.lower()).ratio()
    return max(overlap, sequence)


class DedupeService:
    @staticmethod
    def persist_items(db: Session, items: list[ScrapedItem]) -> list[RawNews]:
        changed: list[RawNews] = []
        pending_by_dedupe_key: dict[str, RawNews] = {}
        changed_ids: set[int] = set()

        for item in items:
            dedupe_key = build_dedupe_key(item.title, item.link)
            pending = pending_by_dedupe_key.get(dedupe_key)
            if pending:
                DedupeService._merge_item(pending, item)
                continue

            existing = db.scalar(select(RawNews).where(RawNews.dedupe_key == dedupe_key))
            if not existing:
                existing = DedupeService._find_similar_existing(db, item)
            if existing:
                DedupeService._merge_item(existing, item)
                if existing.id and existing.id not in changed_ids:
                    changed.append(existing)
                    changed_ids.add(existing.id)
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
            changed.append(model)
            pending_by_dedupe_key[dedupe_key] = model

        db.commit()
        for record in changed:
            db.refresh(record)
        return changed

    @staticmethod
    def _merge_item(existing: RawNews, item: ScrapedItem) -> None:
        existing.mention_count = max(existing.mention_count, item.mention_count)
        existing.engagement_score = max(existing.engagement_score, item.engagement_score)
        existing.credibility_score = max(existing.credibility_score, item.credibility_score)
        existing.tags = sorted(set([*existing.tags, *item.tags]))
        existing.raw_payload = {
            **(existing.raw_payload or {}),
            "merged_sources": sorted(
                set(
                    [
                        *((existing.raw_payload or {}).get("merged_sources") or []),
                        existing.source,
                        item.source,
                    ]
                )
            ),
            "duplicate_links": sorted(
                set(
                    [
                        *((existing.raw_payload or {}).get("duplicate_links") or []),
                        normalize_url(existing.link),
                        normalize_url(item.link),
                    ]
                )
            ),
        }

    @staticmethod
    def _find_similar_existing(db: Session, item: ScrapedItem) -> RawNews | None:
        candidates = list(
            db.scalars(
                select(RawNews)
                .where(RawNews.source != item.source)
                .order_by(RawNews.created_at.desc())
                .limit(100)
            )
        )
        for candidate in candidates:
            if normalize_url(candidate.link) == normalize_url(item.link):
                return candidate
            if _title_similarity(candidate.title, item.title) >= 0.86:
                return candidate
        return None
