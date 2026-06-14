# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

GooseCompass is a RAG-based AI assistant for University of Waterloo outbound exchange students. It answers natural-language questions **strictly from retrieved institutional documents** — no external LLM knowledge is allowed. Every response must include paragraph-level citations.

Stack: FastAPI + MongoDB Atlas + PydanticAI + React/TypeScript + Docling + OpenAI embeddings + OpenRouter LLM.

## Development commands

**Backend setup:**
```bash
pip install -e ".[dev]"
```

**Run backend server:**
```bash
uvicorn backend.api.app:app --reload
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
GET  /health          health check
POST /query           full RAG pipeline, returns GeneratedResponse JSON
POST /query/stream    same pipeline, streams tokens via text/event-stream
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
```

## Architecture

```
GooseCompass/
├── backend/
│   ├── config.py         # pydantic-settings loader, single Settings instance
│   ├── db.py             # async Motor client, lifespan-compatible open/close
│   ├── ingestion/        # Docling pipeline: fetch → chunk → embed → store
│   ├── retrieval/        # vector search + Atlas full-text search + RRF fusion
│   ├── generation/       # PydanticAI structured response + citation schema
│   ├── api/              # FastAPI routes, streaming delivery
│   └── tests/            # mirrors source structure
├── frontend/             # React + TypeScript chat UI, token streaming, citations
├── scripts/              # CLI tools for ingestion and retrieval validation
└── docs/                 # TASKS.md (phased build plan), architecture docs
```

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

### Key constraints

- **Strict grounding**: if retrieved context is insufficient, the system must say so. Never synthesize from model knowledge.
- **Session-only state**: no persistent chat history (MVP). Conversation state lives in memory per session.
- **Retrieval-first development order**: CLI validation → backend API → streaming frontend.

## Coding principles (enforce strictly)

- **DRY**: extract shared logic into reusable modules.
- **KISS**: prefer the simple solution.
- **YAGNI**: don't build what isn't needed yet.
- **SoC**: retrieval, generation, API, and UI layers must stay cleanly separated.
- **Async all the way**: all I/O (MongoDB, embeddings, LLM calls) must be `async`. Use `asyncio` for concurrency. Clean up with `try/finally` or context managers.

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
