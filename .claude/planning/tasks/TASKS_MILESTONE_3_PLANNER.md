# Milestone Phase 3 — Exchange Planner (Backend)

Goal: per-user exchange planner data — phase tracker, host school table, course matching table, notes — fully isolated from the RAG retrieval store, per `CLAUDE.md`'s Planner/RAG isolation rule.

**Prerequisite**: Phase 1 (Auth) complete — every route here is gated by `get_current_user` and scoped to the requesting user.

Development order: models → migration → schemas → service layer → routes → wiring.

---

### 3.1 `[CODE]` Define `backend/planner/models.py` — `ExchangePlan` model

SQLAlchemy model: `id (PK)`, `user_id (FK -> users.id, unique — one plan per user)`, `current_phase` (enum or string: `info_session`, `research`, `apply`, `course_matching`, `ic4e_session`), `checklist_state` (JSON column for the Next Steps checklist).

Test: `tests/planner/test_models.py` — construct and assert defaults; assert `user_id` uniqueness is declared.

---

### 3.2 `[CODE]` Define `backend/planner/models.py` — `HostSchool` model

SQLAlchemy model: `id (PK)`, `plan_id (FK -> exchange_plans.id)`, `name`, `term_dates`, `language`, `cost_of_living`, `weather`, `currency`, `housing`, `competitiveness`, `course_match`, `proctored_exams`, `link`, `comments`.

Test: extend `tests/planner/test_models.py`.

---

### 3.3 `[CODE]` Define `backend/planner/models.py` — `CourseMatch` model

SQLAlchemy model: `id (PK)`, `plan_id (FK -> exchange_plans.id)`, `host_school_id (FK -> host_schools.id)`, `core_course`, `proposed_match`, `syllabus_link`, `language`, `approved (bool)`, `terms_offered`, `restrictions`, `comments`.

Test: extend `tests/planner/test_models.py`.

---

### 3.4 `[CODE]` Alembic migration for `exchange_plans`, `host_schools`, `course_matches`

```bash
alembic revision --autogenerate -m "add exchange planner tables"
```

Test: confirm `upgrade()`/`downgrade()` populated; confirm cascade behavior on delete (deleting a plan should cascade to its host schools and course matches — decide and set `ondelete="CASCADE"` on the FKs before autogenerating, or add manually).

---

### 3.5 `[USER]` Apply the migration

```bash
alembic upgrade head
```

---

### 3.6 `[CODE]` Define `backend/planner/schemas.py` — Pydantic request/response schemas

`PlanRead`/`PlanUpdate`, `HostSchoolCreate`/`HostSchoolRead`/`HostSchoolUpdate`, `CourseMatchCreate`/`CourseMatchRead`/`CourseMatchUpdate`. Mirror the model fields; `*Create` schemas omit `id`/`plan_id` (set server-side from the authenticated user's plan).

Test: `tests/planner/test_schemas.py` — construct valid instances of each; assert `ValidationError` on a missing required field per schema.

---

### 3.7 `[CODE]` Implement `backend/planner/service.py` — plan get-or-create and phase update

Two async functions:
- `async get_or_create_plan(session, user_id: int) -> ExchangePlan`
- `async update_plan(session, user_id: int, update: PlanUpdate) -> ExchangePlan`

`get_or_create_plan` must only ever create/return the plan belonging to `user_id` — never another user's.

Test: `tests/planner/test_service.py` — first call creates a plan with a sensible default phase; second call for the same user returns the same row (no duplicate); `update_plan` changes `current_phase`/`checklist_state` and persists.

---

### 3.8 `[CODE]` Implement `backend/planner/service.py` — host school CRUD

Async functions: `list_host_schools(session, user_id)`, `create_host_school(session, user_id, data)`, `update_host_school(session, user_id, school_id, data)`, `delete_host_school(session, user_id, school_id)`. Every function must verify the school's `plan_id` belongs to `user_id`'s plan before reading/writing — no cross-user access via guessed IDs.

Test: extend `tests/planner/test_service.py` — CRUD round trip for one user; assert a second user cannot read/update/delete the first user's host school (raises a not-found/forbidden error, not a silent no-op).

---

### 3.9 `[CODE]` Implement `backend/planner/service.py` — course match CRUD

Same shape as `3.8` for `CourseMatch`, additionally scoped to an existing `host_school_id` owned by the same plan.

Test: extend `tests/planner/test_service.py` — same ownership-isolation pattern as `3.8`; assert creating a course match against another user's `host_school_id` fails.

---

### 3.10 `[CODE]` Implement `backend/api/routes/planner.py` — `GET /planner/plan`, `PATCH /planner/plan`

Both gated by `get_current_user`. `GET` calls `get_or_create_plan`; `PATCH` calls `update_plan`.

Test: `tests/api/test_planner.py` — `GET` without auth returns `401`; `GET` with auth returns a plan (creating one on first call); `PATCH` updates `current_phase` and the next `GET` reflects it.

---

### 3.11 `[CODE]` Add host school routes to `backend/api/routes/planner.py`

`GET /planner/host-schools`, `POST /planner/host-schools`, `PATCH /planner/host-schools/{id}`, `DELETE /planner/host-schools/{id}`.

Test: extend `tests/api/test_planner.py` — full CRUD round trip via the API; assert a second authenticated user gets `404`/`403` (not another user's data) when hitting the first user's `{id}`.

---

### 3.12 `[CODE]` Add course match routes to `backend/api/routes/planner.py`

`GET /planner/course-matches`, `POST /planner/course-matches`, `PATCH /planner/course-matches/{id}`, `DELETE /planner/course-matches/{id}`.

Test: extend `tests/api/test_planner.py` — same CRUD + isolation pattern as `3.11`.

---

### 3.13 `[CODE]` Wire the planner router into `backend/api/app.py`

Mount `planner.router`. Confirm no import or dependency reaches into `backend/retrieval/` or `backend/generation/` — the planner module must have zero coupling to the Mongo-backed RAG path, per `CLAUDE.md`'s isolation rule.

Test: `tests/api/test_app.py` — assert all `/planner/*` routes appear in the OpenAPI schema; a quick `grep` check (or a small static test) that `backend/planner/` imports nothing from `backend/retrieval` or `backend/generation`.

---

### 3.14 `[USER]` Manually exercise planner CRUD with two accounts

Using curl or the FastAPI Swagger UI (`/docs`) and two different `@uwaterloo.ca` test accounts:
1. Sign in as user A, create a host school and a course match.
2. Sign in as user B, confirm `GET /planner/host-schools` returns an empty list (not user A's data).
3. Attempt to `PATCH`/`DELETE` user A's host school ID while authenticated as user B — confirm it's rejected.

Report back: isolation confirmed, ready for Phase 4 frontend work.
