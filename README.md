# AI Opportunity Radar

AI Opportunity Radar is a production-ready MVP that turns noisy internet activity into a focused daily intelligence brief. It collects signals from developer and startup ecosystems, ranks them with an AI-assisted scoring engine, and presents the top opportunities in a responsive dashboard.

## Architecture

1. The backend uses FastAPI for APIs, scheduled update workflows, scraper orchestration, ranking, summarization, and persistence.
2. PostgreSQL stores user preferences, raw collected items, ranked signals, and generated summaries.
3. SQLAlchemy models and Alembic migrations keep the data layer maintainable and deployable.
4. The frontend uses Next.js App Router and Tailwind CSS to render a clean dark dashboard.
5. Render deploys both services and runs the hourly news refresh job.

## How It Works

New data flows through source scrapers for Reddit, GitHub Trending, Hacker News, RSS/blog feeds, and YouTube channel feeds. The pipeline normalizes and deduplicates raw items, scores trend velocity, engagement, freshness, credibility, and user relevance, then generates concise summaries for the highest-value signals. The dashboard asks one product question: “What are the top 5 things I should care about today?”

## API Surface

- `GET /health`
- `POST /auth/token`
- `GET /auth/me`
- `GET /signals`
- `GET /trending`
- `GET /dashboard`
- `GET /weekly-report`
- `GET /preferences`
- `POST /preferences`
- `POST /update-news`

## Folder Structure

```text
backend/
  alembic/
  app/
    ai/
    api/
    core/
    database/
    db/
    models/
    schemas/
    scraper/
    services/
  update_news.py
  requirements.txt
frontend/
  app/
  components/
  hooks/
  lib/
  styles/
render.yaml
```

## Local Setup

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for database setup options and common fixes.

### Backend

1. Create a Python virtual environment.
2. Install dependencies with `pip install -r backend/requirements.txt`.
3. Copy `.env.example` to `.env` or set environment variables.
4. Run migrations with `alembic upgrade head` from `backend`.
5. Start the API with `uvicorn app.main:app --reload` from `backend`.

### Frontend

1. Install dependencies with `npm install` inside `frontend`.
2. Copy `frontend/.env.local.example` to `.env.local`.
3. Run the app with `npm run dev`.

## Environment Variables

- `DATABASE_URL`
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL`
- `OPENAI_MODEL`
- `SECRET_KEY`
- `NEXT_PUBLIC_API_BASE_URL`

## Deployment

Render configuration is provided in [render.yaml](render.yaml). The backend exposes a health endpoint and includes a scheduled hourly job that refreshes the news pipeline.

## Verification

- Backend smoke tests: `python -m pytest` from `backend`
- Frontend production build: `npm run build` from `frontend`
# ai-opportunity-radar
