import json
import re

from sqlalchemy.orm import Session

from openai import OpenAI

from app.ai.client import get_openai_client, get_openrouter_client
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
        clients = [client for client in [get_openai_client(), get_openrouter_client()] if client]
        if not clients:
            return self._fallback_summary(signal)

        settings = get_settings()
        user_prompt = {
            "title": signal.raw_news.title,
            "source": signal.raw_news.source,
            "tags": signal.raw_news.tags,
            "snippet": signal.raw_news.summary_snippet,
            "importance_score": signal.importance_score,
            "ranking_factors": signal.ranking_factors,
            "category": signal.category,
        }
        last_error: Exception | None = None
        for client in clients:
            try:
                return self._ask_model(client, settings.openai_model, user_prompt, signal)
            except Exception as exc:
                last_error = exc
                logger.warning("AI summary provider failed for signal %s: %s", signal.id, exc)

        logger.warning("Falling back to local summary for signal %s after provider errors: %s", signal.id, last_error)
        return self._fallback_summary(signal)

    def _ask_model(self, client: OpenAI, model: str, user_prompt: dict, signal: Signal) -> dict:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_prompt)},
            ],
        )
        text = response.choices[0].message.content
        return self._normalize_payload(self._parse_json(text), signal)

    def _parse_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))

    def _normalize_payload(self, payload: dict, signal: Signal) -> dict:
        fallback = self._fallback_summary(signal)
        normalized = {**fallback, **{key: value for key, value in payload.items() if value}}
        normalized["opportunity_score"] = max(1, min(10, int(normalized["opportunity_score"])))
        for key in [
            "headline",
            "what_happened",
            "why_it_matters",
            "why_you_should_care",
            "action_recommendation",
        ]:
            normalized[key] = str(normalized[key]).strip()
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
