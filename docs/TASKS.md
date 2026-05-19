# GooseCompass — Phased Build Plan

Each task is one small, reviewable unit of work. Complete and confirm each task before starting the next.

**Legend**
- `[CODE]` — implementation task (always followed by its test before marking done)
- `[USER]` — requires your manual action or decision before work can continue
- `[INFO]` — information you must supply so implementation can proceed

---

## Before We Start — Information You Must Provide

Collect these before Phase 0 begins. They determine `.env` values and config.

| # | What | Why needed |
|---|------|------------|
| I-1 | MongoDB Atlas cluster URI (`mongodb+srv://...`) | Database connection |
| I-2 | MongoDB database name (e.g. `goosecompass`) | Namespace isolation |
| I-3 | MongoDB collection name for chunks (e.g. `chunks`) | Storage target |
| I-4 | OpenAI API key | Embeddings (text-embedding-3-small) |
| I-5 | OpenRouter API key | LLM calls (query rewriting + generation) |
| I-6 | OpenRouter model ID for generation (e.g. `google/gemini-2.0-flash-001`) | Generation config |
| I-7 | OpenRouter model ID for query rewriting (can be same or a cheaper model) | Rewriter config |
| I-8 | Source list file — URLs and/or PDF paths to ingest (see Phase 1 format) | Ingestion data |

---

## Phase 0 — Project Setup

Goal: runnable skeleton with verified MongoDB connection and all dependencies installed.

### 0.1 `[USER]` Create MongoDB Atlas cluster

