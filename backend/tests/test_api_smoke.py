from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token, decode_access_token
from app.main import app
from app.services.ranking_service import RankingService


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_auth_token_round_trip() -> None:
    token = create_access_token("founder@example.com")
    payload = decode_access_token(token)

    assert payload["sub"] == "founder@example.com"


def test_auth_endpoint_issues_bearer_token() -> None:
    response = client.post("/auth/token", json={"email": "Founder@Example.com"})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert decode_access_token(body["access_token"])["sub"] == "founder@example.com"


def test_ranking_classifier_uses_required_signal_types() -> None:
    signal_type = RankingService()._signal_type(
        {"github", "repo", "stars", "library"},
        "general",
    )

    assert signal_type == "open-source trend"
