"""HTTP contract tests: status codes and response shape, with the provider faked.

We patch `build_extractor` in the api module so the endpoint runs end to end without
keys or network — proving the transport layer (validation, error mapping, serialization)
behaves, independent of any real model.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from structured_extractor import api
from structured_extractor.errors import ProviderError
from structured_extractor.extractor import Extractor
from tests.conftest import FakeProvider

client = TestClient(api.app)


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_list_schemas_includes_contact() -> None:
    body = client.get("/schemas").json()
    assert "contact" in body
    assert "name" in body["contact"]


def test_extract_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api, "build_extractor", lambda _settings: Extractor(FakeProvider()))

    resp = client.post("/extract", json={"text": "Ada, ada@example.com", "schema_name": "contact"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "fake"
    assert body["data"]["name"] == "Ada Lovelace"
    assert body["input_tokens"] == 120


def test_extract_unknown_schema_returns_404() -> None:
    resp = client.post("/extract", json={"text": "x", "schema_name": "nope"})
    assert resp.status_code == 404


def test_extract_provider_failure_returns_502(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(_settings: object) -> Extractor:
        raise ProviderError("ANTHROPIC_API_KEY is not set.")

    monkeypatch.setattr(api, "build_extractor", _boom)
    resp = client.post("/extract", json={"text": "x", "schema_name": "contact"})
    assert resp.status_code == 502


def test_extract_rejects_empty_text() -> None:
    # Pydantic min_length=1 → 422 before any provider call.
    resp = client.post("/extract", json={"text": "", "schema_name": "contact"})
    assert resp.status_code == 422
