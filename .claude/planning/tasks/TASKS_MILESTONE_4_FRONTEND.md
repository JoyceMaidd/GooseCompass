# Milestone Phase 4 — Frontend (Auth, Quota, Planner)

Goal: sign-in flow, an authenticated chat experience with a quota indicator, and the exchange planner dashboard. UI/UX layout is explicitly loose for this milestone (per the description doc, detailed design is out of scope) — build functional components now; visual polish is a later pass.

**Prerequisite**: Phases 1–3 backend routes exist and are reachable (local dev is fine — Phase 5 deployment isn't required to build against `localhost:8000`).

Development order: auth client/hook → sign-in page → gate existing chat behind auth → quota indicator → planner client → planner components → routing.

---

### 4.1 `[CODE]` Implement `frontend/src/api/authClient.ts`

Two exported async functions:
- `requestCode(email: string): Promise<void>`
- `verifyCode(email: string, code: string): Promise<{ accessToken: string }>`

Test: unit test with mocked `fetch`; assert correct endpoints/bodies; assert a non-2xx response throws.

---

### 4.2 `[CODE]` Implement `frontend/src/hooks/useAuth.ts`

Manages:
- `accessToken: string | null` — persisted to `localStorage`, restored on load.
- `isAuthenticated: boolean`
- `login(email, code): Promise<void>` — calls `verifyCode`, stores the token.
- `logout(): void` — clears the token.

Test: `tests/hooks/useAuth.test.ts` — mock `authClient`; assert `login` sets `isAuthenticated` true and persists to storage; assert `logout` clears both.

---

### 4.3 `[CODE]` Implement `frontend/src/pages/SignInPage.tsx`

Two-step form: email entry → submit calls `requestCode` → code entry screen → submit calls `useAuth().login`. JSDoc on the component. Shows a clear error for non-`uwaterloo.ca` emails and for a wrong/expired code (surface the backend's error message).

Test: `tests/pages/SignInPage.test.tsx` — simulate entering an email and submitting, assert `requestCode` called; simulate entering a code, assert `login` called with both values.

---

### 4.4 `[CODE]` Update `frontend/src/api/client.ts` — attach auth token

`queryNonStreaming` and `queryStreaming` must send `Authorization: Bearer <token>` on every call (read from wherever `useAuth` persists it — likely via a shared accessor rather than a React hook, since `client.ts` is outside component context). On a `401` response, surface a distinct error so the caller can redirect to sign-in.

Test: extend `frontend/src/api/client.test.ts` — assert the `Authorization` header is present and correct; assert a mocked `401` response produces the distinct auth-error path.

---

### 4.5 `[CODE]` Implement `frontend/src/components/QuotaIndicator.tsx`

Props: `used: number`, `limit: number`, `period: string`. Simple readout of remaining quota (exact placement/design is explicitly TBD per the architecture doc — a basic always-visible readout is enough for this milestone). Fetches its data from `GET /monitoring/usage` scoped to the current user via a small `frontend/src/api/monitoringClient.ts` (new, minimal — one function: `getUsage(): Promise<UsageSummary>`).

Test: `tests/components/QuotaIndicator.test.tsx` — render with mock usage data; assert used/remaining values appear in the DOM; assert an over-limit state renders a distinct visual/text cue.

---

### 4.6 `[CODE]` Implement `frontend/src/api/plannerClient.ts`

Exported async functions mirroring the Phase 3 routes: `getPlan`, `updatePlan`, `listHostSchools`, `createHostSchool`, `updateHostSchool`, `deleteHostSchool`, `listCourseMatches`, `createCourseMatch`, `updateCourseMatch`, `deleteCourseMatch`. All authenticated the same way as `4.4`.

Test: unit test with mocked `fetch` — assert each function hits the correct endpoint/method/body and includes the auth header.

---

### 4.7 `[CODE]` Implement `frontend/src/types.ts` additions — planner types

Add TypeScript interfaces mirroring the Phase 3 Pydantic schemas: `ExchangePlan`, `HostSchool`, `CourseMatch`.

No test needed — TypeScript compilation is the test.

---

### 4.8 `[CODE]` Implement `frontend/src/components/planner/PhaseTracker.tsx`

Props: `currentPhase: string`, `checklistState: Record<string, boolean>`, `onPhaseChange`, `onChecklistToggle`. Renders the five TravelGoose phases (Info Session, Research, Apply, Course Matching, IC4E Session) plus the Next Steps checklist.

Test: render with mock data; assert the current phase is visually distinguished; simulate a checklist toggle, assert the callback fires with the right key.

---

### 4.9 `[CODE]` Implement `frontend/src/components/planner/HostSchoolTable.tsx`

Props: `schools: HostSchool[]`, `onCreate`, `onUpdate`, `onDelete`. Editable table with the fields from `3.2` (term dates, cost of living, language, competitiveness, course match, links, notes).

Test: render with mock rows; simulate an edit and a delete, assert the right callbacks fire with the right IDs/values.

---

### 4.10 `[CODE]` Implement `frontend/src/components/planner/CourseMatchTable.tsx`

Props: `matches: CourseMatch[]`, `hostSchools: HostSchool[]`, `onCreate`, `onUpdate`, `onDelete`. Editable table: core course → proposed host course → syllabus link → approval status → terms offered.

Test: render with mock rows; simulate an edit and a delete, assert the right callbacks fire.

---

### 4.11 `[CODE]` Implement `frontend/src/pages/PlannerPage.tsx`

Composes `plannerClient` + `PhaseTracker` + `HostSchoolTable` + `CourseMatchTable` + a free-text notes field per phase. Visually distinct container/styling from `ChatPage` per `CLAUDE.md`'s planner/RAG isolation rule (this data must read as clearly separate from grounded chat answers).

Test: integration render with mocked `plannerClient`; assert all sub-sections render; simulate a phase change, assert `updatePlan` is called.

---

### 4.12 `[CODE]` Wire routing in `frontend/src/App.tsx`

- Unauthenticated → `SignInPage`.
- Authenticated → nav between `ChatPage` (with `QuotaIndicator`) and `PlannerPage`.
- Use whatever router is already in the project, or a minimal state-based switch if none is installed yet — don't add a routing library if a simple conditional covers two pages (YAGNI).

Test: `tests/App.test.tsx` — unauthenticated render shows `SignInPage`; mock an authenticated `useAuth` state, assert `ChatPage` renders with nav to `PlannerPage`.

---

### 4.13 `[USER]` Full browser walkthrough

With backend (all phases) and frontend running:
1. Sign in with a real `@uwaterloo.ca` email — receive code, enter it, land in the app.
2. Ask a question in chat, confirm streaming + citations still work, confirm the quota indicator updates.
3. Exceed quota (if using a low test limit) and confirm the graceful limit-reached message renders in the chat UI.
4. Switch to the planner, add a host school and a course match, change phase, add notes, refresh the page and confirm everything persisted.
5. Sign out and back in, confirm the planner data is still there (proves it's server-persisted, not local-only).

Report back any issues — this is the final validation gate for the milestone's functionality before Phase 5 deployment.
