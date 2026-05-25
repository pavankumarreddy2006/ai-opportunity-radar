# AI Opportunity Radar Audit Report

Date: 2026-05-25

## Architecture Overview

### Frontend

- Next.js 15 / React 19 app in `frontend/`.
- Primary route is `frontend/app/page.tsx`, a server component that fetches `/news`, `/trending`, `/preferences`, and `/weekly-report` in parallel.
- Main interactive UI is concentrated in `frontend/components/news-feed.tsx`.
- Styling uses Tailwind CSS with custom dark theme tokens in `frontend/tailwind.config.ts` and global background styles in `frontend/app/globals.css`.
- API helper lives in `frontend/lib/api.ts` and includes request timeout, limited retry, and fallback payloads.
- Fallback data lives in `frontend/lib/fallback-data.ts`.

### Backend

- FastAPI app in `backend/app/main.py`.
- API router composes auth, health, news, signals, dashboard, preferences, trending, and update routes.
- SQLAlchemy 2 models store users, interests, raw news, ranked signals, summaries, trend scores, and sources/categories.
- Alembic migrations exist through `20260518_0004_runtime_indexes.py`.
- Fallback API payloads exist in `backend/app/services/fallback_data.py` to keep endpoints alive when the database is empty or degraded.

### API Flow

- Frontend calls:
  - `GET /news?email=demo@ainewscollector.ai&limit=24`
  - `GET /trending`
  - `GET /preferences?email=demo@ainewscollector.ai`
  - `GET /weekly-report?email=demo@ainewscollector.ai`
  - `POST /preferences`
- Next rewrites expose backend endpoints from the frontend domain.
- Backend routes convert `Signal` ORM rows to `SignalResponse` in several duplicated `_to_signal_response` helpers.
- If DB/API work fails, most feed endpoints return fallback payloads.

### News Fetching Pipeline

- `NewsPipelineService` runs Reddit, GitHub, RSS, Hacker News, YouTube, and tech blog scrapers.
- Each scraper normalizes items through `BaseScraper.collect()`, which validates title/link, removes non-AI items, normalizes tags, and deduplicates within a single source.
- `DedupeService.persist_items()` deduplicates by normalized key and fuzzy cross-source title matching.
- `RankingService.rank_for_user()` creates generic and user-specific signals from changed raw items.
- `SummarizationService.generate_for_signals()` generates AI summaries when API keys are present and falls back to local summaries otherwise.
- Render cron runs `backend/update_news.py` hourly with tenacity retries.

### State Management

- Client state is local React state inside `NewsFeed`.
- Persistent user profile is stored in localStorage under `ai-radar-profile-v2`.
- Backend persistence currently stores only email, name, and interests.
- Likes, saves, clicks, reading behavior, search history, and topic weights are local-only.
- No global state library is currently used.

### Database / Storage

- Production uses Render Postgres via `DATABASE_URL`.
- Local default falls back to SQLite.
- Models cover core entities, but there is no persistent interaction/event table yet.
- Runtime indexes exist for signal status/category/importance and raw news source/created queries.

### Current Recommendation Logic

- Backend ranking is based on trend velocity, source credibility, relevance, freshness, engagement, and cross-source duplication.
- Frontend `rankSignals()` reranks already-fetched articles using local interests, clicked IDs, topic weights, freshness, and backend scores.
- The requested weighted formula is not yet implemented as a reusable service.
- Personalization is not fully durable because behavioral data does not sync to backend storage.

### Deployment Config

- `render.yaml` defines:
  - Python FastAPI API service at `ai-opportunity-radar-api`.
  - Node Next.js frontend service at `ai-opportunity-radar`.
  - Hourly Python cron job.
  - Render Postgres database.
- API service runs migrations before Uvicorn start.
- Frontend uses `NEXT_PUBLIC_API_BASE_URL=https://ai-opportunity-radar-api.onrender.com`.
- CORS allows frontend and alternate web host.

## Existing Problems

### Critical / High

- `NewsFeed` is too large and owns rendering, ranking, profile persistence, onboarding, toasts, image fallback, dedupe, search, and pagination in one component.
- `request()` in `frontend/lib/api.ts` reuses one `AbortController` across retries. Once aborted, retries cannot recover cleanly.
- Frontend logs API failures with `console.error`, which violates the no-console-error acceptance bar during normal API wake/fallback conditions.
- Image fallback exists but is embedded in the card and does not protect against repeated fallback failure loops.
- Backend `_to_signal_response()` is duplicated across news, signals, trending, and dashboard routes.
- `/update-news` can be triggered publicly with no auth/rate limiting and starts a process-local daemon thread.
- CORS config sets `allow_credentials` to a boolean expression, but the wildcard case needs careful handling; the current config is acceptable for listed origins but should be validated when origins change.
- Interaction events are not persisted on the backend, so adaptive personalization is fragile across devices and browser resets.

### Medium

- No route-level frontend error boundary beyond `app/error.tsx`; component-level card/image failures can still degrade the feed.
- Missing dedicated empty/loading components and reusable primitives.
- Feed pagination is local "load more"; there is no API cursor/page strategy.
- Backend endpoints generally catch broad exceptions and return fallback data, which keeps the UI alive but can hide production issues without structured error reporting.
- RankingService query orders globally by importance first, so "Latest" in the frontend depends on the same limited result set and cannot fetch true latest articles.
- `rank_for_user()` creates separate signals per user, which can grow quickly as users increase.
- OG image scraping happens during dedupe and can slow ingestion.
- Summarization calls are sequential, which can make cron slow when many new signals arrive.

