"""Reports must not silently omit evidence or unexecuted acceptance criteria."""

from copy import deepcopy

import pytest

from scripts.compare_task_results import compare
from scripts.validate_task_result import validate, validate_contract


def report():
    return {
        "version": 1,
        "task_id": "regression-1",
        "objective": "Reject malformed input",
        "revision": "local-working-tree",
        "criteria": [
            {
                "id": "negative-input",
                "expected": "Error before writing",
                "status": "passed",
                "evidence": {
                    "command": "pytest tests/test_task_result.py",
                    "result": "passed",
                    "artifact": "local pytest output",
                },
            }
        ],
    }


def test_valid_and_unexecuted_results() -> None:
    value = report()
    assert validate(value) is value
    value["criteria"][0] = {
        "id": "gpu",
        "expected": "Numerical parity",
        "status": "not_run",
        "reason": "No device",
    }
    validate(value)


@pytest.mark.parametrize("mutation", ["evidence", "reason", "duplicate", "empty"])
def test_invalid_results(mutation) -> None:
    value = deepcopy(report())
    if mutation == "evidence":
        value["criteria"][0].pop("evidence")
    elif mutation == "reason":
        value["criteria"][0]["status"] = "not_run"
    elif mutation == "duplicate":
        value["criteria"] *= 2
    else:
        value["criteria"] = []
    with pytest.raises(ValueError):
        validate(value)


def test_contract_detects_omitted_or_rewritten_criteria() -> None:
    value = report()
    contract = {
        "task_id": value["task_id"],
        "objective": value["objective"],
        "criteria": [{"id": "negative-input", "expected": "Error before writing"}],
    }
    validate_contract(value, contract)
    contract["criteria"].append({"id": "device", "expected": "Device parity"})
    with pytest.raises(ValueError, match="differ"):
        validate_contract(value, contract)
    contract["criteria"].pop()
    value["criteria"][0]["expected"] = "Always succeeds"
    with pytest.raises(ValueError, match="differ"):
        validate_contract(value, contract)


def test_comparison_exposes_regression_without_promoting() -> None:
    baseline = report()
    candidate = deepcopy(baseline)
    candidate["revision"] = "candidate-hash"
    candidate["criteria"][0]["status"] = "not_run"
    candidate["criteria"][0]["reason"] = "Missing environment"
    contract = {
        "task_id": baseline["task_id"],
        "objective": baseline["objective"],
        "criteria": [{"id": "negative-input", "expected": "Error before writing"}],
    }
    result = compare(contract, baseline, candidate)
    assert result["regressions"] == ["negative-input"]
    assert result["unverified"] == ["negative-input"]
    assert result["decision"] == "human_review_required"
    with pytest.raises(ValueError, match="revisions"):
        compare(contract, baseline, baseline)
