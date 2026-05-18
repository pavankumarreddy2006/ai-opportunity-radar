from types import SimpleNamespace

from app.services.ranking_service import RankingService
from app.services.summarization_service import SummarizationService


def test_ranking_engagement_uses_source_specific_scale() -> None:
    service = RankingService()

    github_raw = SimpleNamespace(source="github", engagement_score=2500)
    reddit_raw = SimpleNamespace(source="reddit", engagement_score=500)

    assert service._engagement(github_raw) == 0.5
    assert service._engagement(reddit_raw) == 0.5


def test_summary_normalization_preserves_required_dashboard_fields() -> None:
    raw = SimpleNamespace(
        title="OpenAI releases a new model",
        source="openai",
        summary_snippet="OpenAI announced a new model for developers.",
    )
    signal = SimpleNamespace(
        raw_news=raw,
        category="Model Releases",
        importance_score=82,
        opportunity_score=8,
    )

    payload = SummarizationService()._normalize_payload(
        {
            "headline": "  OpenAI releases a new model  ",
            "what_happened": "A new model shipped.",
            "why_it_matters": "It may change developer workflows.",
            "why_you_should_care": "Builders should evaluate it.",
            "action_recommendation": "Test it on one workflow.",
            "opportunity_score": 99,
        },
        signal,
    )

    assert payload["headline"] == "OpenAI releases a new model"
    assert payload["opportunity_score"] == 10
    assert set(payload) == {
        "headline",
        "what_happened",
        "why_it_matters",
        "why_you_should_care",
        "action_recommendation",
        "opportunity_score",
    }
