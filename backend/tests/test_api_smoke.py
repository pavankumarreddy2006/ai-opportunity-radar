from fastapi.testclient import TestClient

from app.auth.jwt import create_access_token, decode_access_token
from app.main import app
from app.services.ranking_service import RankingService


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AI Opportunity Radar" in response.text
    assert "/docs" in response.text
    assert "/health" in response.text


def test_required_news_endpoints_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/news" in paths
    assert "/top5" in paths
    assert "/trending" in paths
    assert "/update-news" in paths


def test_required_news_endpoints_return_fallback_payloads() -> None:
    for path in ["/news", "/top5", "/trending", "/dashboard", "/weekly-report"]:
        response = client.get(path)

        assert response.status_code == 200
        assert response.json()


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


def test_preferences_interaction_endpoint_accepts_behavior_events() -> None:
    response = client.post(
        "/preferences/interaction",
        json={
            "email": "reader@example.com",
            "signal_id": 9001,
            "action": "save",
            "category": "AI Agents",
            "topics": ["ai agents", "automation"],
            "reading_seconds": 25,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] in {"ok", "degraded"}


def test_ranking_classifier_uses_required_signal_types() -> None:
    signal_type = RankingService()._signal_type(
        {"github", "repo", "stars", "library"},
        "general",
    )

    assert signal_type == "Open Source AI"
