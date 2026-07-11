# Milestone Phase 5 — Deployment

Goal: backend live on Render, frontend live on Vercel, production Postgres and MongoDB both reachable, end-to-end smoke test passing in production.

**Prerequisite**: Phases 0–4 complete and working locally.

---

### 5.1 `[USER]` Create the Render web service (backend)

1. Connect the GitHub repo to Render.
2. Create a new Web Service pointing at the backend (build command installs the package, start command runs `uvicorn backend.api.app:app --host 0.0.0.0 --port $PORT`).
3. If not already using Render Postgres from `M-1`/Phase 0, provision it now and update `POSTGRES_URI` for the production environment.
4. This is `M-7`.

---

### 5.2 `[CODE]` Ensure migrations run on deploy

Add a release/build step (Render's "Build Command" or a pre-deploy hook, whichever the plan supports) that runs `alembic upgrade head` before the new instance starts serving traffic. Document the exact command in `CLAUDE.md`'s deployment notes or a `docs/deploy.md`.

Test: locally simulate the same sequence (`alembic upgrade head` then start `uvicorn`) against a fresh Postgres database and confirm it comes up clean with no manual steps.

---

### 5.3 `[USER]` Set production environment variables on Render

Set all of: `MONGODB_URI`, `MONGODB_DB_NAME`, `MONGODB_COLLECTION_CHUNKS`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `OPENROUTER_GENERATION_MODEL`, `OPENROUTER_REWRITER_MODEL`, `POSTGRES_URI`, `JWT_SECRET`, `EMAIL_PROVIDER`, `EMAIL_API_KEY`, `EMAIL_FROM`, `FRONTEND_ORIGIN` (set to the Vercel production URL once known from `5.4`).

Use a distinct `JWT_SECRET` from local dev — do not reuse the dev value in production.

---

### 5.4 `[USER]` Create the Vercel project (frontend)

1. Connect the GitHub repo to Vercel, root directory `frontend/`.
2. Set `VITE_API_URL` to the Render backend's production URL.
3. Deploy and note the resulting production URL.

---

### 5.5 `[CODE]` Confirm CORS covers the production frontend origin

Update the deployed backend's `FRONTEND_ORIGIN` (from `5.3`) to the Vercel URL from `5.4`. If preview deployments need to work too, confirm whether the existing CORS config (`FRONTEND_ORIGIN`, singular, per current `CLAUDE.md`) supports multiple/wildcard origins or needs extending to a comma-separated list — small, targeted change, not a rearchitecture.

Test: `tests/api/test_cors.py` — extend if the config shape changes; otherwise confirm the existing test still passes with the new value.

---

### 5.6 `[USER]` Production smoke test

Against the live Vercel URL:
1. Sign in with a real `@uwaterloo.ca` email end-to-end (real OTP email delivery in production).
2. Ask a chat question, confirm streaming + citations work against production MongoDB.
3. Confirm the quota indicator reflects real usage.
4. Add a host school / course match in the planner, refresh, confirm persistence against production Postgres.
5. Check Render logs for the request confirm `request_logs`/`usage_logs` rows are being written (spot-check via `psql` or a GUI client).

Report back: production deployment confirmed working, or list what broke.
