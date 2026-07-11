# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

GooseCompass is a RAG-based AI assistant for University of Waterloo outbound exchange students. It answers natural-language questions **strictly from retrieved institutional documents** — no external LLM knowledge is allowed. Every response must include paragraph-level citations.

Beyond the RAG assistant, GooseCompass provides **@uwaterloo.ca**-restricted authentication (email + OTP), per-user token usage tracking with quotas, basic system monitoring, and a self-service exchange planner with a phase tracker, host-school research table, and course-matching table. Planner data is stored separately as students’ personal working notes and is never used for RAG retrieval, ensuring a clear architectural separation between user-managed information and grounded, citation-backed answers.

Stack: FastAPI + MongoDB Atlas + PostgreSQL (SQLAlchemy 2.0 async + asyncpg + Alembic) + PydanticAI + React/TypeScript + Docling + OpenAI embeddings + OpenRouter LLM. Backend on Render, frontend on Vercel.

## Development commands

**Backend setup:**
```bash
pip install -e ".[dev]"
```

**Run backend server:**
```bash
uvicorn backend.api.app:app --reload
```

**Database migrations (Postgres, via Alembic):**
```bash
alembic upgrade head                  # apply migrations
alembic revision --autogenerate -m "" # create a new migration
```

**Run all tests:**
```bash
pytest backend/tests/ -v
```

**Run a single test:**
```bash
pytest backend/tests/path/to/test_file.py::test_function_name -v
```

**CLI validation tools (built before the API layer):**
```bash
python scripts/ingest.py              # ingest all sources in scripts/sources.json
python scripts/ingest.py --dry-run    # list sources without ingesting
python scripts/validate_retrieval.py  # interactive retrieval quality check
python scripts/validate_generation.py # interactive end-to-end pipeline check
```

**Frontend:**
```bash
cd frontend && npm run dev            # starts Vite dev server at localhost:5174
```

**API endpoints (backend must be running):**
```
GET  /health               health check
POST /query                full RAG pipeline, returns GeneratedResponse JSON (auth required, quota-checked)
POST /query/stream          same pipeline, streams tokens via text/event-stream (auth required, quota-checked)
POST /auth/request-code    send OTP to a @uwaterloo.ca email
POST /auth/verify-code     verify OTP, issue JWT session
/planner/*                 exchange plan, host schools, course matches, notes (per-user, Postgres-backed)
```

## Environment variables

Copy `.env.example` → `.env` and fill in all values:

```
MONGODB_URI=
MONGODB_DB_NAME=
MONGODB_COLLECTION_CHUNKS=
OPENAI_API_KEY=
OPENROUTER_API_KEY=
OPENROUTER_GENERATION_MODEL=
OPENROUTER_REWRITER_MODEL=
FRONTEND_ORIGIN=http://localhost:5174
VITE_API_URL=http://localhost:8000
POSTGRES_URI=
JWT_SECRET=
EMAIL_PROVIDER=
EMAIL_API_KEY=
EMAIL_FROM=
```

## Architecture

Two-database architecture, split by data type rather than by feature:

- **MongoDB Atlas** (unchanged): document store + vector search + full-text search over institutional chunks. Used only by `retrieval/` and `generation/`.
- **PostgreSQL**: relational data — users, auth codes, sessions, usage logs, and all exchange-planner data (host schools, course matches, progress, notes). Used by `auth/`, `users/`, `planner/`, and `monitoring/`.

```
GooseCompass/
├── backend/
│   ├── config.py         # pydantic-settings loader; POSTGRES_URI, JWT_SECRET, EMAIL_* settings
│   ├── db.py              # async Motor client (Mongo) + async SQLAlchemy engine/session (Postgres)
│   ├── auth/              # OTP request/verify, JWT issuance, session dependency
│   ├── users/             # user model, profile
│   ├── planner/           # exchange plan, host schools, course matches, progress
│   ├── monitoring/        # usage logging middleware, quota enforcement, usage queries
│   ├── ingestion/        # Docling pipeline: fetch → chunk → embed → store (unchanged)
│   ├── retrieval/        # vector search + Atlas full-text search + RRF fusion (unchanged)
│   ├── generation/       # PydanticAI structured response + citation schema (unchanged)
│   ├── api/              # FastAPI routes: existing RAG routes + auth/planner/monitoring routers
│   └── tests/            # mirrors source structure, including new modules
├── frontend/             # React + TypeScript: chat UI, sign-in, exchange planner dashboard
├── scripts/              # CLI tools for ingestion and retrieval validation
├── alembic/               # Postgres migrations
└── docs/                 # TASKS.md (phased build plan), architecture docs
```

