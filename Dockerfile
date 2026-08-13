# Multi-stage build: 1. dependencies, 2. runtime

# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build
COPY pyproject.toml pyproject.lock* ./
RUN pip install --no-cache-dir --target /build/deps -e .

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /build/deps /usr/local/lib/python3.11/site-packages

# Copy source code
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Set Python to unbuffered mode (streaming logs in Render)
ENV PYTHONUNBUFFERED=1

# Expose port (Render maps it automatically)
EXPOSE 8000

# Entrypoint: run migrations, then start uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn backend.api.app:app --host 0.0.0.0 --port 8000"]
