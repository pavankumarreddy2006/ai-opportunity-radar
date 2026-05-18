from datetime import datetime, timezone

from app.schemas.signal import DashboardResponse, SignalResponse, SummaryPayload, TrendingGroup, WeeklyReportResponse


def _now() -> datetime:
    return datetime.now(timezone.utc)


FALLBACK_SIGNALS: list[SignalResponse] = [
    SignalResponse(
        id=9001,
        category="AI Agents",
        importance_score=92,
        opportunity_score=9,
        action_recommendation="Prototype one repeated workflow with an agent and measure whether it saves real time.",
        created_at=_now(),
        raw_title="AI agents are moving from impressive demos into practical production workflows",
        source="radar-fallback",
        link="https://news.ycombinator.com",
        tags=["ai", "agents", "automation"],
        published_at=_now(),
        summary=SummaryPayload(
            headline="Agentic workflows are becoming practical for small teams",
            what_happened="AI builders are combining search, code, browser control, and business tools into repeatable workflows.",
            why_it_matters="This shifts AI from chat assistance toward operational leverage for small teams.",
            why_you_should_care="A narrow workflow agent can become an internal advantage or a focused product wedge.",
            action_recommendation="Pick one painful recurring task and sketch an agent version today.",
            opportunity_score=9,
        ),
    ),
    SignalResponse(
        id=9002,
        category="Open Source AI",
        importance_score=88,
        opportunity_score=8,
        action_recommendation="Track the strongest repos and look for setup, observability, or integration gaps.",
        created_at=_now(),
        raw_title="Open-source AI infrastructure keeps fragmenting into sharper tools",
        source="github-fallback",
        link="https://github.com/trending",
        tags=["open-source", "github", "inference"],
        published_at=_now(),
        summary=SummaryPayload(
            headline="AI infrastructure niches are still early enough to enter",
            what_happened="Developers keep shipping focused tools for routing, evals, inference, and workflow orchestration.",
            why_it_matters="Fragmentation creates integration pain, and integration pain often becomes startup demand.",
            why_you_should_care="A small hosted dashboard, wrapper, or managed workflow can be valuable quickly.",
            action_recommendation="Find one popular repo with unresolved setup or monitoring complaints.",
            opportunity_score=8,
        ),
    ),
    SignalResponse(
        id=9003,
        category="Developer Tools",
        importance_score=83,
        opportunity_score=7,
        action_recommendation="Use the simplest managed path for the next MVP unless scale already demands custom infrastructure.",
        created_at=_now(),
        raw_title="Full-stack AI apps are getting easier to deploy and iterate",
        source="rss-fallback",
        link="https://vercel.com/blog",
        tags=["coding", "deployment", "ai"],
        published_at=_now(),
        summary=SummaryPayload(
            headline="Deployment defaults are compressing MVP timelines",
            what_happened="Modern app stacks increasingly bundle typed APIs, server rendering, managed data, and straightforward deploy paths.",
            why_it_matters="Teams can spend more cycles learning from users and fewer cycles wiring infrastructure.",
            why_you_should_care="A credible AI product prototype can be built and shipped faster than before.",
            action_recommendation="Choose the most boring managed deploy path for your next experiment.",
            opportunity_score=7,
        ),
    ),
    SignalResponse(
        id=9004,
        category="Startup and Funding",
        importance_score=79,
        opportunity_score=8,
        action_recommendation="Interview five operators who still copy data between tools.",
        created_at=_now(),
        raw_title="Boring business workflows remain rich AI automation targets",
        source="reddit-fallback",
        link="https://www.reddit.com/r/startups/",
        tags=["startups", "automation", "ops"],
        published_at=_now(),
        summary=SummaryPayload(
            headline="Unsexy operations problems are AI product opportunities",
            what_happened="Operators still describe repeated handoffs across spreadsheets, inboxes, CRMs, and dashboards.",
            why_it_matters="These workflows have clear ROI and buyers who already feel the pain.",
            why_you_should_care="A narrow automation product can beat a generic assistant when it owns one workflow end to end.",
            action_recommendation="Look for one recurring approval, reporting, or reconciliation loop.",
            opportunity_score=8,
        ),
    ),
    SignalResponse(
        id=9005,
        category="Research Breakthroughs",
        importance_score=74,
        opportunity_score=6,
        action_recommendation="Map the skill gap and adjust learning or hiring priorities.",
        created_at=_now(),
        raw_title="AI product engineering increasingly rewards systems thinking",
        source="hackernews-fallback",
        link="https://news.ycombinator.com/jobs",
        tags=["jobs", "ai", "engineering"],
        published_at=_now(),
        summary=SummaryPayload(
            headline="AI features now require full product systems",
            what_happened="Hiring and product signals increasingly blend backend reliability, evals, UX polish, and model judgment.",
            why_it_matters="Model calls alone are not enough for durable AI products.",
            why_you_should_care="Owning end-to-end AI product quality is becoming a stronger advantage.",
            action_recommendation="Build one portfolio workflow with evals, auth, persistence, and deployment.",
            opportunity_score=6,
        ),
    ),
]


def fallback_signals(limit: int = 20) -> list[SignalResponse]:
    return FALLBACK_SIGNALS[:limit]


def fallback_trending() -> list[TrendingGroup]:
    return [
        TrendingGroup(section="Trending Topics", signals=fallback_signals(3)),
        TrendingGroup(section="AI Tool Trends", signals=[FALLBACK_SIGNALS[0], FALLBACK_SIGNALS[2]]),
        TrendingGroup(section="Open Source AI", signals=[FALLBACK_SIGNALS[1], FALLBACK_SIGNALS[2]]),
        TrendingGroup(section="Startup Opportunities", signals=[FALLBACK_SIGNALS[3], FALLBACK_SIGNALS[0]]),
    ]


def fallback_dashboard() -> DashboardResponse:
    return DashboardResponse(
        top_signals=fallback_signals(5),
        trending=fallback_trending(),
        interests=["ai", "coding", "startups"],
    )


def fallback_weekly_report() -> WeeklyReportResponse:
    return WeeklyReportResponse(
        headline="Your highest-value AI opportunity signals this week",
        executive_summary=(
            "Agents, open-source infrastructure, and workflow automation remain the strongest "
            "startup-relevant patterns to watch."
        ),
        top_categories=["AI Agents", "Open Source AI", "Developer Tools", "Startup and Funding"],
        signals=fallback_signals(5),
    )
