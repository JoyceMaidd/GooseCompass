# Milestone: Platform Expansion — Auth, Usage Tracking & Exchange Planner

## Overview

GooseCompass moves from a single-user MVP (RAG Q&A only) to a deployed platform available to all UWaterloo students.

This milestone adds three capabilities on top of the existing RAG pipeline:

* Authenticated access restricted to `@uwaterloo.ca` emails
* Per-user token usage tracking with quotas
* A self-service exchange planner (adapted from the existing TravelGoose spreadsheet workflow) that lets students track their application progress alongside asking the RAG assistant questions

Detailed UI/UX design is explicitly out of scope for this milestone and will be specified separately; this milestone only defines *which* UI-facing features exist, not their layout or visuals.

WatIAM/institutional SSO is also out of scope — auth uses email + one-time code instead.

---

# MVP Scope — Features

## Authentication

* Restrict sign-in to `@uwaterloo.ca` email addresses
* One-time code (OTP) sent via email; no password
* Session issued as JWT after successful code verification
* Rate limiting on code requests and verification attempts

---

## Usage Tracking & Quotas

* Every `/query` and `/query/stream` call logs prompt tokens, completion tokens, and an estimated cost per user
* Per-user quota (daily and/or monthly) enforced before invoking the LLM
* Graceful "limit reached" response when exceeded

---

## System Monitoring

* Token usage logs queryable per user and in aggregate (for the operator to watch spend)
* Basic system behavior logging: request outcomes, errors, and latency for the retrieval/generation pipeline, so failures and slow queries are visible without needing to reproduce them

---

## Exchange Planner (adapted from TravelGoose)

* Phase-based progress tracker mirroring TravelGoose's five phases (Info Session, Research, Apply, Course Matching, IC4E Session) plus a Next Steps checklist
* Host school research table (term dates, cost of living, language, competitiveness, course match, links, notes) — user-editable, stored per user
* Course matching table (core course → proposed host course → syllabus link → approval status → terms offered)
* Free-text notes per phase
* This data is explicitly **not** fed into the RAG retrieval layer — it's the student's own working notes, not institutional source material, and must stay visually/architecturally distinct from grounded answers

---

## Deployment

* Backend on Render
* Frontend on Vercel
* Existing MongoDB Atlas retained for RAG
* New Postgres instance for everything else

---

## Out of Scope

* UI/UX design and layout (feature list only for this milestone)
* WatIAM / institutional SSO
