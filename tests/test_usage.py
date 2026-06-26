"""Cost/usage accounting is pure arithmetic — easy to get subtly wrong, so pin it."""

from __future__ import annotations

from structured_extractor.usage import TokenUsage


def test_total_tokens_sums_input_and_output() -> None:
    usage = TokenUsage(model="claude-opus-4-8", input_tokens=1000, output_tokens=500)
    assert usage.total_tokens == 1500


def test_cost_uses_per_million_token_rates() -> None:
    # Opus 4.8: $5 / 1M input, $25 / 1M output.
    usage = TokenUsage(model="claude-opus-4-8", input_tokens=1_000_000, output_tokens=1_000_000)
    assert usage.estimated_cost_usd == 30.0


def test_unknown_model_costs_zero_not_crash() -> None:
    usage = TokenUsage(model="some-future-model", input_tokens=10, output_tokens=10)
    assert usage.estimated_cost_usd == 0.0
