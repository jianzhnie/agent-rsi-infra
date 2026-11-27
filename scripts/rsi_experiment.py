"""Evidence-first RSI experiment ledger; no execution or automatic promotion."""
import argparse
import hashlib
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = 1
THRESHOLD = 1.10


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("JSON input must be an object")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def init_experiment(path: Path, task: dict) -> dict:
    fields = (
        "task_id",
        "objective",
        "baseline_revision",
        "quality_contract",
        "workload",
        "environment",
    )
    for field in fields:
        if not isinstance(task.get(field), str) or not task[field].strip():
            raise ValueError(f"task requires non-empty {field}")
    if path.exists():
        raise ValueError(f"Experiment already exists: {path}")
    record = {
        "schema_version": VERSION,
        "experiment_id": task["task_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "trials": [],
        "policy": {
            "minimum_validated_speedup": THRESHOLD,
            "promotion": "human_review_only",
        },
    }
    write_json(path, record)
    return record


def record_trial(path: Path, trial: dict) -> dict:
    experiment = read_json(path)
    if experiment.get("schema_version") != VERSION:
        raise ValueError("Unsupported experiment schema")
    fields = (
        "trial_id",
        "candidate_revision",
        "quality_gate",
        "quality_evidence",
        "command",
        "artifact",
    )
    for field in fields:
        if not isinstance(trial.get(field), str) or not trial[field].strip():
            raise ValueError(f"trial requires non-empty {field}")
    if trial["candidate_revision"] == experiment["task"]["baseline_revision"]:
        raise ValueError("Candidate revision must differ from baseline revision")
    if trial["quality_gate"] not in ("passed", "failed", "not_run"):
        raise ValueError("quality_gate must be passed, failed, or not_run")
    samples = trial.get("latency_samples")
    if not isinstance(samples, list) or len(samples) < 2:
        raise ValueError("Require at least two repeated end-to-end latency samples")
    if any(
        type(sample) not in (int, float)
        or not math.isfinite(sample)
        or sample <= 0
        for sample in samples
    ):
        raise ValueError("Latency samples must be finite positive numbers")
    if any(row["trial_id"] == trial["trial_id"] for row in experiment["trials"]):
        raise ValueError("trial_id must be unique")
    baseline = trial.get("baseline_median_latency")
    if trial["quality_gate"] == "passed" and (
        type(baseline) not in (int, float)
        or not math.isfinite(baseline)
        or baseline <= 0
    ):
        raise ValueError("Quality-passed trial requires positive baseline_median_latency")
    row = dict(trial)
    row["recorded_at"] = datetime.now(timezone.utc).isoformat()
    row["median_latency"] = statistics.median(samples)
    row["baseline_revision"] = experiment["task"]["baseline_revision"]
    row["validated_speedup"] = (
        baseline / row["median_latency"] if trial["quality_gate"] == "passed" else None
    )
    evidence = json.dumps(
        trial, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    row["evidence_sha256"] = hashlib.sha256(evidence).hexdigest()
    experiment["trials"].append(row)
    write_json(path, experiment)
    return row


def summarize(path: Path) -> dict:
    experiment = read_json(path)
    threshold = experiment["policy"]["minimum_validated_speedup"]
    rows = []
    for trial in experiment["trials"]:
        speedup = trial["validated_speedup"]
        qualified = (
            trial["quality_gate"] == "passed"
            and speedup is not None
            and speedup >= threshold
        )
        rows.append(
            {
                "trial_id": trial["trial_id"],
                "candidate_revision": trial["candidate_revision"],
                "quality_gate": trial["quality_gate"],
                "median_latency": trial["median_latency"],
                "validated_speedup": speedup,
                "threshold_met": qualified,
                "recommendation": (
                    "human_review" if qualified else "reject_or_continue"
                ),
            }
        )
    return {
        "schema_version": 1,
        "experiment_id": experiment["experiment_id"],
        "baseline_revision": experiment["task"]["baseline_revision"],
        "minimum_validated_speedup": threshold,
        "trials": rows,
        "promotion": "never_automatic",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("experiment", type=Path)
    init_parser.add_argument("task", type=Path)
    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("experiment", type=Path)
    record_parser.add_argument("trial", type=Path)
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("experiment", type=Path)
    report_parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "init":
            result = init_experiment(args.experiment, read_json(args.task))
        elif args.action == "record":
            result = record_trial(args.experiment, read_json(args.trial))
        else:
            result = summarize(args.experiment)
            if args.output:
                write_json(args.output, result)
                print(f"Wrote {args.output}")
                return 0
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"RSI experiment error: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
