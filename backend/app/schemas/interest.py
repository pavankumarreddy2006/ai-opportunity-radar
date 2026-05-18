from pydantic import BaseModel

from app.schemas.common import ORMBase


class InterestItem(BaseModel):
    name: str


class PreferenceUpdateRequest(BaseModel):
    email: str
    name: str | None = None
    interests: list[str]


class PreferenceResponse(ORMBase):
    id: int
    email: str
    name: str | None
    interests: list[InterestItem]

