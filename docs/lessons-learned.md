# Lessons Learned

Notes to my future self from building this (Milestone 1).

## Technical

- **Structured output is a feature, not a prompt.** The big reliability win came from using the
  providers' parse helpers (`messages.parse` / `chat.completions.parse`) with a Pydantic model,
  not from clever JSON-coaxing prompts. Let the platform enforce the shape.
- **Provider quirks are real and worth abstracting.** `temperature` 400s on Opus 4.8 but is fine
  on OpenAI. Discovering this *before* writing the call (by reading current docs, not memory)
  saved a debugging loop. The `LLMProvider` boundary is exactly where such differences belong.
- **A `Protocol` makes testing free.** Because providers are structural, a 15-line fake is a
  complete substitute. The whole suite runs with no keys and no network — fast and free.
- **Put cross-cutting policy in one place.** Retries and cost accounting live in the `Extractor`,
  so they're written once and every provider inherits them.

## Process

- **Read the current API docs first.** Model behavior changes (sampling-param removal is a good
  example); coding from memory would have shipped a bug.
- **Separate library from transport.** The CLI and API are thin shells over the same `Extractor`.
  That made both trivial to write and the logic trivial to test.
- **Document the *why*, not the *what*.** The code says what; `docs/` says why. Re-reading the
  architecture doc is faster than re-deriving the decisions.

## If I did it again

- Add the eval harness from the start, even a tiny one — "is extraction still good?" should be a
  command, not a vibe. (That's Milestone 4, and retrofitting here will be a good exercise.)
- Consider a thin retry/backoff with jitter rather than immediate retries for rate-limit cases.
