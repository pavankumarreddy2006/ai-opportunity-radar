from pydantic import BaseModel

from app.schemas.common import ORMBase


class InterestItem(BaseModel):
    name: str


class PreferenceUpdateRequest(BaseModel):
    email: str
    name: str | None = None
    interests: list[str]


class InteractionTrackRequest(BaseModel):
    email: str
    signal_id: int
    action: str
    category: str | None = None
    topics: list[str] = []
    query: str | None = None
    reading_seconds: int = 0


class PreferenceResponse(ORMBase):
    id: int
    email: str
    name: str | None
    interests: list[InterestItem]
