# GooseCompass — CLAUDE.md

## Project overview
- RAG-based AI assistant for UWaterloo outbound exchange students.
- Stack: FastAPI + MongoDB Atlas + PydanticAI + React/TypeScript.
- Goal: grounded, citation-backed answers from curated institutional docs.

## Architecture
```
goosecompass/ 
├── backend/ 
│ ├── ingestion/    # data ingestion pipeline 
│ ├── retrieval/    # vector + text search + RRF 
│ ├── generation/   # PydanticAI response builder 
│ ├── api/          # FastAPI routes 
│ └── tests/        # mirrors source structure 
├── frontend/       # React + TypeScript 
├── scripts/        # CLI validation tools
├── docs/           # Documentation
├── CLAUDE.md 
├── .env.example 
└── pyproject.toml
```

## Coding principles (enforce strictly)
- DRY(Don't Repeat Yourself): Avoid redundant code. If you have the same block of code in multiple places, extract it into a reusable function or module.
- KISS(Keep It Simple, Stupid): Prioritize simplicity. Simple code is easier to read, test, and debug. Avoid premature optimization or over-engineering.
- YAGNI (You Aren't Gonna Need It): Don't add functionality or features until they are strictly necessary. Speculative code often adds unnecessary complexity.
- SoC(Separation of Concerns): Separate retrieval, generation, API, and UI concerns cleanly.
- ASYNC ALL THE WAY
   - All I/O operations MUST be async (MongoDB, embeddings, LLM calls)
   - Use `asyncio` for concurrent operations
   - Proper cleanup with `try/finally` or context managers

## Code style
- Python: **Use Google-style docstrings** for all functions, classes, and modules
```python
async def semantic_search(
    ctx: RunContext[AgentDependencies],
    query: str,
    match_count: Optional[int] = None
) -> list[SearchResult]:
    """
    Perform pure semantic search using vector similarity.

    Args:
        ctx: Agent runtime context with dependencies
        query: Search query text
        match_count: Number of results to return (default: 10)

    Returns:
        List of search results ordered by similarity

    Raises:
        ConnectionFailure: If MongoDB connection fails
        ValueError: If match_count exceeds maximum allowed
    """
```
- TypeScript: JSDoc on exported functions and components.
- Max function length: 40 lines. Split if longer.

## Testing rules
- Write a test immediately after implementing each function.
- Tests go in `tests/ mirroring` the source structure.
- Run tests before marking a task done. Never skip.

## Task discipline
- Do exactly ONE task at a time. Stop and wait for review.
- If a task feels large, split it further and confirm with the user.
