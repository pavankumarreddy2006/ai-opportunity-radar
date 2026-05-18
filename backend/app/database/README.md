# Database Layer

This package mirrors the lower-level database helpers and exists to preserve a clean, explicit architecture boundary for database concerns.

- `session.py` style responsibilities live in `app.db`
- SQLAlchemy model discovery lives in `app.db.base`
- Alembic migrations live in `backend/alembic`

The `database` package gives the project an intuitive top-level architecture for engineers reading the codebase for the first time.

