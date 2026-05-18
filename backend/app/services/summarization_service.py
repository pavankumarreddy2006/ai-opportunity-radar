import json

from sqlalchemy.orm import Session

from app.ai.client import get_ai_client
from app.ai.prompts import SUMMARY_SYSTEM_PROMPT
from app.core.logging import get_logger
from app.core.settings import get_settings
from app.models.signal import Signal
from app.models.summary import Summary

logger = get_logger(__name__)


class SummarizationService:
    def generate_for_signals(self, db: Session, signals: list[Signal]) -> list[Summary]:
        created: list[Summary] = []
        for signal in signals:
            if signal.summary:
                continue

            payload = self._generate_summary(signal)
            summary = Summary(signal_id=signal.id, **payload)
            signal.action_recommendation = payload["action_recommendation"]
            signal.opportunity_score = payload["opportunity_score"]
            db.add(summary)
            created.append(summary)

        db.commit()
        for summary in created:
            db.refresh(summary)
        return created

    def _generate_summary(self, signal: Signal) -> dict:
        client = get_ai_client()
        if not client:
            return self._fallback_summary(signal)

        settings = get_settings()
        user_prompt = {
            "title": signal.raw_news.title,
            "source": signal.raw_news.source,
            "tags": signal.raw_news.tags,
            "snippet": signal.raw_news.summary_snippet,
            "importance_score": signal.importance_score,
        }
        try:
            response = client.responses.create(
                model=settings.openai_model,
                input=[
                    {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(user_prompt)},
                ],
            )
            text = response.output_text
            return self._normalize_payload(json.loads(text), signal)
        except Exception as exc:
            logger.warning("Falling back to local summary for signal %s: %s", signal.id, exc)
            return self._fallback_summary(signal)

    def _normalize_payload(self, payload: dict, signal: Signal) -> dict:
        fallback = self._fallback_summary(signal)
        normalized = {**fallback, **{key: value for key, value in payload.items() if value}}
        normalized["opportunity_score"] = max(1, min(10, int(normalized["opportunity_score"])))
        return normalized

    def _fallback_summary(self, signal: Signal) -> dict:
        raw = signal.raw_news
        headline = raw.title
        what_happened = raw.summary_snippet or f"{raw.source.title()} surfaced a notable update related to {signal.category}."
        why_it_matters = (
            f"This is scoring {signal.importance_score}/100 because it is fresh, relevant, and showing measurable traction."
        )
        why_you_should_care = (
            f"If you care about {signal.category}, this may affect what to learn, build, invest time in, or monitor next."
        )
        action = (
            "Open the source, validate the details, and decide whether to bookmark, share, build on it, or act today."
        )
        return {
            "headline": headline,
            "what_happened": what_happened[:280],
            "why_it_matters": why_it_matters,
            "why_you_should_care": why_you_should_care,
            "action_recommendation": action,
            "opportunity_score": signal.opportunity_score or min(10, max(1, round(signal.importance_score / 10))),
        }
