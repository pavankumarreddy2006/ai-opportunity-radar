from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.settings import get_settings

security = HTTPBearer(auto_error=False)


def create_access_token(subject: str, expires_minutes: int = 60 * 24 * 7) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "aud": "ai-opportunity-radar",
    }
    return jwt.encode(payload, get_settings().secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=["HS256"],
            audience="ai-opportunity-radar",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def get_optional_subject(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str | None:
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    return payload.get("sub")
