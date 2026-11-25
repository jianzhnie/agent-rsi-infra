"""Compare contract-matched results for human review; never promote changes."""

import argparse
import json
from pathlib import Path

try:
    from .validate_task_result import validate_contract
except ImportError:
    from validate_task_result import validate_contract


def compare(contract, baseline, candidate):
    validate_contract(baseline, contract)
    validate_contract(candidate, contract)
    if baseline["revision"] == candidate["revision"]:
        raise ValueError("Baseline and candidate revisions must differ")
    old = {item["id"]: item["status"] for item in baseline["criteria"]}
    changes = []
    for item in candidate["criteria"]:
        before, after = old[item["id"]], item["status"]
        changes.append({"id": item["id"], "baseline": before, "candidate": after})
    return {
        "task_id": candidate["task_id"],
        "baseline_revision": baseline["revision"],
        "candidate_revision": candidate["revision"],
        "criteria": changes,
        "regressions": [
            x["id"]
            for x in changes
            if x["baseline"] == "passed" and x["candidate"] != "passed"
        ],
        "unverified": [
            x["id"] for x in changes if x["candidate"] in ("not_run", "not_applicable")
        ],
        "failures": [x["id"] for x in changes if x["candidate"] == "failed"],
        "decision": "human_review_required",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("contract", "baseline", "candidate"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    try:
        result = compare(
            *(
                json.loads(path.read_text())
                for path in (args.contract, args.baseline, args.candidate)
            )
        )
    except (OSError, ValueError) as error:
        parser.exit(1, f"Invalid comparison: {error}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
