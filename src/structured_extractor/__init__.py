"""structured-extractor: turn messy unstructured text into validated, typed data.

The public surface is intentionally small: pick a provider, hand it some text and
a Pydantic schema, get back a validated model plus token/cost accounting.
"""

from structured_extractor.extractor import ExtractionResult, Extractor
from structured_extractor.usage import TokenUsage

__version__ = "0.1.0"

__all__ = ["Extractor", "ExtractionResult", "TokenUsage", "__version__"]
