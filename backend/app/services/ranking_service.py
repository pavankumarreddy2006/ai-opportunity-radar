from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.raw_news import RawNews
from app.models.signal import Signal
from app.models.summary import Summary
from app.models.trend_score import TrendScore
from app.models.user import User
from app.scraper.utils import tokenize, utc_now

MIN_IMPORTANCE_SCORE = 40

INTEREST_KEYWORDS = {
    "ai": {"ai", "llm", "model", "openai", "agent", "inference"},
    "coding": {"code", "coding", "developer", "programming", "framework", "sdk", "api"},
    "startups": {"startup", "saas", "launch", "founder"},
    "automation": {"automation", "workflow", "agent", "ops"},
    "jobs": {"job", "career", "hiring", "remote"},
    "open-source": {"open-source", "opensource", "github", "repo", "library", "stars"},
    "funding": {"funding", "seed", "series", "venture"},
    "productivity tools": {"tool", "workflow", "productivity", "assistant"},
    "research": {"research", "paper", "benchmark", "eval", "dataset"},
    "infrastructure": {"inference", "gpu", "database", "vector", "deployment", "hosting"},
}

SIGNAL_TYPE_KEYWORDS = {
    "Model Releases": {"model", "gpt", "llm", "claude", "gemini", "llama", "openai", "anthropic"},
    "Research Breakthroughs": {"research", "paper", "benchmark", "eval", "dataset", "reasoning"},
    "AI Agents": {"agent", "agents", "automation", "workflow", "tool-use", "mcp"},
    "Open Source AI": {"open-source", "opensource", "github", "repo", "stars", "library"},
    "Developer Tools": {"code", "coding", "developer", "programming", "framework", "sdk", "api"},
    "AI Infrastructure": {"inference", "gpu", "vector", "database", "deployment", "hosting"},
    "Startup and Funding": {"startup", "saas", "founder", "launch", "customer", "market", "funding", "venture"},
    "Policy and Safety": {"policy", "regulation", "safety", "copyright", "privacy"},
}


