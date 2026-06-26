# Contributing

## Setup
```bash
uv sync --extra dev
uv run pre-commit install
```

## Checks (must pass before commit; CI enforces them)
```bash
uv run ruff check .
uv run ruff format .
uv run mypy .
uv run pytest
```

## Conventions
- Type hints on all functions; mypy clean.
- Tests for new logic; fakes over real network calls (`tests/conftest.py`).
- Secrets via `.env` (never committed); update `.env.example` when adding a variable.
- Conventional-commit style messages (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- New providers: implement the `LLMProvider` protocol and wire them in `factory.py`.