1. Sign up / log in at [cloud.mongodb.com](https://cloud.mongodb.com).
2. Create a **free M0** cluster (or M10+ for production vector search performance).
3. Under **Security → Database Access**: create a database user with read/write privileges.
4. Under **Security → Network Access**: add your IP (or `0.0.0.0/0` for dev).
5. Copy the **connection string** → this is `I-1`.

> Note: Vector Search requires at least M10 or Serverless in Atlas. M0 supports it in limited preview — if vector search fails on M0, upgrade to M10.

---

### 0.2 `[CODE]` Create `pyproject.toml` with all dependencies

File: `pyproject.toml` (project root)

Dependencies to include:
- `fastapi`, `uvicorn[standard]`
- `motor` (async MongoDB driver)
- `pymongo`
- `pydantic`, `pydantic-settings`
- `pydantic-ai` (PydanticAI)
- `openai` (embeddings)
- `docling` (document processing + chunking)
- `httpx` (async HTTP)
- `python-dotenv`
- `pytest`, `pytest-asyncio`, `pytest-mock` (dev deps)

Test: `pip install -e ".[dev]"` completes without errors.

---

### 0.3 `[CODE]` Create `.env.example` with all required variables

File: `.env.example`

```
MONGODB_URI=
MONGODB_DB_NAME=
MONGODB_COLLECTION_CHUNKS=
OPENAI_API_KEY=
OPENROUTER_API_KEY=
OPENROUTER_GENERATION_MODEL=
OPENROUTER_REWRITER_MODEL=
```

No test needed — this is a template file.

---

### 0.4 `[USER]` Fill in `.env` from `.env.example`

Copy `.env.example` → `.env` and fill in all values from `I-1` through `I-7`.
Confirm the file is listed in `.gitignore` before committing anything.

---

### 0.5 `[CODE]` Create project directory skeleton

Create all `__init__.py` files so imports work:

```
backend/
  __init__.py
  ingestion/__init__.py
  retrieval/__init__.py
  generation/__init__.py
  api/__init__.py
  tests/
    __init__.py
    ingestion/__init__.py
    retrieval/__init__.py
    generation/__init__.py
    api/__init__.py
scripts/
  __init__.py
```

Test: `python -c "import backend"` succeeds.

---

### 0.6 `[CODE]` Implement `backend/config.py` — settings loader

Use `pydantic-settings` to load and validate all env vars from `.env`.
Export a single `Settings` instance used across the entire backend.

Test: `tests/test_config.py` — assert all required fields are loaded and non-empty when `.env` is present; assert `ValidationError` is raised when a required field is missing.

---

### 0.7 `[CODE]` Implement `backend/db.py` — async MongoDB client

Async Motor client with a `get_database()` function and `lifespan`-compatible open/close.
Returns the database handle; callers get collection handles from it.

Test: `tests/test_db.py` — assert connection succeeds and `ping` command returns `{"ok": 1.0}`.

---

## Phase 1 — Ingestion Pipeline

Goal: given a list of source URLs/PDFs, produce embedded chunks stored in MongoDB.

Development order within this phase: models → fetch → chunk → embed → store → CLI.

---

### 1.1 `[CODE]` Define `backend/ingestion/models.py` — Chunk Pydantic model

Fields per chunk (matches what MongoDB stores):
- `chunk_id: str` — stable hash of `(source_url, chunk_index)`
- `content: str`
- `embedding: list[float]`
- `source_url: str`
- `document_title: str`
- `section_title: str`
- `document_type: str` — `"web"` or `"pdf"`
- `chunk_index: int`

Test: `tests/ingestion/test_models.py` — construct a valid `Chunk`, assert field types; assert `ValidationError` on missing required field.

---

### 1.2 `[CODE]` Implement `backend/ingestion/loader.py` — document fetching

Two async functions:
- `load_url(url: str) -> DoclingDocument` — fetches and parses a web URL via Docling.
- `load_pdf(path: str) -> DoclingDocument` — loads and parses a local PDF via Docling.

Test: `tests/ingestion/test_loader.py` — load a known public URL (e.g. UWaterloo exchange page) and assert the returned document has non-empty content; load a small local test PDF and assert the same.

---

### 1.3 `[CODE]` Implement `backend/ingestion/chunker.py` — hybrid chunking

One async function:
- `chunk_document(doc: DoclingDocument, source_meta: dict) -> list[ChunkData]`

Uses Docling's built-in hybrid chunker. Returns a list of `ChunkData` (content + extracted metadata). Does **not** embed — embedding is separate.

Test: `tests/ingestion/test_chunker.py` — chunk the test URL/PDF from 1.2; assert output is a non-empty list; assert each item has non-empty `content` and populated metadata fields.

---

### 1.4 `[CODE]` Implement `backend/ingestion/embedder.py` — chunk embedding

One async function:
- `embed_chunks(chunks: list[ChunkData]) -> list[Chunk]`

Calls OpenAI `text-embedding-3-small` in batches (max 100 per API call). Attaches embedding to each chunk and returns fully populated `Chunk` models.

Test: `tests/ingestion/test_embedder.py` — embed a list of 2–3 short strings; assert each returns a vector of length 1536; assert no chunk has an empty embedding.

---

### 1.5 `[CODE]` Implement `backend/ingestion/store.py` — MongoDB upsert

One async function:
- `upsert_chunks(chunks: list[Chunk], collection) -> int`

Upserts by `chunk_id` (replace if exists, insert if new). Returns count of upserted documents.

Test: `tests/ingestion/test_store.py` — upsert 3 chunks; assert count == 3; upsert same 3 again; assert no duplicates (count in collection still 3).

---

### 1.6 `[CODE]` Implement `backend/ingestion/pipeline.py` — unified orchestrator

One async function:
- `ingest_source(source: dict, db) -> int`

where `source = {"url": "...", "type": "web"}` or `{"path": "...", "type": "pdf"}`.

Calls `load_*` → `chunk_document` → `embed_chunks` → `upsert_chunks` in sequence. Returns chunk count ingested.

Test: `tests/ingestion/test_pipeline.py` — run the full pipeline on one URL; assert chunks are present in the (test) MongoDB collection.

---

### 1.7 `[USER]` Provide source list — `scripts/sources.json`

Create `scripts/sources.json` with the URLs and PDFs to ingest. Format:

```json
[
  { "type": "web", "url": "https://uwaterloo.ca/international/..." },
  { "type": "web", "url": "https://uwaterloo.ca/international/..." },
  { "type": "pdf", "path": "docs/sources/some_policy.pdf" }
]
```

Start with 5–10 sources for initial validation. More can be added later.

---

### 1.8 `[CODE]` Implement `scripts/ingest.py` — ingestion CLI

Reads `scripts/sources.json`, runs `ingest_source` for each entry concurrently (via `asyncio.gather`), prints progress and total chunks stored.

Test: run `python scripts/ingest.py --dry-run` (print sources, skip ingestion); confirm output lists all sources.

---

### 1.9 `[USER]` Run ingestion and verify data

```bash
python scripts/ingest.py
```

Then in MongoDB Atlas Data Explorer, confirm:
- Documents exist in the chunks collection.
- Each document has `content`, `source_url`, `embedding` (1536 floats), and metadata fields.

Report back: how many chunks were created?

---

## Phase 2 — Retrieval Pipeline

Goal: given a query string, return a ranked, fused list of the most relevant chunks.

**Prerequisite**: complete ingestion (Phase 1) before creating indexes.

---

### 2.1 `[USER]` Create MongoDB Vector Search index

In Atlas UI → **Search → Create Search Index → Atlas Vector Search (JSON editor)**:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    }
  ]
}
```

Index name: `vector_index`. Target: your chunks collection. Wait for status = **Active**.

---

### 2.2 `[USER]` Create MongoDB Atlas Search index

In Atlas UI → **Search → Create Search Index → Atlas Search (JSON editor)**:

```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "content": { "type": "string", "analyzer": "lucene.standard" },
      "document_title": { "type": "string" },
      "section_title": { "type": "string" }
    }
  }
}
```

Index name: `text_index`. Same collection. Wait for status = **Active**.

---

### 2.3 `[CODE]` Implement `backend/retrieval/models.py` — SearchResult model

```python
class SearchResult:
    chunk_id: str
    content: str
    source_url: str
    document_title: str
    section_title: str
    score: float
