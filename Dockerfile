FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .


FROM python:3.14-slim

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv

COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/alembic.ini /app/alembic.ini

COPY --from=builder /app/src /app/src

RUN chown -R appuser:appgroup /app

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

CMD sh -c "alembic upgrade head && uvicorn src.app.main:app --host 0.0.0.0 --port 8000"