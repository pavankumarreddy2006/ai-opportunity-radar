# AI Opportunity Radar Final Report

Date: 2026-05-25

## 1. Bugs Fixed

- Reworked frontend API requests to use per-attempt timeouts, retry/backoff for GET requests, safe JSON parsing, and cleaner fallback behavior.
- Removed normal fallback-path `console.error` logging from the API client.
- Fixed fragile image fallback behavior by moving it into a dedicated image component with a controlled fallback chain.
- Prevented behavior tracking failures from crashing or blocking the feed when backend storage is unavailable.
- Consolidated duplicated backend signal serialization across news, signals, trending, and dashboard routes.
- Added optional token protection support for `/update-news` while preserving current behavior when no token is configured.
- Added regression coverage for the new interaction tracking endpoint.

## 2. Features Added

- `components/news/NewsImage.tsx`
  - Lazy/eager loading support.
  - Skeleton and blur transition.
  - Stable 16:9 aspect ratio.
  - Source image, category fallback, and platform fallback chain.
  - Broken-image recovery.
- `services/recommendationEngine.ts`
  - Personalized ranking using the requested weighted formula:
    - interest match: 35%
    - engagement: 20%
    - click history: 15%
    - saved/liked preference: 15%
    - freshness: 10%
    - trend: 5%
  - Local persistence for interests, saves, likes, clicks, reading time, search history, category views, and topic weights.
  - For You, Trending, Latest, and Saved feed helpers.
- `services/newsScoring.ts`
  - AI summary fallback composition.
  - Why-it-matters fallback.
  - Opportunity score normalization.
  - Trend score normalization.
  - Clickbait/spam/quality filtering.
- Backend `/preferences/interaction`
  - Stores interaction weights when the database is available.
  - Returns a degraded status instead of crashing when storage is unavailable.
- UI improvements
  - Cleaner app shell.
  - Sticky nav.
  - Theme toggle.
  - Stronger empty/loading/toast states.
  - Reusable feed tabs, sidebar, cards, and image rendering.

## 3. Files Modified

- `docs/audit-report.md`
- `docs/final-report.md`
- `frontend/components/news-feed.tsx`
- `frontend/components/news/NewsImage.tsx`
- `frontend/services/recommendationEngine.ts`
- `frontend/services/newsScoring.ts`
- `frontend/lib/api.ts`
- `backend/app/api/routes/*.py`
- `backend/app/core/settings.py`
- `backend/app/schemas/interest.py`
- `backend/app/services/interest_service.py`
- `backend/app/services/signal_serializer.py`
- `backend/tests/test_api_smoke.py`
- `.env.example`
- `backend/.env.example`
- `render.yaml`

## 4. Architecture Improvements

- Split frontend business logic out of the feed component into reusable services.
- Centralized news image behavior in one component.
- Centralized backend `Signal` to API response serialization.
- Added a backend path for persistent personalization signals without introducing a new migration.
- Kept Render deployment simple and compatible with existing API/frontend/cron services.

## 5. Performance Metrics

- `npm run build`: passed.
- Next production route size:
  - `/`: 11.1 kB route size.
  - First Load JS: 114 kB.
  - Shared JS: 102 kB.
- Backend tests: 11 passed.
- Local smoke:
  - Backend `/health`: HTTP 200, database `ok` with local SQLite.
  - Frontend `/`: HTTP 200 and rendered expected app content.

## 6. Lighthouse Score

- Lighthouse was not run because the `lighthouse` CLI/package is not installed in this workspace and no browser automation tool was exposed in this session.
- Current build size is small enough to be a good Lighthouse baseline, but an actual Lighthouse score still needs a browser run.

## 7. Remaining Issues

- No frontend browser screenshot verification was possible in this session.
- Likes/saves/clicks are synced as aggregate backend preference weights, not yet as a full normalized event table.
- `/update-news` token support is optional; production can enable it with `UPDATE_NEWS_TOKEN`, but the current Render cron does not send a header.
- True API pagination/cursors are still future work; frontend pagination remains client-side over the fetched set.
- Lighthouse and cross-browser checks still need to be run in an environment with browser automation available.

## 8. Future Roadmap

1. Add a normalized `user_interactions` table and analytics endpoints.
2. Add cursor pagination to `/news`.
3. Add a dedicated image cache/proxy service for remote article images.
4. Add frontend component tests and Playwright visual checks.
5. Add production error monitoring and structured metrics.
6. Run Lighthouse and tune any discovered render-blocking or accessibility issues.
7. Add authenticated user accounts instead of the shared demo email.
