"""Benchmark records reject ambiguous or invalid measurements."""

import pytest

from scripts.validate_benchmark import validate


def sample():
    # Synthetic unit-test input, never a hardware measurement.
    return {
        "version": 1,
        "task_id": "synthetic",
        "command": "not executed",
        "metric": "latency",
        "unit": "us",
        "timing_boundary": "synthetic op",
        "cache": "synthetic",
        "graph": "synthetic",
        "workload": "synthetic",
        "warmup": 0,
        "environment": {
            "device": "synthetic",
            "device_count": 1,
            "topology": "single",
            "driver": "n/a",
            "runtime": "n/a",
            "compiler": "n/a",
            "framework": "n/a",
        },
        "baseline": {"revision": "synthetic-base", "samples": [12, 14, 13]},
        "candidate": {"revision": "synthetic-candidate", "samples": [10, 11, 9]},
    }


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
