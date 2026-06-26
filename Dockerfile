# Multi-stage build: install deps in a builder, copy a slim runtime image.
# Using uv for fast, reproducible installs.

FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
# Copy only what's needed to resolve + install first, for better layer caching.
COPY pyproject.toml README.md ./
COPY src ./src
RUN uv sync --no-dev

FROM python:3.12-slim AS runtime
WORKDIR /app
# Bring the resolved virtual environment and the source over.
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
# Run the API. The CLI is also available in this image as `extract`.
CMD ["uvicorn", "structured_extractor.api:app", "--host", "0.0.0.0", "--port", "8000"]