### Low

- `deploy-copy/` duplicates much of the project and can drift from active source.
- `README.md` is minimal.
- Static backend dashboard exists separately from the Next UI and is not deeply integrated.

## Technical Debt

- Monolithic `NewsFeed` component should be split into app shell, tabs, sidebar, cards, onboarding, toast provider, and services.
- Shared response serialization should move to a backend utility/service.
- Frontend recommendation and scoring logic should move into reusable modules under `frontend/services/`.
- Fallback image constants are duplicated frontend/backend.
- Local-only state should be wrapped in a storage adapter to support backend sync and future auth.
- Tests cover backend smoke and a few service helpers, but no frontend render/interaction tests exist.

## Security Issues

- Public update endpoint can trigger scraper work and external requests.
- Demo email is hard-coded in the frontend, so all visitors share backend preference state.
- No auth is required for preferences writes; anyone can overwrite the demo profile.
- Error logging may expose operational details in server logs.
- External image URLs are rendered directly; UI needs strict broken-image fallback and Next image remote patterns if using `next/image`.
- Secrets are properly configured as unsynced/generated in Render, but local defaults like `SECRET_KEY=change-me` must never reach production.

## Performance Issues

- The main page makes four API requests on every dynamic render.
- `export const dynamic = "force-dynamic"` disables static optimization and increases cold-start sensitivity.
- Feed merges and re-sorts arrays on each state/profile change; acceptable at current size but should be isolated and memoized.
- No infinite-scroll observer; pagination requires manual load.
- Sequential backend summarization can slow the hourly cron.
- OG image scraping during ingestion is synchronous per item.
- No frontend bundle splitting beyond default Next behavior.
- No Lighthouse measurement has been run yet in this audit phase.

## UI / UX Problems

- Existing UI is functional but visually dense and dark-only.
- No explicit dark/light toggle despite a dark-mode requirement.
- Sidebar can consume too much vertical space on smaller laptops.
- Card image handling is not a reusable system.
- Action buttons have labels only through `aria-label/title`; this is fine for compact controls but hover/focus feedback can be improved.
- Empty states and skeletons exist but are not reusable and are visually basic.
- The onboarding modal exists but copy says "What are you interested in?" instead of the requested "What topics interest you?"
- Saved/liked/share interactions are local and can feel non-durable.

## Recommended Fixes

1. Stabilize `frontend/lib/api.ts` with per-attempt timeout, better retry/backoff, safe JSON parsing, and quiet expected fallback logging.
2. Extract shared frontend services:
   - `frontend/services/recommendationEngine.ts`
   - `frontend/services/newsScoring.ts`
   - local profile/interaction storage helpers.
3. Create `frontend/components/news/NewsImage.tsx` with lazy loading, skeleton, blur placeholder, aspect ratio, and safe fallback chain.
4. Split `NewsFeed` into smaller components and keep existing behavior intact.
5. Add backend interaction persistence endpoints/models or a lightweight JSON preference payload so clicks/saves/likes/search/category views can sync.
6. Consolidate backend signal serialization to one helper.
7. Protect `/update-news` with a secret header or internal-only Render cron path.
8. Add cursor/offset support to `/news` for scalable pagination.
9. Add quality filters for spam/clickbait/low-quality titles before ranking.
10. Add browser verification and Lighthouse after UI/performance work.

## Implementation Roadmap

### Iteration 1: Stability

- Repair API request retry/timeout behavior.
- Make expected fallback paths avoid console errors.
- Add reusable loading, empty, toast, and error UI.
- Verify backend tests and frontend typecheck/build.

### Iteration 2: Images

- Add `NewsImage` and central fallback chain.
- Reuse it in article cards.
- Ensure no broken image states.

### Iteration 3: Personalization

- Move ranking into `recommendationEngine.ts`.
- Track clicks, saves, likes, reading time, search history, and category views.
- Persist local profile and sync preferences/behavior to backend.
- Keep For You, Trending, Latest, and Saved tabs.

### Iteration 4: Quality Engine

- Add `newsScoring.ts`.
- Score summary quality, clickbait risk, spam likelihood, opportunity, freshness, and trend.
- Deduplicate more aggressively on canonical title/link.

### Iteration 5: Premium UI

- Refactor UI components and redesign as a polished mobile-first app shell.
- Add responsive sidebar/drawer behavior, sticky nav, smoother tabs, dark mode handling, skeletons, empty states, and micro-interactions.

### Iteration 6: Performance / Render

- Reduce waterfalls, cache API calls appropriately, memoize ranking, lazy-load non-critical UI, and validate Render env/build/health paths.
- Add pagination support and avoid overfetching.

### Iteration 7: Testing / Final Report

- Run backend tests, frontend typecheck/build, local API/frontend smoke tests, desktop/mobile browser checks, and Lighthouse if tooling is available.
- Create `docs/final-report.md` with bugs fixed, features added, modified files, architecture changes, metrics, remaining issues, and roadmap.
