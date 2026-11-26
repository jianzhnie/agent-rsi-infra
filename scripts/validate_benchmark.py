"""Validate paired benchmark samples and a non-sensitive environment record."""

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path


def validate(value):
    if (
        not isinstance(value, dict)
        or type(value.get("version")) is not int
        or value["version"] != 1
    ):
        raise ValueError("Expected benchmark version 1")
    for field in (
        "task_id",
        "command",
        "metric",
        "unit",
        "timing_boundary",
        "cache",
        "graph",
        "workload",
    ):
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise ValueError(f"Missing {field}")
    if value["metric"] != "latency":
        raise ValueError("This format currently supports latency only")
    if value["unit"] not in ("ns", "us", "ms", "s"):
        raise ValueError("Latency samples require ns/us/ms/s units")
    if type(value.get("warmup")) is not int or value["warmup"] < 0:
        raise ValueError("warmup must be a nonnegative integer")
    environment = value.get("environment")
    fields = {
        "device",
        "device_count",
        "topology",
        "driver",
        "runtime",
        "compiler",
        "framework",
    }
    if not isinstance(environment, dict) or set(environment) != fields:
        raise ValueError("Environment requires exactly the documented fields")
    for key in fields - {"device_count"}:
        if not isinstance(environment[key], str) or not environment[key].strip():
            raise ValueError(f"Missing environment {key}")
    if type(environment["device_count"]) is not int or environment["device_count"] < 1:
        raise ValueError("device_count must be positive")
    summary = {}
    for arm in ("baseline", "candidate"):
        record = value.get(arm)
        if (
            not isinstance(record, dict)
            or not isinstance(record.get("revision"), str)
            or not record["revision"].strip()
        ):
            raise ValueError(f"Missing {arm} revision")
        samples = record.get("samples")
        if not isinstance(samples, list) or len(samples) < 2:
            raise ValueError(f"{arm} requires repeated samples")
        if any(
            type(x) not in (int, float) or not math.isfinite(x) or x <= 0
            for x in samples
        ):
            raise ValueError("Samples must be finite positive numbers")
        summary[arm] = {
            "median": statistics.median(samples),
            "min": min(samples),
            "max": max(samples),
            "count": len(samples),
        }
    if value["baseline"]["revision"] == value["candidate"]["revision"]:
        raise ValueError("Baseline and candidate revisions must differ")
    encoded = json.dumps(
        environment, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    summary["environment_sha256"] = hashlib.sha256(encoded.encode()).hexdigest()
    summary["latency_speedup"] = (
        summary["baseline"]["median"] / summary["candidate"]["median"]
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.report.read_text()))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Invalid benchmark: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
