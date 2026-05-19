# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

GooseCompass is a RAG-based AI assistant for University of Waterloo outbound exchange students. It answers natural-language questions **strictly from retrieved institutional documents** — no external LLM knowledge is allowed. Every response must include paragraph-level citations.

Stack: FastAPI + MongoDB Atlas + PydanticAI + React/TypeScript + Docling + OpenAI embeddings + OpenRouter LLM.

## Development commands

> Commands will be added here as the project is bootstrapped. Expected: `uvicorn` for the backend, `pytest` for tests, `npm`/`vite` for the frontend.

Run a single test:
```
pytest backend/tests/path/to/test_file.py::test_function_name -v
```

## Architecture

```
goosecompass/
├── backend/
│   ├── ingestion/    # Docling pipeline: fetch → chunk → embed → store
│   ├── retrieval/    # vector search + Atlas full-text search + RRF fusion
│   ├── generation/   # PydanticAI structured response + citation schema
│   ├── api/          # FastAPI routes, streaming delivery
│   └── tests/        # mirrors source structure
├── frontend/         # React + TypeScript chat UI, token streaming, citations
├── scripts/          # CLI tools for retrieval validation (built before UI)
├── docs/
├── .env.example
└── pyproject.toml
```

### Retrieval pipeline (the core of the system)

```
User query
  → Query rewriter (LLM, improves recall for institutional terminology)
  → Parallel retrieval
      ├── MongoDB vector search (OpenAI text-embedding-3-small, top 20)
      └── MongoDB Atlas full-text search (top 20)
  → Reciprocal Rank Fusion (RRF) merge
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
- **Streaming deferred**: token streaming is a final-phase concern. Initial development uses CLI interaction for retrieval validation.
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
