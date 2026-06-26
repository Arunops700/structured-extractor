"""The provider contract every backend must satisfy.

A `Protocol` (structural typing) rather than an ABC: providers don't need to inherit
anything, they just need a matching `extract` method. That keeps each provider file
independent and makes them trivial to fake in tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar

from pydantic import BaseModel

from structured_extractor.usage import TokenUsage

# The schema type flows through generically so callers keep their concrete type
# (e.g. `Invoice`) instead of a bare BaseModel.
SchemaT = TypeVar("SchemaT", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    """What a provider returns: the validated object plus usage accounting."""

    data: BaseModel
    usage: TokenUsage


class LLMProvider(Protocol):
    """Anything that can turn text into a validated instance of a Pydantic schema."""

    name: str

    def extract(
        self,
        *,
        text: str,
        schema: type[SchemaT],
        instructions: str,
    ) -> ProviderResponse:
        """Extract `schema` from `text`.

        Implementations MUST use schema-constrained generation (structured output or
        strict tool use) rather than parsing free-text JSON, and MUST return a
        validated instance. Raise `ProviderError` on transport/auth failures.
        """
        ...
