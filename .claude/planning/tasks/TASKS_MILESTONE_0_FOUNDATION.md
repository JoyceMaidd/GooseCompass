# Milestone Phase 0 — Foundation & Postgres Setup

Goal: Postgres wired alongside the existing MongoDB client, Alembic migrations working, new module skeletons in place. No feature logic yet — this phase only makes the next four phases possible.

See `TASKS_MILESTONE.md` for the M-1 to M-7 info items this phase consumes.

---

### 0.1 `[USER]` Provision a Postgres instance

1. Create a Postgres instance — Render managed Postgres is recommended for single-platform simplicity with the Phase 5 deployment, but any Postgres works for local dev.
2. Note the connection string in `postgresql+asyncpg://user:pass@host:port/dbname` form (SQLAlchemy async driver prefix, not the bare `postgresql://` Render gives you by default).
3. This is `M-1`.

---

### 0.2 `[CODE]` Add Postgres/auth dependencies to `pyproject.toml`

Add to `dependencies`:
- `sqlalchemy[asyncio]>=2.0`
- `asyncpg>=0.29`
- `alembic>=1.13`
- `pyjwt>=2.9`
- `argon2-cffi>=23.1` (OTP hashing)
- `email-validator>=2.2` (pydantic email validation)

Add to `dev`:
- `pytest-postgresql` or note in test docs that Postgres tests run against a real test database (matches existing pattern of testing against real Atlas — no mocking of the DB layer).

Test: `pip install -e ".[dev]"` completes without errors.

---

### 0.3 `[CODE]` Extend `.env.example` with new variables

Add:
```
POSTGRES_URI=
JWT_SECRET=
EMAIL_PROVIDER=
EMAIL_API_KEY=
EMAIL_FROM=
```

(`FRONTEND_ORIGIN` and `VITE_API_URL` already exist per current `CLAUDE.md`.)

No test needed — template file.

---

### 0.4 `[USER]` Fill in new `.env` values

Fill in `POSTGRES_URI` (`M-1`), `JWT_SECRET` (`M-2`), `EMAIL_PROVIDER`/`EMAIL_API_KEY` (`M-3`), `EMAIL_FROM` (`M-4`).

---

### 0.5 `[CODE]` Extend `backend/config.py` — new settings fields

Add to the existing `Settings` class: `postgres_uri`, `jwt_secret`, `email_provider`, `email_api_key`, `email_from`. Keep the existing MongoDB/OpenAI/OpenRouter fields untouched.

Test: extend `tests/test_config.py` — assert the new fields load and are non-empty when `.env` is present; assert `ValidationError` when one is missing.

---

### 0.6 `[CODE]` Create `backend/db_models.py` — shared SQLAlchemy declarative base

One `Base` (SQLAlchemy 2.0 `DeclarativeBase`) that every new module's models inherit from, so Alembic can autogenerate against a single `Base.metadata`. Does not itself define any tables.

Test: `tests/test_db_models.py` — assert `Base.metadata.tables` is empty before any module models are imported (sanity check the base is otherwise inert).

---

### 0.7 `[CODE]` Extend `backend/db.py` — async Postgres engine/session

Add:
- `get_postgres_engine()` — creates the async engine from `settings.postgres_uri` (created once, reused).
- `get_db_session()` — FastAPI dependency yielding an `AsyncSession`, closed after the request.
- Wire engine creation/disposal into the existing `lifespan` alongside the Mongo client open/close.

Test: extend `tests/test_db.py` — assert a session from `get_db_session()` can execute `SELECT 1` and get back `1`.

---

### 0.8 `[CODE]` Create new module directory skeletons

```
backend/
  auth/__init__.py
  users/__init__.py
  planner/__init__.py
  monitoring/__init__.py
  tests/
    auth/__init__.py
    users/__init__.py
    planner/__init__.py
    monitoring/__init__.py
```

Test: `python -c "import backend.auth, backend.users, backend.planner, backend.monitoring"` succeeds.

---

### 0.9 `[CODE]` Initialize Alembic

```bash
alembic init alembic
```

Configure `alembic/env.py` to:
- Read `POSTGRES_URI` from `backend.config.settings` rather than a hardcoded `alembic.ini` URL.
- Use a **sync** driver (`psycopg2`) for the Alembic run itself, per `CLAUDE.md`'s exception for migrations/admin scripts — add `psycopg2-binary` as a dev-only dependency for this.
- Set `target_metadata = Base.metadata` from `backend.db_models`.

Test: `alembic current` runs without error and reports no revision (empty history).

---

### 0.10 `[USER]` Confirm Alembic ↔ Postgres connectivity

Run:
```bash
alembic revision -m "baseline (empty)"
alembic upgrade head
```

Confirm no errors and that Alembic's `alembic_version` table appears in the database (via `psql` or a GUI client).

Report back: connection confirmed, ready for Phase 1.
