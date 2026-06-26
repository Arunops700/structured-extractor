# Architecture & Design Decisions

This document explains *why* the code is shaped the way it is — the reasoning is the
learning. Read it alongside the source.

## The core idea

Extraction is a pipeline with one variable part (which LLM) and several invariant parts
(prompting, validation, retries, cost accounting). The design isolates the variable part
behind a narrow interface so the invariant parts are written and tested **once**.

```
text + schema ─▶ Extractor ─▶ LLMProvider ─▶ (Anthropic | OpenAI) ─▶ validated object + usage
                  │  owns: prompt, retries, cost
                  └─ depends only on the LLMProvider protocol
```

## Key decisions

### 1. Provider behind a `Protocol`, not an ABC
`LLMProvider` is a `typing.Protocol` (structural typing). Providers don't inherit anything —
they just expose a matching `extract(...)`. This keeps each provider file self-contained and
makes a test fake a *complete* substitute (see `tests/conftest.py`). It's the **Dependency
Inversion Principle**: high-level policy (the `Extractor`) depends on an abstraction, and the
concrete providers depend on that same abstraction.

**Alternative considered:** a single class with `if provider == ...` branches. Rejected —
it couples every provider's quirks into one file and makes testing require real SDKs.

### 2. Schema-constrained output over "reply in JSON"
Both providers use their structured-output parse helpers (`messages.parse`,
`chat.completions.parse`) with a Pydantic model. The provider enforces the *shape*; Pydantic
enforces the *semantics* (types, enums, required fields). Free-text JSON prompting was rejected:
it's brittle, needs ad-hoc repair, and fails silently on edge cases.

### 3. Provider-correct sampling, hidden behind the interface
- **Anthropic (Opus 4.8):** sampling parameters were removed from the model; sending
  `temperature` returns HTTP 400. The provider omits it. Determinism comes from the task +
  constrained decoding.
- **OpenAI:** `temperature=0` is valid and aids determinism, so the provider sets it.

Same intent, two correct implementations — and callers never see the difference. This is
exactly the kind of provider-specific detail an abstraction should absorb.

### 4. Retries live in the `Extractor`, not the providers
Providers do one call. The `Extractor` wraps them in a bounded retry loop covering two
failure classes — transient provider errors (429/5xx/connection) and the rare invalid output —
then raises a typed exception. Writing the policy once means it applies uniformly to every
backend and is tested with a `FlakyProvider` fake.

### 5. One composition root (`factory.py`)
The CLI and API never construct providers directly — they call `build_extractor(settings)`.
Wiring and defaults live in one place, so adding a provider or changing a default is a
single-file change.

### 6. Configuration via `pydantic-settings`
Typed, validated config with a single source of truth and `.env` support. Secrets come from
the environment, never code.

## Cost trade-off: which model?

The Anthropic default is `claude-opus-4-8` (following Anthropic's guidance). But **extraction
is a comparatively easy task**, and cost scales with usage:

| Model | Input $/1M | Output $/1M | When |
|---|---|---|---|
| `claude-opus-4-8` | $5 | $25 | Hard/ambiguous documents; default |
| `claude-haiku-4-5` | $1 | $5 | High-volume, well-structured extraction |

For a pipeline doing millions of extractions, switching to Haiku is often the right call —
set `ANTHROPIC_MODEL=claude-haiku-4-5`. Measuring quality on a golden set before downgrading
is the disciplined way to decide (that evaluation muscle is built in a later milestone).

## What's deliberately out of scope (for now)
- Tracing/observability and eval harnesses — Milestone 4.
- OCR/PDF ingestion — a natural extension.
- Streaming and batching — needed only at scale.

Keeping the surface small keeps the design legible; these extend cleanly because the provider
boundary already exists.
