# Interview Questions This Project Answers

Questions an interviewer could ask about this codebase, with grounded answers.

---

### Q. How do you get reliable structured output from an LLM?

Use **schema-constrained generation** plus **validation**, not "reply in JSON." Here both
providers use their parse helpers (`messages.parse` / `chat.completions.parse`) with a Pydantic
model, so the provider constrains generation to the schema and returns a validated object.
Pydantic then enforces semantics (types, enums, required). On failure, a bounded retry loop runs.

### Q. Why not just prompt "return JSON" and `json.loads` it?

It's brittle: models add prose around the JSON, hallucinate fields, and break on edge cases,
so you end up writing fragile repair code. Schema-constrained output makes the provider enforce
the shape; you only validate semantics. It's more reliable and less code.

### Q. How is this provider-agnostic?

Everything depends on a narrow `LLMProvider` protocol with one method, `extract(...)`. The
`Extractor`, CLI, and API never reference Anthropic or OpenAI directly — only `factory.py`
picks a concrete provider. Adding a third provider is a new file plus one factory branch.

### Q. You set `temperature=0` for OpenAI but not Anthropic. Why?

On Claude Opus 4.8, sampling parameters were removed — sending `temperature` returns a 400.
OpenAI still accepts it, and `0` aids deterministic extraction. The interface hides this:
each provider does the provider-correct thing; callers are unaware.

### Q. Where do retries belong, and what do you retry?

In the `Extractor`, not the providers — so the policy is written and tested once and applies to
every backend. We retry transient provider errors (rate limits, 5xx, connection blips) and the
rare output that fails validation, up to `MAX_RETRIES`, then raise a typed exception.

### Q. How do you control and observe cost?

Every result carries a `TokenUsage` with input/output tokens and an estimated USD cost from a
small per-model price table. That makes spend loggable and alertable. The default model is
Opus 4.8; for high-volume extraction you'd switch to Haiku (~5× cheaper) after checking quality
on a golden set.

### Q. How is it tested without spending money or hitting the network?

Hand-written fake providers implement the same protocol (`FakeProvider`, `FlakyProvider`).
Tests exercise our logic — retries, wiring, HTTP status mapping, cost math — with no keys or
network. The HTTP tests patch `build_extractor` to inject a fake.

### Q. How would you scale this to millions of documents?

Batch APIs (both providers offer ~50% cheaper batch endpoints), concurrency with rate-limit
backoff, prompt caching for the stable system prompt, semantic caching of repeat inputs, and a
cheaper model tier. Add an eval harness first so a model/prompt change can't silently regress
quality.

### Q. What are the failure modes and how do you handle them?

Auth/config errors (missing key → clear `ProviderError`, surfaced as 502 over HTTP), transient
provider errors (retried), safety refusals (detected and raised), and invalid output (retried,
then `SchemaValidationError`). Each maps to a distinct, typed exception so callers can react.
