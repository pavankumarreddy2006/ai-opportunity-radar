from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMBase


class SummaryPayload(ORMBase):
    headline: str
    what_happened: str
    why_it_matters: str
    why_you_should_care: str
    action_recommendation: str
    opportunity_score: int


class SignalResponse(ORMBase):
    id: int
    category: str
    importance_score: int
    opportunity_score: int
    trend_score: int
    action_recommendation: str | None
    created_at: datetime
    raw_title: str
    source: str
    link: str
    tags: list[str]
    published_at: datetime | None
    image_url: str | None = None
    image_alt: str | None = None
    summary: SummaryPayload | None


class TrendingGroup(BaseModel):
    section: str
    signals: list[SignalResponse]


class DashboardResponse(BaseModel):
    top_signals: list[SignalResponse]
    trending: list[TrendingGroup]
    interests: list[str]


class WeeklyReportResponse(BaseModel):
    headline: str
    executive_summary: str
    top_categories: list[str]
    signals: list[SignalResponse]


class UpdateResponse(BaseModel):
    inserted_raw_items: int
    generated_signals: int
    generated_summaries: int
    status: str
