# Milestone Phase 1 — Authentication

Goal: `@uwaterloo.ca`-restricted OTP sign-in with JWT sessions, rate-limited, ready to gate every other new route.

**Prerequisite**: Phase 0 (Foundation) complete.

Development order: models → migration → OTP/rate-limit/email/JWT primitives → orchestration service → routes → dependency → wiring.

---

### 1.1 `[CODE]` Define `backend/users/models.py` — `User` model

SQLAlchemy model: `id (PK)`, `email (unique, indexed)`, `created_at`. Plus a Pydantic `UserRead` schema (`id`, `email`, `created_at`) for API responses.

Test: `tests/users/test_models.py` — assert the table name and column set match spec; assert `UserRead` validates from an ORM instance (`from_attributes=True`).

---

### 1.2 `[CODE]` Define `backend/auth/models.py` — `AuthCode` model

SQLAlchemy model: `id (PK)`, `user_id (FK -> users.id)`, `code_hash`, `expires_at`, `attempts (default 0)`, `created_at`.

Test: `tests/auth/test_models.py` — construct and assert defaults (`attempts == 0`).

---

### 1.3 `[CODE]` Define `backend/auth/models.py` — `RateLimit` model

SQLAlchemy model: `key (e.g. email or IP)`, `scope (e.g. "request-code" / "verify-code")`, `window_start`, `count`. Composite unique constraint on `(key, scope, window_start)`.

Test: `tests/auth/test_models.py` — assert the unique constraint exists on the table definition.

---

### 1.4 `[CODE]` Alembic migration for `users`, `auth_codes`, `rate_limits`

```bash
alembic revision --autogenerate -m "add users, auth_codes, rate_limits"
```

Review the generated migration by hand before applying — confirm FKs, indexes, and the `rate_limits` unique constraint are present.

Test: read the generated migration file; confirm `upgrade()`/`downgrade()` are both populated (not empty stubs).

---

### 1.5 `[USER]` Apply the migration

```bash
alembic upgrade head
```

Confirm the three tables exist in Postgres.

---

### 1.6 `[CODE]` Implement `backend/auth/otp.py` — code generation & hashing

Three functions:
- `generate_otp() -> str` — cryptographically random 6-digit code (`secrets` module, not `random`).
- `async hash_otp(code: str) -> str` — Argon2 hash, run via `asyncio.to_thread` (CPU-bound, per `CLAUDE.md`).
- `async verify_otp(code: str, code_hash: str) -> bool` — same `asyncio.to_thread` treatment.

Test: `tests/auth/test_otp.py` — assert `generate_otp()` is a 6-digit string; assert `verify_otp` returns `True` for the correct code and `False` for a wrong one; assert hashing two calls of the same code produce different hashes (salted).

---

### 1.7 `[CODE]` Implement `backend/auth/rate_limit.py` — Postgres-backed rate limiting

One async function:
- `check_and_increment(session, key: str, scope: str, limit: int, window_seconds: int) -> bool`

Computes the current window's `window_start`, upserts/increments the matching `rate_limits` row, returns `False` if `count > limit` after incrementing (caller treats `False` as "reject").

Test: `tests/auth/test_rate_limit.py` — call repeatedly under the limit, assert `True` each time; call one more over the limit, assert `False`; simulate a new window (mock time), assert the counter resets.

---

### 1.8 `[CODE]` Implement `backend/auth/email.py` — OTP email delivery

One async function:
- `async send_otp_code(to_email: str, code: str) -> None`

Calls the configured provider's REST API via `httpx.AsyncClient` (per `CLAUDE.md` — no provider SDK). Provider chosen at `M-3`; branch on `settings.email_provider` if you want to support more than one, otherwise hardcode the chosen provider's endpoint.

Test: `tests/auth/test_email.py` — mock `httpx.AsyncClient.post` (via `pytest-mock`); assert it's called once with the provider's endpoint, correct auth header, and the code embedded in the payload.

---

### 1.9 `[CODE]` Implement `backend/auth/jwt.py` — session tokens