```

Test: `tests/retrieval/test_models.py` — construct and validate.

---

### 2.4 `[CODE]` Implement `backend/retrieval/vector_search.py`

One async function:
- `vector_search(query_embedding: list[float], collection, k: int = 20) -> list[SearchResult]`

Uses MongoDB `$vectorSearch` aggregation stage. Returns top-`k` results with scores.

Test: `tests/retrieval/test_vector_search.py` — run against real Atlas collection with a known query; assert result list is non-empty and all results have non-empty `content`.

---

### 2.5 `[CODE]` Implement `backend/retrieval/text_search.py`

One async function:
- `text_search(query: str, collection, k: int = 20) -> list[SearchResult]`

Uses MongoDB `$search` aggregation stage (Atlas Search). Returns top-`k` results with scores.

Test: `tests/retrieval/test_text_search.py` — same pattern as 2.4 with a keyword-heavy query.

---

### 2.6 `[CODE]` Implement `backend/retrieval/rrf.py` — Reciprocal Rank Fusion

One pure function (no I/O, no async needed):
- `reciprocal_rank_fusion(results_a: list[SearchResult], results_b: list[SearchResult], k: int = 60) -> list[SearchResult]`

Standard RRF formula: `score = Σ 1 / (k + rank)`. Deduplicates by `chunk_id`. Returns merged list sorted by fused score descending.

Test: `tests/retrieval/test_rrf.py` — construct two toy ranked lists with known overlaps; assert fused list order matches expected RRF output; assert no duplicates.

---

### 2.7 `[CODE]` Implement `backend/retrieval/pipeline.py` — parallel retrieval orchestrator

One async function:
- `retrieve(query: str, query_embedding: list[float], collection, top_k: int = 10) -> list[SearchResult]`

Runs `vector_search` and `text_search` concurrently with `asyncio.gather`, then applies `rrf`, then returns top-`top_k` chunks.

Test: `tests/retrieval/test_pipeline.py` — run against Atlas; assert 10 results returned; assert results have content and source URLs.

---

### 2.8 `[CODE]` Implement `scripts/validate_retrieval.py` — CLI validation tool

Interactive loop: accepts a query string, prints the top-10 retrieved chunks (content preview + source URL + score), then prompts for another query. Exit with `q`.

Test: run the script manually with 3–4 representative user questions (see 2.9).

---

### 2.9 `[USER]` Validate retrieval quality

Run `python scripts/validate_retrieval.py` with at least these queries:
1. "What GPA do I need to apply for exchange?"
2. "What documents are required for the exchange application?"
3. "What are the housing options at [a partner university you ingested]?"

For each result: do the top chunks actually answer the question? Are sources correct?

Report back: any queries returning irrelevant results? We'll tune from there.

---

## Phase 3 — Generation Pipeline

Goal: given a user query and retrieved context, produce a grounded, cited answer.

---

### 3.1 `[CODE]` Define `backend/generation/models.py` — response schema

```python
class CitedParagraph:
    text: str
    citations: list[str]  # source URLs referenced in this paragraph

