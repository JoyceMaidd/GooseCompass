# GooseCompass — Technical Architecture (Platform Expansion Milestone)

## Overview

This milestone extends GooseCompass from a single-user RAG MVP into a multi-user platform by adding authentication, usage tracking/quotas, system monitoring, and a self-service exchange planner.

The existing RAG pipeline (retrieval, generation, MongoDB Atlas) is untouched. New capabilities are added as equally separate layers alongside it, preserving the project's separation-of-concerns rule.

---

# 3.1 High-Level Architecture

Two-database architecture, split by data type rather than by feature:

* **MongoDB Atlas** (existing, unchanged) — document store + vector search + full-text search over institutional chunks. Used only by `retrieval/` and `generation/`.
* **PostgreSQL** (new) — relational data: users, auth codes, sessions, usage logs, and all exchange-planner data (host schools, course matches, progress, notes). Used by new `auth/`, `users/`, `planner/`, and `monitoring/` modules.

```text
backend/
├── config.py            # extended with POSTGRES_URI, JWT_SECRET, EMAIL_* settings
├── db.py                # Mongo client (existing) + new Postgres async engine/session
├── auth/                # OTP request/verify, JWT issuance, session dependency
├── users/                # user model, profile
├── planner/              # exchange plan, host schools, course matches, progress
├── monitoring/           # usage logging middleware, quota enforcement, usage queries
├── ingestion/            # unchanged
├── retrieval/            # unchanged
├── generation/           # unchanged
├── api/                  # existing routes + new auth/planner/monitoring routers
└── tests/                # mirrors new modules too
```

Reasoning:

* Keeps the RAG pipeline's storage concerns fully isolated from relational/app-state concerns
* Each new module owns its own Postgres tables, so auth, planner, and monitoring can be developed and tested independently
* No coupling introduced between the new relational modules and the existing retrieval/generation code paths

---

# 3.2 Technology Stack

## Backend framework

FastAPI (existing) — new routers added, existing routes untouched.

## RAG database

MongoDB Atlas via Motor (existing, unchanged).

## Relational database

PostgreSQL, accessed via SQLAlchemy 2.0 async engine + `asyncpg`.

## Migrations

Alembic.

## Auth

OTP codes (hashed at rest) + JWT sessions.

## Email delivery

Transactional email provider — Resend, SendGrid, or Postmark (pick one; all have adequate free tiers for OTP volume).

Called via `httpx.AsyncClient` against the provider's REST API, not its SDK — the common SDKs (SendGrid, Postmark) are built on the blocking `requests` library, which would stall the event loop if called inline from an `async def` route. This keeps email delivery consistent with the project's async-I/O rule (see CLAUDE.md Coding principles).

## Backend hosting

Render (web service + optionally Render managed Postgres, for single-platform simplicity).

## Frontend hosting

Vercel.

## Monitoring storage

Postgres tables (`usage_logs`, `request_logs`), queried directly — no separate observability service in this milestone.

---

# 3.3 Authentication Design

## Endpoints

### `POST /auth/request-code`

* Validates email domain is `uwaterloo.ca`
* Generates a 6-digit code
* Stores a hashed version with a short TTL (5–10 min) in Postgres
* Emails the code
* Rate-limited per email and per IP

### `POST /auth/verify-code`

* Checks the code (max 3–5 attempts before invalidation)
* Issues a JWT on success

## Session

JWT carries user ID and expiry; used as a bearer token or session cookie for all subsequent API calls.

## Blocking work

OTP hashing (bcrypt/argon2) is CPU-bound, not I/O — it must run via `asyncio.to_thread` rather than be awaited inline, since a direct call inside an `async def` handler would block the event loop for the duration of the hash (tens–hundreds of ms), stalling every other concurrent request on the worker, including in-flight RAG streams. JWT encode/decode is also CPU-bound but sub-millisecond, so it can stay inline without offloading.

## Rate limiting

Rate limiting for `request-code` and `verify-code` (per-email and per-IP) is Postgres-backed, not Redis or in-process memory — no new infra beyond the Postgres instance already required for this milestone, and consistent with the "single-platform simplicity" goal for the Render deployment. In-process memory was rejected because it silently breaks the moment more than one backend instance is running (each instance tracks its own counters, making the effective rate limit N times looser than configured).

## Postgres tables

* `users (id, email, created_at)`
* `auth_codes (id, user_id, code_hash, expires_at, attempts)`
* `rate_limits (key, scope, window_start, count)` — tracks request-code/verify-code attempts per email and per IP over a rolling window; exact shape (standalone table vs. a windowed query over `auth_codes`) to be finalized during implementation

---

# 3.4 Backend / Data Design

## Auth tables

* `rate_limits (key, scope, window_start, count)` — see 3.3; Postgres-backed per-email/per-IP rate limiting for OTP request/verify

## Usage & quota tables

* `usage_logs (id, user_id, endpoint, prompt_tokens, completion_tokens, estimated_cost, created_at)` — one row per LLM call
* `quota_limits (user_id, period, limit, used)` or computed on the fly from `usage_logs` — decide during implementation which is simpler to keep consistent

## Exchange planner tables

* `exchange_plans (id, user_id, current_phase, checklist_state)`
* `host_schools (id, plan_id, name, term_dates, language, cost_of_living, weather, currency, housing, competitiveness, course_match, proctored_exams, link, comments)`
* `course_matches (id, plan_id, host_school_id, core_course, proposed_match, syllabus_link, language, approved, terms_offered, restrictions, comments)`

## Monitoring table

* `request_logs (id, user_id, endpoint, status, latency_ms, error, created_at)` for system behavior monitoring

---

# 3.5 System Monitoring Design

## Usage logging & quota enforcement

A middleware/dependency on the `/query` and `/query/stream` routes:

* Checks quota *before* the LLM call, using an aggregate/cached count against the relevant period
* Captures token counts returned by the LLM call
* Writes to `usage_logs` via a FastAPI `BackgroundTask`, scheduled after the response (or final stream chunk) is sent — not awaited inline before returning to the client, so the Postgres write never adds latency to the user-visible request/stream

## Request logging

`request_logs` captures success/failure and latency for all API routes, giving basic visibility into system health without adding an external APM tool at this stage. Like `usage_logs`, these writes run via `BackgroundTasks` after the response is sent, keeping logging off the response-latency critical path.

## Dashboard

No dashboard UI is required for this milestone — usage and behavior data just needs to be queryable (via direct SQL or a simple internal endpoint) for the operator.

---

# 3.6 UI/UX (feature list only — no design spec)

* Sign-in screen: email entry, then code entry
* Exchange planner dashboard: phase-based navigation, host-school table, course-matching table, notes fields, progress checklist
* Existing chat assistant view, retained as-is architecturally, accessible alongside the planner
* Some indication to the user of remaining usage/quota (exact placement/design TBD later)