Each new module owns its own Postgres tables, preserving the project's separation-of-concerns rule; the existing retrieval/generation pipeline over MongoDB is untouched by this expansion.

### Retrieval pipeline (the core of the system)

```
User query
  → Query rewriter (LLM via OpenRouter, improves recall for institutional terminology)
  → Parallel retrieval
      ├── MongoDB vector search (OpenAI text-embedding-3-small, top 20)
      └── MongoDB Atlas full-text search (top 20)
  → Reciprocal Rank Fusion (RRF)
  → Top-10 context selection
  → PydanticAI response generator (structured answer + end-of-paragraph citations)
```

**PydanticAI is used only for structured generation and schema validation — not for retrieval.** Retrieval is deterministic backend logic.

### MongoDB Atlas roles

- **Vector Search index**: semantic similarity on chunk embeddings
- **Atlas Search index**: keyword/fuzzy full-text search
- **Document store**: chunks with metadata (source URL, document title, section title, document type, chunk index)

### PostgreSQL roles

- **Auth**: `users`, `auth_codes` (hashed OTP codes with TTL and attempt limits)
- **Usage/monitoring**: `usage_logs` (per-call token/cost tracking), `request_logs` (status/latency for all routes)
- **Exchange planner**: `exchange_plans`, `host_schools`, `course_matches`

### Key constraints

- **Strict grounding**: if retrieved context is insufficient, the system must say so. Never synthesize from model knowledge.
- **Session-only chat state**: no persistent chat history (MVP). Conversation state lives in memory per session — distinct from the JWT auth session, which is persisted.
- **Retrieval-first development order**: CLI validation → backend API → streaming frontend.
- **Auth-gated access**: `/query` and `/query/stream` require a valid JWT for a verified `@uwaterloo.ca` user; no anonymous access.
- **Quota before generation**: usage quota must be checked before the LLM call, not just logged after — a user over quota must get a graceful "limit reached" response instead of invoking the LLM.
- **Planner/RAG isolation**: exchange planner data (host schools, course matches, notes) is user-authored working data, not institutional source material. It must never be written into the MongoDB retrieval store or used as grounding context, and must stay architecturally distinct from the RAG chat path.

## Coding principles (enforce strictly)

- **DRY**: extract shared logic into reusable modules.
- **KISS**: prefer the simple solution.
- **YAGNI**: don't build what isn't needed yet.
- **SoC**: retrieval, generation, auth, planner, monitoring, API, and UI layers must stay cleanly separated. New modules own their own tables and don't reach into each other's storage.
- **Async I/O**: all I/O inside request-handling code paths (MongoDB, Postgres, embeddings, LLM calls, email/HTTP) must use async clients (Motor, asyncpg via SQLAlchemy's async engine, httpx.AsyncClient). No sync SDKs or requests calls inside request handlers — this is why email must go through httpx.AsyncClient rather than a provider SDK. Exception: Alembic migrations and standalone admin/maintenance scripts that run outside the live server process may use sync clients (e.g. psycopg2 for Alembic) — they don't share the event loop with concurrent user traffic, so async adds complexity with no benefit there.
- **Offload CPU-bound work**: blocking CPU work with no async equivalent (OTP/password hashing) must never be awaited inline — run it via `asyncio.to_thread` so it doesn't stall the event loop. Cheap CPU-bound calls with negligible cost (JWT encode/decode) may stay inline; don't offload work that costs less than the offload itself.
- **Keep logging off the response path**: `usage_logs` and `request_logs` writes must not block the client-visible response — use FastAPI `BackgroundTasks` so the Postgres write happens after the response (or final stream chunk) is sent, not before.

## Code style

- Python: Google-style docstrings on all functions and classes (`Args`, `Returns`, `Raises` sections).
- TypeScript: JSDoc on all exported functions and components.
- Max function length: 40 lines — split if longer.

## Testing rules

- Write the test immediately after implementing each function.
- Tests mirror source structure under `backend/tests/`.
- Run tests before marking any task done. Never skip.

## Task discipline

- Do exactly ONE task at a time. Stop and wait for review.
- If a task feels large, split it further and confirm with the user.