class GeneratedResponse:
    paragraphs: list[CitedParagraph]
    insufficient_context: bool  # True if context was not enough to answer
```

Test: `tests/generation/test_models.py` — construct and validate both models; assert `insufficient_context` defaults to `False`.

---

### 3.2 `[CODE]` Implement `backend/generation/rewriter.py` — query rewriter

One async function:
- `rewrite_query(query: str) -> str`

Calls the rewriter LLM via OpenRouter (model from config). Rewrites the user query into retrieval-optimized form. System prompt: rewrite to improve recall for institutional documentation; return only the rewritten query.

Example: `"Can I go to ETH if my grades are average?"` → `"ETH Zurich exchange eligibility GPA requirements University of Waterloo"`

Test: `tests/generation/test_rewriter.py` — rewrite a conversational query; assert output is non-empty, shorter/denser than the original, and does not contain hedging language.

---

### 3.3 `[CODE]` Implement `backend/generation/prompt.py` — prompt builder

One pure function:
- `build_prompt(query: str, context_chunks: list[SearchResult]) -> str`

Assembles the final prompt with:
1. System instruction: answer strictly from provided context; if context is insufficient, say so explicitly; cite sources at the end of each paragraph.
2. Context section: numbered chunks with source URL.
3. User query.

Test: `tests/generation/test_prompt.py` — build a prompt with 3 mock chunks; assert all chunk contents appear in the output; assert system grounding instruction is present.

---

### 3.4 `[CODE]` Implement `backend/generation/agent.py` — PydanticAI agent

Set up a PydanticAI `Agent` with:
- OpenRouter as the provider
- `GeneratedResponse` as the result type
- System prompt from `build_prompt`

One async function:
- `generate_response(prompt: str) -> GeneratedResponse`

Test: `tests/generation/test_agent.py` — call with a prompt containing 2 mock context chunks and a simple question; assert response has at least one paragraph; assert `insufficient_context` is False.

---

### 3.5 `[CODE]` Implement `backend/generation/pipeline.py` — full generation orchestrator

One async function:
- `answer(query: str, context_chunks: list[SearchResult]) -> GeneratedResponse`

Calls `build_prompt` then `generate_response`. Does not call the rewriter or retrieval — those are upstream concerns.

Test: `tests/generation/test_pipeline.py` — end-to-end with real context chunks (from retrieval); assert a non-empty grounded response.

---

### 3.6 `[CODE]` Implement `scripts/validate_generation.py` — end-to-end CLI

Interactive loop: accepts a query → rewrites → retrieves → generates → prints paragraphs with citations. Useful for evaluating full pipeline before the API layer.

Test: run manually with the same queries from 2.9.

---

### 3.7 `[USER]` Evaluate generation quality

Run `python scripts/validate_generation.py` with 5 representative queries. For each answer, check:
- Is the answer grounded (no hallucinated facts)?
- Are citations correct (point to the chunks that support the claim)?
- Does it refuse appropriately when context is insufficient?

Report back: any responses that feel wrong or uncited. We'll tune the prompt.

---

## Phase 4 — API Layer

Goal: expose the full RAG pipeline as a FastAPI service, first non-streaming then streaming.

---

### 4.1 `[CODE]` Implement `backend/api/app.py` — FastAPI app with lifespan

Lifespan opens the MongoDB connection on startup and closes it on shutdown.
Mount all routers here.

Test: `tests/api/test_app.py` — use `httpx.AsyncClient` to call `GET /health`; assert `200 OK` and `{"status": "ok"}`.

---

### 4.2 `[CODE]` Implement `backend/api/routes/query.py` — `POST /query` (non-streaming)

Request body:
```json
{ "query": "string", "session_history": [] }
```

Response body: `GeneratedResponse` as JSON.

Full pipeline: rewrite → embed → retrieve → generate → return.

Test: `tests/api/test_query.py` — post a real query; assert 200 with paragraphs and at least one citation.

---

### 4.3 `[CODE]` Add `POST /query/stream` — SSE streaming endpoint

Same pipeline as 4.2 but streams tokens via `text/event-stream`. Each SSE event is a token chunk. Final event includes the full citation list.

Test: `tests/api/test_stream.py` — consume the stream; assert token events arrive before the final citation event; reconstruct full text and assert it's non-empty.

---

### 4.4 `[CODE]` Configure CORS

Allow the frontend origin (configurable via `FRONTEND_ORIGIN` env var, default `http://localhost:5173`). Add to `.env.example`.

