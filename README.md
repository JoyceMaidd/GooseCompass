# GooseCompass

A RAG-based AI assistant that answers exchange-program questions for University of Waterloo outbound students — partner universities, application procedures, eligibility, housing, visas, and more — with every answer cited to official source documents.

## Overview

Students researching exchange programs have to dig through scattered PDFs and web pages across dozens of partner institutions. GooseCompass indexes that institutional content and answers natural-language questions over it directly, with citations, instead of leaving students to search manually.

**Strict grounding rule:** the system only answers from retrieved institutional documents. It never falls back on general LLM knowledge — if the retrieved context doesn't cover the question, it says so rather than guessing.

## Demo

https://github.com/user-attachments/assets/0abeff0b-f22f-457f-8b15-180e1a462644

## Features

- **Grounded answers with citations** — every paragraph is backed by a source document; insufficient context is surfaced explicitly rather than hallucinated.
- **Hybrid retrieval** — combines vector search and full-text search via Reciprocal Rank Fusion for better recall than either alone.
- **Usage controls** — per-user monthly token quotas and a global monthly spend cap, enforced before each LLM call.
- **Structured generation** — PydanticAI validates every response against a citation schema before it reaches the client.

## Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Retrieval store | MongoDB Atlas (vector search + full-text search) |
| Usage & quota tracking | PostgreSQL (SQLAlchemy async + Alembic) |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM | OpenRouter (configurable model) |
| Structured generation | PydanticAI |
| Document ingestion | Docling |
| Frontend | React + TypeScript + Vite |

## How it works

```
User query
  → Query rewriter (LLM — improves recall for institutional terminology)
  → Parallel retrieval
      ├── MongoDB vector search (top 20)
      └── MongoDB Atlas full-text search (top 20)
  → Reciprocal Rank Fusion (RRF)
  → Top-10 context selection
  → PydanticAI response generator (structured answer + end-of-paragraph citations)
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A MongoDB Atlas cluster with:
  - A vector search index on the chunks collection
  - An Atlas Search (full-text) index on the chunks collection
- A PostgreSQL database (for usage/quota tracking)
- API keys for OpenAI and OpenRouter

### Installation

```bash
git clone <repo-url>
cd GooseCompass
pip install -e ".[dev]"
cd frontend && npm install && cd ..
```

### Configuration

```bash
cp .env.example .env
```

Fill in `.env`:

```
MONGODB_URI=                          # Atlas connection string
MONGODB_DB_NAME=                      # database name
MONGODB_COLLECTION_CHUNKS=            # collection that stores document chunks
OPENAI_API_KEY=                       # used for embeddings
OPENROUTER_API_KEY=                   # used for LLM calls
OPENROUTER_GENERATION_MODEL=          # e.g. openai/gpt-4.1-nano
OPENROUTER_REWRITER_MODEL=            # e.g. google/gemini-2.5-flash-lite
OPENROUTER_EVAL_JUDGE_MODEL=          # model used to score eval runs
FRONTEND_ORIGIN=http://localhost:5174
VITE_API_URL=http://localhost:8000
POSTGRES_URI=                         # usage/quota tracking database
MONTHLY_SPEND_CAP_USD=2.0             # global monthly LLM spend ceiling
USER_MONTHLY_QUOTA_TOKENS=50000       # per-user monthly token quota
LOGFIRE_API_KEY=                      # optional — observability
LOGFIRE_ENABLED=true
```

Then apply the Postgres schema:

```bash
alembic upgrade head
```

### Running locally

```bash
# Terminal 1 — backend (from repo root)
uvicorn backend.api.app:app --reload

# Terminal 2 — frontend
cd frontend && npm run dev
```

The frontend is available at `http://localhost:5174` and the API at `http://localhost:8000`.

### Ingesting documents

Edit `scripts/sources.json` to list your source URLs and PDFs, then run:

```bash
python scripts/ingest.py              # ingest all sources
python scripts/ingest.py --dry-run    # preview sources without ingesting
```

See `scripts/example.sources.json` for the expected format.

## Usage

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/query` | Full RAG pipeline, returns `GeneratedResponse` JSON |
| `POST` | `/query/stream` | Same pipeline, streams tokens via `text/event-stream` |

With the backend running:

```bash
# Full query (blocking)
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the GPA requirements for outbound exchange?"}' | python3 -m json.tool
# {
#   "paragraphs": [
#     { "text": "...", "citations": ["https://..."] }
#   ],
#   "insufficient_context": false
# }

# Streaming query (SSE)
curl -N -X POST http://localhost:8000/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "What documents do I need for my exchange application?"}'
# data: {"type": "token", "text": "You "}
# data: {"type": "token", "text": "will "}
# ...
# data: {"type": "citations", "citations": ["https://..."]}

# Out-of-scope query (triggers grounding refusal)
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}' | python3 -m json.tool
# "insufficient_context": true
```

## Development / Testing

**Retrieval and generation quality checks**, useful before or instead of running the full API:

```bash
python scripts/validate_retrieval.py   # interactive retrieval quality check
python scripts/validate_generation.py  # interactive end-to-end pipeline check
```

**Automated eval** against a golden dataset through DeepEval:

```bash
python scripts/run_eval.py
```

**Unit and integration tests**:

```bash
pytest backend/tests/ -v                                          # all tests
pytest backend/tests/path/to/test_file.py::test_function_name -v  # a single test
```

## Project structure

```
GooseCompass/
├── backend/
│   ├── config.py         # pydantic-settings env loader
│   ├── db.py              # async Motor client (Mongo) + async SQLAlchemy engine (Postgres)
│   ├── ingestion/        # Docling pipeline: fetch → chunk → embed → store
│   ├── retrieval/        # vector search + full-text search + RRF fusion
│   ├── generation/       # PydanticAI structured response + citation schema
│   ├── monitoring/       # usage logging, quota + spend-cap enforcement
│   ├── eval/              # DeepEval scoring pipeline
│   ├── api/               # FastAPI routes and streaming delivery
│   └── tests/             # mirrors source structure
├── frontend/             # React + TypeScript chat UI with token streaming
├── scripts/              # ingestion, validation, and eval CLI tools
├── alembic/               # Postgres migrations
└── docs/                 # architecture docs and task plan
```

## Contributing

Contributions are welcome. A few conventions this repo follows:

- Write the test for a function immediately after implementing it; tests mirror the source layout under `backend/tests/`.
- Run `pytest backend/tests/ -v` before opening a PR.
- Keep functions under ~40 lines; split rather than let them grow.
- Python uses Google-style docstrings; TypeScript uses JSDoc on exported functions/components.

To submit a change: fork the repo, create a feature branch, make your change with tests, and open a pull request describing what changed and why.

## License

[MIT](LICENSE)