class RankingService:
    def rank_for_user(self, db: Session, user: User | None, raw_items: list[RawNews]) -> list[Signal]:
        created_signals: list[Signal] = []
        interests = {interest.name for interest in user.interests} if user else {"ai", "coding", "startups"}

        for raw in raw_items:
            if db.scalar(select(Signal).where(Signal.raw_news_id == raw.id, Signal.user_id == getattr(user, "id", None))):
                continue

            tokens = set(tokenize(f"{raw.title} {raw.summary_snippet or ''} {' '.join(raw.tags)}"))
            relevance_score, matched_interest = self._relevance(tokens, interests)
            merged_sources = (raw.raw_payload or {}).get("merged_sources") or [raw.source]
            duplicate_links = (raw.raw_payload or {}).get("duplicate_links") or [raw.link]
            cross_source_score = min((len(set(merged_sources)) - 1) / 3, 1.0)
            trend_velocity = min((raw.mention_count / 12) + (0.25 * cross_source_score), 1.0)
            source_credibility = raw.credibility_score
            freshness_score = self._freshness(raw)
            engagement_score = self._engagement(raw)
            reddit_mentions = raw.mention_count if raw.source == "reddit" else 0
            github_stars = raw.engagement_score if raw.source == "github" else 0
            score = int(
                100
                * (
                    0.22 * trend_velocity
                    + 0.2 * source_credibility
                    + 0.2 * relevance_score
                    + 0.15 * freshness_score
                    + 0.15 * engagement_score
                    + 0.08 * cross_source_score
                )
            )
            if score < MIN_IMPORTANCE_SCORE:
                continue
            opportunity_score = min(10, max(1, round((score / 100) * 10)))
            ranking_factors = {
                "trend_velocity": trend_velocity,
                "source_credibility": source_credibility,
                "relevance_score": relevance_score,
                "freshness_score": freshness_score,
                "engagement_score": engagement_score,
                "cross_source_score": cross_source_score,
                "reddit_mentions": reddit_mentions,
                "github_stars": github_stars,
                "merged_sources": sorted(set(merged_sources)),
                "duplicate_links": sorted(set(duplicate_links)),
            }

            signal_type = self._signal_type(tokens, matched_interest or (raw.tags[0] if raw.tags else "general"))

            signal = Signal(
                raw_news_id=raw.id,
                user_id=getattr(user, "id", None),
                category=signal_type,
                importance_score=score,
                opportunity_score=opportunity_score,
                trend_velocity=trend_velocity,
                relevance_score=relevance_score,
                source_credibility=source_credibility,
                freshness_score=freshness_score,
                engagement_score=engagement_score,
                ranking_factors=ranking_factors,
                expires_at=utc_now() + timedelta(days=2),
                action_recommendation=self._action_recommendation(signal_type, score, raw.source),
            )
            db.add(signal)
            db.add(
                TrendScore(
                    raw_news_id=raw.id,
                    scored_at=utc_now(),
                    source=raw.source,
                    trend_velocity=trend_velocity,
                    engagement_score=engagement_score,
                    freshness_score=freshness_score,
                    reddit_activity_score=min(reddit_mentions / 50, 1.0),
                    github_star_score=min(github_stars / 5000, 1.0),
                    credibility_score=source_credibility,
                    composite_score=score,
                    factors=ranking_factors,
                )
            )
            created_signals.append(signal)

        db.commit()
        for signal in created_signals:
            db.refresh(signal)
        return created_signals

    def _relevance(self, tokens: set[str], interests: set[str]) -> tuple[float, str | None]:
        best_score = 0.1
        best_interest = None
        for interest in interests:
            keywords = INTEREST_KEYWORDS.get(interest, {interest})
            overlap = len(tokens.intersection(keywords))
            score = min(overlap / max(len(keywords) / 2, 1), 1.0)
            if score > best_score:
                best_score = score
                best_interest = interest
        return best_score, best_interest

    def _freshness(self, raw: RawNews) -> float:
        if not raw.published_at:
            return 0.5
        age_hours = max((utc_now() - raw.published_at).total_seconds() / 3600, 0)
        return max(0.05, min(1.0, 1 - (age_hours / 48)))

    def _engagement(self, raw: RawNews) -> float:
        if raw.source == "github":
            return min(raw.engagement_score / 5000, 1.0)
        if raw.source == "reddit":
            return min(raw.engagement_score / 1000, 1.0)
        if raw.source == "hackernews":
            return min(raw.engagement_score / 700, 1.0)
        return min(raw.engagement_score / 150, 1.0)

    def _signal_type(self, tokens: set[str], fallback: str) -> str:
        best_type = fallback
        best_overlap = 0
        for signal_type, keywords in SIGNAL_TYPE_KEYWORDS.items():
            overlap = len(tokens.intersection(keywords))
            if overlap > best_overlap:
                best_overlap = overlap
                best_type = signal_type
        return best_type

    def _action_recommendation(self, signal_type: str, score: int, source: str) -> str:
        if score >= 85:
            urgency = "Act today"
        elif score >= 70:
            urgency = "Review this week"
        else:
            urgency = "Monitor"

        actions = {
            "AI Agents": "prototype one narrow workflow or add it to your automation backlog",
            "Open Source AI": "inspect the repo, issues, adoption signals, and integration gaps",
            "Developer Tools": "test whether this improves your build, deploy, or coding loop",
            "AI Infrastructure": "compare it against your current inference, eval, or data stack",
            "Research Breakthroughs": "read the technical details and look for productizable constraints",
            "Startup and Funding": "validate buyer pain with customer conversations before building",
            "Policy and Safety": "check compliance exposure and update your watchlist",
        }
        next_step = actions.get(signal_type, "open the source and decide whether it changes your roadmap")
        return f"{urgency}: {next_step}. Source: {source}."

    @staticmethod
    def top_signals(db: Session, user_id: int | None = None, limit: int = 5) -> list[Signal]:
        query = (
            select(Signal)
            .options(joinedload(Signal.raw_news), joinedload(Signal.summary))
            .where(Signal.status == "active")
            .order_by(Signal.importance_score.desc(), Signal.created_at.desc())
            .limit(limit)
        )
        if user_id is not None:
            query = query.where(Signal.user_id == user_id)
        return list(db.scalars(query).unique())

    @staticmethod
    def grouped_trending(db: Session, limit: int = 4) -> dict[str, list[Signal]]:
        sections = {
            "Trending AI Topics": ["Model Releases", "Research Breakthroughs", "AI Agents", "Policy and Safety"],
            "Latest Open Source AI": ["Open Source AI"],
            "Important AI Tools": ["Developer Tools", "AI Infrastructure", "AI Agents"],
            "Startup and Funding": ["Startup and Funding"],
        }
        output: dict[str, list[Signal]] = {}
        for section, categories in sections.items():
            query = (
                select(Signal)
                .options(joinedload(Signal.raw_news), joinedload(Signal.summary))
                .where(Signal.category.in_(categories), Signal.status == "active")
                .order_by(Signal.importance_score.desc(), Signal.created_at.desc())
                .limit(limit)
            )
            output[section] = list(db.scalars(query).unique())
        return output