Test: `tests/api/test_cors.py` — send a preflight `OPTIONS` request; assert `Access-Control-Allow-Origin` header is present.

---

### 4.5 `[USER]` Smoke-test the API manually

Start the server:
```bash
uvicorn backend.api.app:app --reload
```

Then test with curl:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What GPA do I need for exchange?", "session_history": []}'
```

Confirm the response is valid JSON with paragraphs and citations. Report any errors.

---

### 4.6 `[CODE]` Update `CLAUDE.md` dev commands section

Fill in the now-known commands: `uvicorn`, `pytest`, env setup instructions.

---

## Phase 5 — Frontend

Goal: single-page chat UI with streaming responses and inline citations.

---

### 5.1 `[CODE]` Scaffold React + TypeScript app with Vite

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install
```

Add `VITE_API_URL` to `.env.example` (default: `http://localhost:8000`).

Test: `npm run dev` starts without errors; blank page loads at `localhost:5173`.

---

### 5.2 `[CODE]` Implement `frontend/src/api/client.ts` — API client

Two exported async functions:
- `queryNonStreaming(query: string): Promise<GeneratedResponse>`
- `queryStreaming(query: string, onToken: (token: string) => void, onDone: (citations: string[]) => void): Promise<void>`

Uses `fetch` with `EventSource` / `ReadableStream` for streaming.

Test: unit test with mocked `fetch`; assert `onToken` is called for each event, `onDone` called with citations at end.

---

### 5.3 `[CODE]` Implement `frontend/src/types.ts` — shared TypeScript types

Mirror `GeneratedResponse`, `CitedParagraph` as TypeScript interfaces.

No test needed — TypeScript compilation is the test.

---

### 5.4 `[CODE]` Implement `frontend/src/components/ChatMessage.tsx`

Props: `paragraphs: CitedParagraph[]`, `role: "user" | "assistant"`.

Renders each paragraph followed by its citation links (superscript style). JSDoc on the component.

Test: render with mock data using Vitest + React Testing Library; assert paragraphs and citation links appear in the DOM.

---

### 5.5 `[CODE]` Implement `frontend/src/components/ChatInput.tsx`

Props: `onSubmit: (query: string) => void`, `disabled: boolean`.

Text area + submit button. Submits on Enter (Shift+Enter for newline). Clears on submit.

Test: simulate typing and pressing Enter; assert `onSubmit` called with correct string.

---

### 5.6 `[CODE]` Implement `frontend/src/hooks/useChat.ts`

Manages:
- `messages: Message[]` — full chat history for this session
- `isLoading: boolean`
- `sendMessage(query: string): void` — calls streaming API, appends tokens to last assistant message, finalizes with citations

Test: mock `queryStreaming`; assert messages array grows correctly; assert `isLoading` transitions.

---

### 5.7 `[CODE]` Implement `frontend/src/pages/ChatPage.tsx`

Composes `useChat` + `ChatMessage` + `ChatInput`. Auto-scrolls to bottom on new message.

Test: integration render; send a message via mocked hook; assert assistant message appears.

---

### 5.8 `[USER]` End-to-end browser test

With both backend and frontend running:
1. Ask: "What are the housing options at [a partner university]?"
2. Watch streaming tokens arrive.
3. Confirm citations appear at the bottom of paragraphs.
4. Ask a second question in the same session.
5. Ask something off-topic (e.g., "What's the weather?") — confirm the system refuses gracefully.

Report back any issues. This is the final validation gate.

---

## Summary — User Actions Checklist

| Task | Action |
|------|--------|
| I-1 to I-8 | Gather all credentials and source list before starting |
| 0.1 | Create MongoDB Atlas cluster, user, and network access |
| 0.4 | Fill in `.env` from `.env.example` |
| 1.7 | Provide `scripts/sources.json` with 5–10 source URLs/PDFs |
| 1.9 | Run ingestion CLI and verify chunks in Atlas |
| 2.1 | Create Vector Search index in Atlas UI |
| 2.2 | Create Atlas Search index in Atlas UI |
| 2.9 | Validate retrieval quality with test queries |
| 3.7 | Evaluate generation quality and grounding |
| 4.5 | Smoke-test the API with curl |
| 5.8 | Final end-to-end browser test |
