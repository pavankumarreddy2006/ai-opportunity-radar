# Deployment Checklist

## Current Status

The app is prepared for GitHub and Render Blueprint deployment.

Important: the public URL `https://ai-opportunity-radar.onrender.com/` currently responds with the older FastAPI/Jinja shell. The upgraded production UI lives in the `frontend` Next.js app, so the Render service using that URL must be configured from the `ai-opportunity-radar` node service in `render.yaml`, not from the backend root.

Validated locally:

- Backend smoke tests pass.
- Frontend production build works.
- Render Blueprint parses correctly.
- Local secrets and build artifacts are ignored by Git.

## GitHub Upload

Run these from the project root:

```powershell
cd "C:\Users\pavan\OneDrive\Documents\news 2"
git status
git add .
git commit -m "Build AI Opportunity Radar MVP"
```

Create a new GitHub repository, then connect and push:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/ai-opportunity-radar.git
git branch -M main
git push -u origin main
```

If GitHub CLI is installed and authenticated, this can also create the repo:

```powershell
gh repo create ai-opportunity-radar --private --source=. --remote=origin --push
```

## Render Deploy

After the repository is pushed to GitHub, open:

```text
https://dashboard.render.com/blueprint/new
```

Select the GitHub repo and Render will read `render.yaml`.

The Blueprint creates:

- `ai-opportunity-radar-api`
- `ai-opportunity-radar`
- `ai-opportunity-radar-hourly-refresh`
- `ai-opportunity-radar-db`

If `ai-opportunity-radar` already exists as a Python/FastAPI service in Render, either:

- update that service to use `rootDir: frontend`, runtime `node`, build command `npm ci && npm run build`, and start command `npm start`, or
- delete/rename the old backend service before applying the Blueprint so the frontend can own `https://ai-opportunity-radar.onrender.com`.

The backend API should be the separate Python service:

```text
https://ai-opportunity-radar-api.onrender.com
```

## Required Secrets

Render will generate `SECRET_KEY` automatically.

Fill at least one AI provider key:

```env
OPENAI_API_KEY=your_openai_key
```

Optional fallback:

```env
OPENROUTER_API_KEY=your_openrouter_key
```

## Post-Deploy Checks

Open the frontend dashboard:

```text
https://ai-opportunity-radar.onrender.com
```

Check backend:

```text
https://ai-opportunity-radar-api.onrender.com/health
```

Expected:

```json
{"status":"ok"}
```

Trigger the first news update from the Render cron job page or wait for the hourly schedule.

## Common Render Errors

`DATABASE_URL missing`

The Blueprint database reference was not applied. Reopen the Blueprint resources and confirm the API and cron services reference `ai-opportunity-radar-db`.

`ModuleNotFoundError`

Confirm the backend service root directory is `backend`, build command is `pip install -r requirements.txt`, and start command is `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

Frontend builds but dashboard is empty

The backend has no signals yet. Run the cron job once or call the update endpoint after deployment.
