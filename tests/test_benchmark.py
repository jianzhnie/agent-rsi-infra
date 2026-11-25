"""Benchmark records reject ambiguous or invalid measurements."""

import json
from pathlib import Path

import pytest

from scripts.validate_benchmark import validate

FIXTURE = Path(__file__).parent / "fixtures/benchmark/synthetic.json"


def sample():
    return json.loads(FIXTURE.read_text())


def test_summary_and_fingerprint_are_stable():
    record = sample()
    result = validate(record)
    assert result["latency_speedup"] == 1.3
    assert result["baseline"]["count"] == 3
    record["environment"] = dict(reversed(list(record["environment"].items())))
    assert validate(record)["environment_sha256"] == result["environment_sha256"]
    record["environment"]["driver"] = "changed"
    assert validate(record)["environment_sha256"] != result["environment_sha256"]


@pytest.mark.parametrize(
    "samples", [[1], [0, 1], [-1, 2], [True, 2], [float("nan"), 2], [float("inf"), 2]]
)
def test_bad_samples_are_rejected(samples):
    record = sample()
    record["candidate"]["samples"] = samples
    with pytest.raises(ValueError):
        validate(record)


def test_environment_does_not_accept_arbitrary_environment_variables():
    record = sample()
    record["environment"]["SECRET_TOKEN"] = "must not archive"
    with pytest.raises(ValueError):
        validate(record)