Two functions (sync — JWT encode/decode is sub-millisecond, stays inline per `CLAUDE.md`):
- `create_access_token(user_id: int, expires_minutes: int = ...) -> str`
- `decode_access_token(token: str) -> dict` — raises on invalid/expired.

Test: `tests/auth/test_jwt.py` — round-trip encode/decode, assert `user_id` matches; assert an expired token raises; assert a tampered token raises.

---

### 1.10 `[CODE]` Implement `backend/auth/service.py` — `request_code` orchestration

One async function:
- `async request_code(session, email: str, client_ip: str) -> None`

Steps: validate `@uwaterloo.ca` domain (raise a typed exception otherwise) → rate-limit check per email and per IP (`1.7`) → get-or-create `User` row → generate + hash OTP (`1.6`) → store `AuthCode` row → send email (`1.8`).

Test: `tests/auth/test_service.py` — mock email sending; assert a `User` row is created for a new email; assert an `AuthCode` row exists with a non-plaintext `code_hash`; assert a non-`uwaterloo.ca` email raises before any DB writes; assert exceeding the rate limit raises without sending an email.

---

### 1.11 `[CODE]` Implement `backend/auth/service.py` — `verify_code` orchestration

One async function:
- `async verify_code(session, email: str, code: str, client_ip: str) -> str` (returns JWT)

Steps: rate-limit check → fetch latest non-expired `AuthCode` for the user → check `attempts < max_attempts` (else raise/invalidate) → `verify_otp` → on success issue JWT (`1.9`) and invalidate the code (delete or mark used); on failure increment `attempts` and raise.

Test: extend `tests/auth/test_service.py` — correct code returns a decodable JWT; wrong code raises and increments `attempts`; exceeding max attempts raises even with the correct code; expired code raises.

---

### 1.12 `[CODE]` Implement `backend/api/routes/auth.py` — `POST /auth/request-code`

Request body: `{ "email": "string" }`. Calls `request_code`. Returns `202 Accepted` with a generic message (never reveal whether the email existed before, to avoid enumeration).

Test: `tests/api/test_auth.py` — post a valid `@uwaterloo.ca` email, assert `202`; post a non-`uwaterloo.ca` email, assert `4xx` with a clear error.

---

### 1.13 `[CODE]` Add `POST /auth/verify-code` to `backend/api/routes/auth.py`

Request body: `{ "email": "string", "code": "string" }`. Calls `verify_code`. Returns `{ "access_token": "...", "token_type": "bearer" }` on success, `4xx` on failure.

Test: extend `tests/api/test_auth.py` — full round trip: request code (capture the hashed value via a test hook or query the DB directly for the raw code in test mode), verify it, assert `200` with a token; verify with a wrong code, assert `4xx`.

---

### 1.14 `[CODE]` Implement `backend/auth/dependency.py` — `get_current_user`

FastAPI dependency: extracts the bearer token, calls `decode_access_token`, loads the `User` row, raises `401` if missing/invalid/expired. This is what gates `/query`, `/query/stream`, and all `/planner/*` routes in later phases.

Test: `tests/auth/test_dependency.py` — valid token resolves to the right `User`; missing header raises `401`; expired/invalid token raises `401`.

---

### 1.15 `[CODE]` Wire the auth router into `backend/api/app.py`

Mount `auth.router`. No behavior change to existing routes yet.

Test: `tests/api/test_app.py` — assert `/auth/request-code` and `/auth/verify-code` appear in the OpenAPI schema.

---

### 1.16 `[USER]` End-to-end OTP email test

With the server running:
```bash
curl -X POST http://localhost:8000/auth/request-code -H "Content-Type: application/json" -d '{"email": "yourid@uwaterloo.ca"}'
```
Confirm you receive the email with a 6-digit code, then:
```bash
curl -X POST http://localhost:8000/auth/verify-code -H "Content-Type: application/json" -d '{"email": "yourid@uwaterloo.ca", "code": "123456"}'
```
Confirm a JWT comes back. Report any errors — this is the gate before Phase 2 and 3 can build on `get_current_user`.
