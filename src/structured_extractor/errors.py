"""Domain-specific exceptions.

Distinct error types let callers (CLI, API, tests) react differently to a provider
outage versus the model returning data that won't validate against the schema.
"""

from __future__ import annotations


class ExtractionError(Exception):
    """Base class for all extraction failures."""


class ProviderError(ExtractionError):
    """The underlying LLM provider failed (auth, network, rate limit, server error)."""


class SchemaValidationError(ExtractionError):
    """The model produced output that did not validate against the target schema,
    even after retries."""
