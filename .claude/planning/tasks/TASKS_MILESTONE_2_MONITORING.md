# Milestone Phase 2 — Usage Tracking, Quotas & System Monitoring

Goal: every `/query` and `/query/stream` call is quota-checked before the LLM runs and logged afterward without adding response latency; all routes get basic request logging.

**Prerequisite**: Phase 1 (Auth) complete — this phase relies on `get_current_user`.

Development order: models → migration → quota logic → logging writers → middleware/wiring into existing routes → operator query endpoint.

---

### 2.1 `[CODE]` Define `backend/monitoring/models.py` — `UsageLog` model

SQLAlchemy model: `id (PK)`, `user_id (FK -> users.id)`, `endpoint`, `prompt_tokens`, `completion_tokens`, `estimated_cost`, `created_at`.

Test: `tests/monitoring/test_models.py` — construct and assert field types/defaults.

---

### 2.2 `[CODE]` Define `backend/monitoring/models.py` — `RequestLog` model

SQLAlchemy model: `id (PK)`, `user_id (nullable FK — some requests are pre-auth)`, `endpoint`, `status`, `latency_ms`, `error (nullable)`, `created_at`.

Test: extend `tests/monitoring/test_models.py`.

---

### 2.3 `[CODE]` Alembic migration for `usage_logs`, `request_logs`

```bash
alembic revision --autogenerate -m "add usage_logs, request_logs"
```

Test: confirm `upgrade()`/`downgrade()` are populated; review indexes on `user_id` and `created_at` (both tables will be queried by user and by time range).

---

### 2.4 `[USER]` Apply the migration

```bash
alembic upgrade head
```

---

### 2.5 `[CODE]` Implement `backend/monitoring/quota.py` — quota computation

Two functions:
- `async get_usage_for_period(session, user_id: int, period: str) -> int` — sums tokens (or request count — decide which unit the quota is denominated in) from `usage_logs` for `"daily"` or `"monthly"`, computed on the fly (per the architecture doc's "decide during implementation" note — computed-from-`usage_logs` is simpler than a separately maintained counter table and avoids a second write path to keep in sync).
- `async check_quota(session, user_id: int) -> bool` — compares against the configured limit(s) from `M-6`; returns `False` if over.

Test: `tests/monitoring/test_quota.py` — insert usage rows under/over the limit; assert `check_quota` returns `True`/`False` correctly; assert a "daily" query doesn't count rows from yesterday.

---

### 2.6 `[CODE]` Implement `backend/monitoring/usage.py` — usage log writer

One async function:
- `async log_usage(session, user_id: int, endpoint: str, prompt_tokens: int, completion_tokens: int, estimated_cost: float) -> None`

Plain insert — no business logic. Designed to be called from a `BackgroundTasks` callback, not awaited on the response path.

Test: `tests/monitoring/test_usage.py` — call it, assert a row lands in `usage_logs` with the right values.

---

### 2.7 `[CODE]` Implement `backend/monitoring/request_log.py` — request log writer

One async function:
- `async log_request(session, user_id: int | None, endpoint: str, status: int, latency_ms: float, error: str | None) -> None`

Same shape as `2.6`.

Test: `tests/monitoring/test_request_log.py` — call it, assert a row lands in `request_logs`.

---

### 2.8 `[CODE]` Implement request logging as a FastAPI middleware

`backend/api/middleware.py` — an ASGI middleware (or `@app.middleware("http")` handler) wrapping every request: times it, captures status/exceptions, and schedules `log_request` to run after the response is sent (use `BackgroundTasks` if attachable at the middleware layer, or a fire-and-forget `asyncio.create_task` with an eat-the-exception wrapper if `BackgroundTasks` isn't reachable from middleware — pick whichever keeps the write off the response path, matching `CLAUDE.md`'s logging rule).

Test: `tests/api/test_middleware.py` — hit `/health`; assert a `request_logs` row is written with status `200` and a plausible `latency_ms`; hit a route that raises, assert a row with the error captured.

---

### 2.9 `[CODE]` Gate `/query` with auth + quota, log usage via `BackgroundTasks`

Update `backend/api/routes/query.py`:
- Add `current_user: User = Depends(get_current_user)`.
- Before calling the generation pipeline, call `check_quota`; if over, return a graceful structured "limit reached" response (not a raw `4xx` — matches the `GeneratedResponse`-shaped contract the frontend expects) **without** invoking the LLM.
- On success, schedule `log_usage` via `BackgroundTasks` with the token counts returned by the generation call.

Test: extend `tests/api/test_query.py` — request without a token, assert `401`; request under quota, assert `200` and a `usage_logs` row appears after the response (poll or check post-response); request when already over quota (seed usage rows in test setup), assert a graceful limit-reached body and **no** LLM call (mock the generation pipeline and assert it was not invoked).

---

### 2.10 `[CODE]` Gate `/query/stream` with auth + quota, log usage after the final chunk

Same quota check before streaming starts. Schedule `log_usage` after the final SSE event is sent (either via `BackgroundTasks` on the streaming response or a callback at stream close — confirm the token counts from the streamed generation are available at that point).

Test: extend `tests/api/test_stream.py` — assert quota-exceeded returns immediately without opening a stream; assert a successful stream still produces a `usage_logs` row after completion.

---

### 2.11 `[CODE]` Implement `backend/api/routes/monitoring.py` — operator query endpoint

`GET /monitoring/usage` — returns usage aggregated per user and in total, for a given period. Auth-gated at minimum (`get_current_user`); no separate operator-role system exists yet, so document this as a known gap if you want stricter access control, or restrict by a hardcoded operator email list read from config — confirm approach with the user before building, since this is a judgment call not specified in the architecture doc.

Test: `tests/api/test_monitoring.py` — seed usage rows for two users; assert the aggregate endpoint returns correct per-user and total sums.

---

### 2.12 `[USER]` Confirm quota numbers and limit-reached copy

Confirm the daily/monthly limit values (`M-6`) and the exact wording shown to a user who hits the limit (surfaces in the frontend in Phase 4).

---

### 2.13 `[USER]` Manually verify quota enforcement

With the server running and a low test quota configured, send `/query` requests past the limit via curl. Confirm:
- Requests under quota succeed normally.
- The request that crosses the limit gets the graceful limit-reached response, not an error and not a real LLM call (check your OpenRouter usage dashboard doesn't tick up).

Report back any issues before Phase 4 wires the frontend quota indicator to this data.
