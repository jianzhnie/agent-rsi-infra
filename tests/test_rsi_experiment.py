import pytest

from scripts.rsi_experiment import init_experiment, record_trial, summarize


def task():
    return {
        "task_id": "sample",
        "objective": "test",
        "baseline_revision": "base",
        "quality_contract": "independent validation",
        "workload": "fixed replay",
        "environment": "synthetic test",
    }


def trial(**updates):
    row = {
        "trial_id": "t1",
        "candidate_revision": "candidate",
        "quality_gate": "passed",
        "quality_evidence": "quality.json",
        "command": "benchmark invocation",
        "artifact": "artifact digest",
        "latency_samples": [90, 100, 110],
        "baseline_median_latency": 120,
    }
    row.update(updates)
    return row


def test_quality_gate_and_threshold_are_required_for_review(tmp_path):
    path = tmp_path / "exp.json"
    init_experiment(path, task())
    record_trial(path, trial())
    report = summarize(path)
    assert report["trials"][0]["validated_speedup"] == 1.2
    assert report["trials"][0]["recommendation"] == "human_review"
    assert report["promotion"] == "never_automatic"


@pytest.mark.parametrize("gate", ["failed", "not_run"])
def test_failed_or_missing_quality_never_scores(tmp_path, gate):
    path = tmp_path / "exp.json"
    init_experiment(path, task())
    record_trial(path, trial(quality_gate=gate))
    row = summarize(path)["trials"][0]
    assert row["validated_speedup"] is None
    assert not row["threshold_met"]


def test_rejects_same_revision_duplicate_and_bad_samples(tmp_path):
    path = tmp_path / "exp.json"
    init_experiment(path, task())
    with pytest.raises(ValueError, match="differ"):
        record_trial(path, trial(candidate_revision="base"))
    record_trial(path, trial())
    with pytest.raises(ValueError, match="unique"):
        record_trial(path, trial())
    with pytest.raises(ValueError, match="finite positive"):
        record_trial(path, trial(trial_id="bad", latency_samples=[2, float("nan")]))


def test_init_is_non_destructive(tmp_path):
    path = tmp_path / "exp.json"
    init_experiment(path, task())
    with pytest.raises(ValueError, match="already exists"):
        init_experiment(path, task())
