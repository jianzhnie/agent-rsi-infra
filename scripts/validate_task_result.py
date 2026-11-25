"""Validate a task contract and its evidence report without executing commands."""

import argparse
import json
from pathlib import Path


def validate(report):
    if (
        not isinstance(report, dict)
        or type(report.get("version")) is not int
        or report["version"] != 1
    ):
        raise ValueError("Expected an object with version 1")
    for field in ("task_id", "objective", "revision"):
        if not isinstance(report.get(field), str) or not report[field].strip():
            raise ValueError(f"Missing {field}")
    criteria = report.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("criteria must be a nonempty list")
    ids = set()
    for item in criteria:
        if not isinstance(item, dict):
            raise ValueError("Each criterion must be an object")
        for field in ("id", "expected"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"Missing criterion {field}")
        if item["id"] in ids:
            raise ValueError("Duplicate criterion id")
        ids.add(item["id"])
        status = item.get("status")
        if status not in ("passed", "failed", "not_run", "not_applicable"):
            raise ValueError("Invalid criterion status")
        if status in ("passed", "failed"):
            evidence = item.get("evidence")
            if not isinstance(evidence, dict):
                raise ValueError("Executed criteria require evidence")
            for field in ("command", "result", "artifact"):
                if (
                    not isinstance(evidence.get(field), str)
                    or not evidence[field].strip()
                ):
                    raise ValueError(f"Missing evidence {field}")
        elif not isinstance(item.get("reason"), str) or not item["reason"].strip():
            raise ValueError("Unexecuted criteria require a reason")
    return report


def validate_contract(report, contract):
    """Match a result to independently recorded acceptance criteria."""
    validate(report)
    if not isinstance(contract, dict) or contract.get("task_id") != report["task_id"]:
        raise ValueError("Task identity does not match contract")
    if contract.get("objective") != report["objective"]:
        raise ValueError("Task objective does not match contract")
    expected = contract.get("criteria")
    if not isinstance(expected, list) or not expected:
        raise ValueError("Contract requires acceptance criteria")
    mapping = {}
    for item in expected:
        if not isinstance(item, dict):
            raise ValueError("Invalid contract criterion")
        for field in ("id", "expected"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"Missing contract {field}")
        if item["id"] in mapping:
            raise ValueError("Duplicate contract criterion")
        mapping[item["id"]] = item["expected"]
    actual = {item["id"]: item["expected"] for item in report["criteria"]}
    if actual != mapping:
        raise ValueError("Report criteria differ from contract")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument(
        "--contract", type=Path, help="Compare with fixed task criteria"
    )
    args = parser.parse_args()
    try:
        report = validate(json.loads(args.report.read_text()))
        if args.contract:
            validate_contract(report, json.loads(args.contract.read_text()))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Invalid report: {error}\n")
    print("Report structure valid; evidence authenticity was not verified.")


if __name__ == "__main__":
    main()
