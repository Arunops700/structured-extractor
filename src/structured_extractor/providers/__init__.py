"""LLM provider implementations behind a single, narrow interface.

The rest of the app depends only on the `LLMProvider` protocol — so swapping
Anthropic for OpenAI (or adding a third provider) touches nothing else. This is the
Dependency Inversion Principle in practice and the reason the tool is "provider-agnostic."
"""

from structured_extractor.providers.base import LLMProvider, ProviderResponse

__all__ = ["LLMProvider", "ProviderResponse"]
