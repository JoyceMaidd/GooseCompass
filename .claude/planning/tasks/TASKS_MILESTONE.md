# GooseCompass — Milestone Build Plan: Platform Expansion

Auth, Usage Tracking, System Monitoring, Exchange Planner, and Deployment — built on top of the existing RAG MVP (`TASKS_MVP.md`), which is untouched by this milestone.

Each task is one small, reviewable unit of work. Complete and confirm each task before starting the next, per `CLAUDE.md`'s task discipline rule (ONE task at a time, stop for review).

**Legend**
- `[CODE]` — implementation task (always followed by its test before marking done)
- `[USER]` — requires your manual action or decision before work can continue
- `[INFO]` — information you must supply so implementation can proceed

This milestone is too large for one file. It is split by module, matching the architecture's separation of concerns (`auth/`, `monitoring/`, `planner/`, frontend, deployment). Work through the files in this order:

| File | Covers | Depends on |
|---|---|---|
| [TASKS_MILESTONE_0_FOUNDATION.md](TASKS_MILESTONE_0_FOUNDATION.md) | Postgres setup, SQLAlchemy/Alembic wiring, `db.py` extension, shared config | MVP Phase 0 |
| [TASKS_MILESTONE_1_AUTH.md](TASKS_MILESTONE_1_AUTH.md) | `users`, `auth_codes`, `rate_limits` tables; OTP request/verify; JWT sessions; auth dependency | Foundation |
| [TASKS_MILESTONE_2_MONITORING.md](TASKS_MILESTONE_2_MONITORING.md) | `usage_logs`, `request_logs`; quota enforcement; usage/request logging middleware; query routes gated by auth+quota | Auth |
| [TASKS_MILESTONE_3_PLANNER.md](TASKS_MILESTONE_3_PLANNER.md) | `exchange_plans`, `host_schools`, `course_matches`; planner CRUD routes | Auth |
| [TASKS_MILESTONE_4_FRONTEND.md](TASKS_MILESTONE_4_FRONTEND.md) | Sign-in UI, quota indicator, exchange planner dashboard UI | Auth, Monitoring, Planner APIs |
| [TASKS_MILESTONE_5_DEPLOYMENT.md](TASKS_MILESTONE_5_DEPLOYMENT.md) | Render backend deploy, Vercel frontend deploy, production env config | All above |

Modules are independently developable once Foundation is done — Auth must land first since Monitoring and Planner both depend on the `users` table and the auth dependency. Frontend work per screen can start as soon as its corresponding backend routes exist.

---

## Before We Start — Information You Must Provide

Collect these before Phase 0 (Foundation) begins.

| # | What | Why needed |
|---|------|------------|
| M-1 | Postgres connection URI (`postgresql+asyncpg://...`) — Render managed Postgres or other | `POSTGRES_URI` config |
| M-2 | JWT signing secret (generate a random 32+ byte value) | `JWT_SECRET` config |
| M-3 | Email provider choice (Resend, SendGrid, or Postmark) + API key | `EMAIL_PROVIDER`, `EMAIL_API_KEY` |
| M-4 | Verified "from" email address/domain with the chosen provider | `EMAIL_FROM` |
| M-5 | OTP policy numbers: code TTL (5–10 min), max verify attempts (3–5), request rate limit (e.g. 3/email/hour) | Auth rate-limiting config |
| M-6 | Quota numbers: daily and/or monthly token/request limit per user | Quota enforcement config |
| M-7 | Render account + Vercel account access | Deployment (Phase 5) |

---

## Summary — User Actions Checklist

See each phase file for full detail; consolidated here for tracking.

| Task | Action |
|------|--------|
| M-1 to M-7 | Gather credentials/config before starting |
| 0.1 | Provision Postgres instance |
| 0.5 | Fill in new `.env` values |
| 1.9 | Send yourself a real OTP email end-to-end |
| 2.7 | Verify quota block behavior manually |
| 3.7 | Manually exercise planner CRUD via curl/Swagger |
| 4.8 | Full browser walkthrough: sign in → chat → planner |
| 5.1–5.6 | Render + Vercel deployment and production smoke test |
