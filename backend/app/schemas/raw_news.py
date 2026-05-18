from datetime import datetime

from app.schemas.common import ORMBase


class RawNewsResponse(ORMBase):
    id: int
    source: str
    title: str
    link: str
    published_at: datetime | None
    engagement_score: float
    tags: list[str]
    summary_snippet: str | None

