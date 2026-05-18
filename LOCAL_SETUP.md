# Local Setup

## Current Requirement

The backend uses PostgreSQL. The API can import without a running database, but migrations and dashboard data endpoints need a reachable database.

## Fast Path With Docker

If Docker Desktop is installed:

```powershell
docker compose up -d db
alembic upgrade head
uvicorn app.main:app --reload
```

## Fast Path Without Docker

Install PostgreSQL locally, then create this database:

```sql
CREATE DATABASE ai_opportunity_radar;
```

The default local connection string is:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ai_opportunity_radar?connect_timeout=5
```

If your local PostgreSQL password is different, update `.env`.

## Useful Checks

Check whether Postgres is listening:

```powershell
Test-NetConnection -ComputerName localhost -Port 5432
```

Check Alembic can see migrations:

```powershell
alembic heads
```

Run migrations:

```powershell
alembic upgrade head
```

Start backend:

```powershell
uvicorn app.main:app --reload
```

## Common Errors

`No such file or directory: requirements.txt`

Run from the project root. A root `requirements.txt` now points to the backend dependencies.

`No module named psycopg`

Run `python -m pip install -r requirements.txt`.

`connection failed` or migration timeout

PostgreSQL is not running, the database does not exist, or `.env` has the wrong password.

