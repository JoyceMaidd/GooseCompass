# GooseCompass

A RAG-based AI assistant for University of Waterloo outbound exchange students. Ask natural-language questions about partner universities, application procedures, eligibility requirements, housing, visa information, and more — and get factual answers cited to official source documents.

**Strict grounding rule:** the system only answers from retrieved institutional documents. It never synthesizes from general LLM knowledge. If the retrieved context is insufficient, it says so.

## Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Database | MongoDB Atlas (vector search + full-text search) |
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

## Prerequisites

- Python 3.11+
- Node.js 18+
- A MongoDB Atlas cluster with:
  - A vector search index on the chunks collection
  - An Atlas Search (full-text) index on the chunks collection
- API keys for OpenAI and OpenRouter

## Setup

### 1. Clone and install backend

```bash
git clone <repo-url>
cd GooseCompass
pip install -e ".[dev]"
```

### 2. Configure environment variables

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
OPENROUTER_GENERATION_MODEL=          # e.g. anthropic/claude-sonnet-4-6
OPENROUTER_REWRITER_MODEL=            # e.g. anthropic/claude-haiku-4-5
FRONTEND_ORIGIN=http://localhost:5174
VITE_API_URL=http://localhost:8000
```

### 3. Install frontend dependencies

```bash
cd frontend && npm install
```

## Running locally

Start the backend and frontend in separate terminals:

```bash
# Terminal 1 — backend (from repo root)
uvicorn backend.api.app:app --reload

# Terminal 2 — frontend
cd frontend && npm run dev
```

The frontend is available at `http://localhost:5174` and the API at `http://localhost:8000`.

## Ingesting documents

Edit `scripts/sources.json` to list your source URLs and PDFs, then run:

```bash
python scripts/ingest.py              # ingest all sources
python scripts/ingest.py --dry-run    # preview sources without ingesting
```

See `scripts/example.sources.json` for the expected format.

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/query` | Full RAG pipeline, returns `GeneratedResponse` JSON |
| `POST` | `/query/stream` | Same pipeline, streams tokens via `text/event-stream` |

## Smoke testing

With the backend running, use these curl commands to verify each endpoint:

**Health check**
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

**Full query (blocking)**
```bash
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the GPA requirements for outbound exchange?"}' | python3 -m json.tool
# {
#   "paragraphs": [
#     {
#       "text": "...",
#       "citations": ["https://..."]
#     }
#   ],
#   "insufficient_context": false
# }
```

**Streaming query (SSE)**
```bash
curl -N -X POST http://localhost:8000/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "What documents do I need for my exchange application?"}'
# data: {"type": "token", "text": "You "}
# data: {"type": "token", "text": "will "}
# ...
# data: {"type": "citations", "citations": ["https://..."]}
```

**Insufficient context (triggers grounding refusal)**
```bash
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}' | python3 -m json.tool
# "insufficient_context": true
```

## Validation scripts

Use these to check retrieval and generation quality before using the API:

```bash
python scripts/validate_retrieval.py   # interactive retrieval quality check
python scripts/validate_generation.py  # interactive end-to-end pipeline check
```

## Testing

```bash
# Run all tests
pytest backend/tests/ -v

# Run a single test
pytest backend/tests/path/to/test_file.py::test_function_name -v
```

## Project structure

```
GooseCompass/
├── backend/
│   ├── config.py         # pydantic-settings env loader
│   ├── db.py             # async Motor client
│   ├── ingestion/        # Docling pipeline: fetch → chunk → embed → store
│   ├── retrieval/        # vector search + full-text search + RRF fusion
│   ├── generation/       # PydanticAI structured response + citation schema
│   ├── api/              # FastAPI routes and streaming delivery
│   └── tests/            # mirrors source structure
├── frontend/             # React + TypeScript chat UI with token streaming
├── scripts/              # ingestion and validation CLI tools
└── docs/                 # architecture docs and task plan
```
