"""The Extractor's reliability behavior: success, retry-then-succeed, and exhaustion."""

from __future__ import annotations

import pytest

from structured_extractor.errors import ProviderError
from structured_extractor.extractor import Extractor
from structured_extractor.schemas import ContactInfo
from tests.conftest import FakeProvider, FlakyProvider


def test_extract_returns_validated_object_and_usage() -> None:
    extractor = Extractor(FakeProvider())
    result = extractor.extract("Ada Lovelace, ada@example.com", ContactInfo)

    assert isinstance(result.data, ContactInfo)
    assert result.data.name == "Ada Lovelace"
    assert result.provider == "fake"
    assert result.attempts == 1
    assert result.usage.total_tokens == 150


def test_retries_then_succeeds() -> None:
    provider = FlakyProvider(fail_times=2)
    extractor = Extractor(provider, max_retries=2)  # 3 attempts total

    result = extractor.extract("text", ContactInfo)

    assert provider.calls == 3
    assert result.attempts == 3
    assert isinstance(result.data, ContactInfo)
    assert result.data.name == "Grace Hopper"


def test_raises_after_exhausting_retries() -> None:
    provider = FlakyProvider(fail_times=99)
    extractor = Extractor(provider, max_retries=1)  # 2 attempts, both fail

    with pytest.raises(ProviderError):
        extractor.extract("text", ContactInfo)
    assert provider.calls == 2
