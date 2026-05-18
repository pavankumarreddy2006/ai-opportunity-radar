from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends

from app.auth.jwt import create_access_token, get_optional_subject

router = APIRouter()


class TokenRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    email: str | None
    authenticated: bool


@router.post("/token", response_model=TokenResponse)
def create_token(payload: TokenRequest) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(payload.email.lower()))


@router.get("/me", response_model=MeResponse)
def me(subject: str | None = Depends(get_optional_subject)) -> MeResponse:
    return MeResponse(email=subject, authenticated=subject is not None)
