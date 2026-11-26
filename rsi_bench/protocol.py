"""Paper-aligned RSIBench-Infra protocol and scoring primitives."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import statistics
import sys
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

LAYER_MEDIA_TYPE = "application/vnd.oci.image.layer.v1.tar+gzip"
_SHA256 = "sha256:"


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _number(value: Any, name: str, *, zero: bool = False) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite numeric data")
    invalid = value < 0 if zero else value <= 0
    if invalid:
        raise ValueError(f"{name} must be {'nonnegative' if zero else 'positive'}")
    return float(value)


def _digest(value: Any, name: str) -> str:
    value = _string(value, name)
    if len(value) != 71 or not value.startswith(_SHA256):
        raise ValueError(f"{name} must be a sha256 digest")
    try:
        int(value[7:], 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be a hexadecimal sha256 digest") from exc
    return value


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def load_catalog(path: Path) -> dict[str, Any]:
    catalog = read_json(path)
    if not isinstance(catalog, dict) or catalog.get("schema_version") != 1:
        raise ValueError("Task catalog must use schema_version=1")
    tasks = catalog.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != 20:
        raise ValueError("Paper task catalog must contain exactly 20 tasks")
    seen: set[str] = set()
    kinds = {"inference": 0, "training": 0}
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Each task must be an object")
        task_id = _string(task.get("task_id"), "task_id")
        if task_id in seen:
            raise ValueError(f"Duplicate task_id: {task_id}")
        seen.add(task_id)
        for key in ("model", "engine", "workload", "quality_gate_id", "throughput_unit"):
            _string(task.get(key), f"{task_id}.{key}")
        kind = task.get("kind")
        if kind not in kinds:
            raise ValueError(f"{task_id}.kind must be inference or training")
        kinds[kind] += 1
        hardware = task.get("hardware")
        if not isinstance(hardware, dict):
            raise ValueError(f"{task_id}.hardware must be an object")
        nodes = hardware.get("nodes")
        devices = hardware.get("devices_per_node")
        if type(nodes) is not int or nodes < 1 or type(devices) is not int or devices < 1:
            raise ValueError(f"{task_id} has an invalid device topology")
        if hardware.get("devices_total") != nodes * devices:
            raise ValueError(f"{task_id}.devices_total does not match topology")
        _string(hardware.get("accelerator"), f"{task_id}.accelerator")
        baseline = _number(task.get("baseline_throughput"), f"{task_id}.baseline_throughput")
        sol = _number(task.get("sol_throughput"), f"{task_id}.sol_throughput")
        if sol <= baseline:
            raise ValueError(f"{task_id}: SOL must be greater than baseline")
    if kinds != {"inference": 16, "training": 4}:
        raise ValueError("The paper inventory consists of 16 inference and 4 training tasks")
    return catalog


def validate_lite_set(path: Path, catalog: dict[str, Any]) -> list[str]:
    lite = read_json(path)
    ids = lite.get("task_ids") if isinstance(lite, dict) else None
    if not isinstance(ids, list) or len(ids) != 5 or len(set(ids)) != 5:
        raise ValueError("Lite Set must contain five unique task IDs")
    by_id = {row["task_id"]: row for row in catalog["tasks"]}
    for task_id in ids:
        if task_id not in by_id:
            raise ValueError(f"Unknown Lite task: {task_id}")
        hw = by_id[task_id]["hardware"]
        if (hw["nodes"], hw["devices_per_node"], hw["accelerator"]) != (1, 1, "NVIDIA H20"):
            raise ValueError(f"{task_id} is not a single-H20 task")
    return ids


def _safe_tar_path(name: str) -> str:
    if not name or "\x00" in name or name.startswith("/") or "\\" in name:
        raise ValueError(f"Unsafe archive path: {name!r}")
    while name.startswith("./"):
        name = name[2:]
    name = name.rstrip("/")
    if name in ("", "."):
        return "."
    parts = name.split("/")
    if any(part in ("", ".", "..") for part in parts) or PurePosixPath(name).is_absolute():
        raise ValueError(f"Unsafe archive path: {name!r}")
    return name


def inspect_oci_layer(path: Path, *, max_uncompressed_bytes: int = 32 * 1024**3,
                      max_entries: int = 100_000) -> dict[str, Any]:
    """Inspect a candidate layer without extracting or executing it."""
    if not path.is_file():
        raise ValueError(f"Submission does not exist: {path}")
    compressed_hash = hashlib.sha256()
    compressed_size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            compressed_hash.update(chunk)
            compressed_size += len(chunk)
    diff_hash = hashlib.sha256()
    expanded = 0
    try:
        with gzip.open(path, "rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                diff_hash.update(chunk)
                expanded += len(chunk)
                if expanded > max_uncompressed_bytes:
                    raise ValueError("Layer exceeds maximum uncompressed size")
        paths: set[str] = set()
        launch_ok = False
        count = 0
        with tarfile.open(path, mode="r|gz") as archive:
            for member in archive:
                count += 1
                if count > max_entries:
                    raise ValueError("Layer exceeds maximum entry count")
                name = _safe_tar_path(member.name)
                if name == "." and member.isdir():
                    continue
                if name in paths:
                    raise ValueError(f"Duplicate archive path: {name}")
                paths.add(name)
                if not (member.isfile() or member.isdir()):
                    raise ValueError(f"Unsupported archive entry type: {name}")
                if name == "launch.sh":
                    if not member.isfile() or member.mode & 0o111 == 0:
                        raise ValueError("Root launch.sh must be an executable regular file")
                    launch_ok = True
    except (OSError, EOFError, gzip.BadGzipFile, tarfile.TarError) as exc:
        raise ValueError(f"Invalid gzip tar layer: {exc}") from exc
    if not launch_ok:
        raise ValueError("OCI layer must include executable launch.sh at archive root")
    return {
        "media_type": LAYER_MEDIA_TYPE,
        "digest": "sha256:" + compressed_hash.hexdigest(),
        "diff_id": "sha256:" + diff_hash.hexdigest(),
        "compressed_size": compressed_size,
        "uncompressed_size": expanded,
        "entry_count": count,
        "validation": "structural_only",
    }


def sol_score(baseline: float, candidate: float, sol: float) -> float:
    baseline = _number(baseline, "baseline")
    candidate = _number(candidate, "candidate")
    sol = _number(sol, "sol")
    if sol <= baseline:
        raise ValueError("SOL throughput must exceed baseline throughput")
    t_base, t_candidate, t_sol = 1 / baseline, 1 / candidate, 1 / sol
    if candidate >= sol:
        return 1.0
    score = (t_base - t_sol) / ((t_candidate - t_sol) + (t_base - t_sol))
    return min(1.0, max(0.0, score))


def score_result(row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("Result must be an object")
    for field in ("task_id", "agent_model", "evaluation_status"):
        _string(row.get(field), field)
    if row["evaluation_status"] == "not_run":
        return {"task_id": row["task_id"], "agent_model": row["agent_model"],
                "formal": False, "speedup": None, "sol_score": None, "faster": None,
                "reason": _string(row.get("reason"), "reason")}
    if row["evaluation_status"] != "completed":
        raise ValueError("evaluation_status must be completed or not_run")
    fields = ("deployment_status", "compliance_status", "quality_gate_status", "performance_status")
    for field in fields:
        if row.get(field) not in ("passed", "failed", "inconclusive", "not_run"):
            raise ValueError(f"Invalid {field}")
    failures = [field for field in fields if row[field] != "passed"]
    if failures:
        return {"task_id": row["task_id"], "agent_model": row["agent_model"],
                "formal": True, "speedup": 0.0, "sol_score": 0.0, "faster": False,
                "reason": "formal_zero:" + ",".join(failures)}
    for field in ("workload_sha256", "hardware_sha256"):
        _digest(row.get(field), field)
    baseline = _number(row.get("baseline_throughput"), "baseline_throughput")
    candidate = _number(row.get("candidate_throughput"), "candidate_throughput")
    sol = _number(row.get("sol_throughput"), "sol_throughput")
    speedup = candidate / baseline
    return {"task_id": row["task_id"], "agent_model": row["agent_model"], "formal": True,
            "speedup": speedup, "sol_score": sol_score(baseline, candidate, sol),
            "faster": speedup > 1.10, "reason": "validated",
            "throughput_unit": _string(row.get("throughput_unit"), "throughput_unit"),
            "workload_sha256": row["workload_sha256"], "hardware_sha256": row["hardware_sha256"]}


def aggregate_results(rows: list[dict[str, Any]], eligible_task_ids: list[str]) -> dict[str, Any]:
    if not isinstance(eligible_task_ids, list) or not eligible_task_ids:
        raise ValueError("eligible_task_ids must be a nonempty list")
    if len(set(eligible_task_ids)) != len(eligible_task_ids):
        raise ValueError("eligible_task_ids contains duplicates")
    by_id = {}
    for row in rows:
        task_id = _string(row.get("task_id"), "task_id")
        if task_id in by_id:
            raise ValueError(f"Duplicate result for task {task_id}")
        by_id[task_id] = row
    if set(by_id) != set(eligible_task_ids):
        raise ValueError("Results must match the eligible task set exactly")
    ordered = [by_id[task_id] for task_id in eligible_task_ids]
    if any(row.get("formal") is not True for row in ordered):
        raise ValueError("Not-run tasks cannot enter the formal denominator")
    speedups = [_number(row.get("speedup"), "speedup", zero=True) for row in ordered]
    scores = [_number(row.get("sol_score"), "sol_score", zero=True) for row in ordered]
    if any(score > 1 for score in scores):
        raise ValueError("SOL scores must be in [0, 1]")
    faster = sum(value > 1.10 for value in speedups)
    return {"eligible_tasks": len(ordered), "faster_count": faster,
            "faster_rate_percent": 100 * faster / len(ordered),
            "median_speedup": statistics.median(speedups),
            "mean_sol_score": statistics.fmean(scores),
            "task_ids": eligible_task_ids}


def validate_run(manifest: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    """Check job separation and digest invariants in a trusted scheduler manifest."""
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("Run manifest must use schema_version=1")
    if manifest.get("task_id") != task.get("task_id"):
        raise ValueError("Run task_id does not match fixed task contract")
    jobs = {name: manifest.get(name) for name in ("agent_job", "deployment_job", "benchmark_job")}
    if any(not isinstance(job, dict) for job in jobs.values()):
        raise ValueError("Manifest must contain Agent, deployment and Benchmark jobs")
    ids = [_string(job.get("job_id"), "job_id") for job in jobs.values()]
    if len(set(ids)) != 3:
        raise ValueError("Three jobs must have distinct job_id values")
    agent, deploy, bench = jobs["agent_job"], jobs["deployment_job"], jobs["benchmark_job"]
    base = _digest(agent.get("baseline_image_digest"), "agent baseline image")
    if _digest(deploy.get("baseline_image_digest"), "deployment baseline image") != base:
        raise ValueError("Agent and deployment jobs must pin the same baseline image")
    layer = _digest(agent.get("submission_layer_digest"), "submission layer")
    _digest(agent.get("submission_diff_id"), "submission diff_id")
    if _digest(deploy.get("applied_layer_digest"), "applied layer") != layer:
        raise ValueError("Deployment must apply the submitted layer digest")
    hardware = task["hardware"]
    ranks_expected = hardware["nodes"] * hardware["devices_per_node"]
    ranks = deploy.get("rank_layer_digests")
    if not isinstance(ranks, list) or len(ranks) != ranks_expected:
        raise ValueError(f"Deployment must report all {ranks_expected} ranks")
    seen = {}
    for item in ranks:
        if not isinstance(item, dict) or type(item.get("rank")) is not int:
            raise ValueError("Invalid rank layer digest entry")
        rank = item["rank"]
        if rank in seen:
            raise ValueError(f"Duplicate rank: {rank}")
        seen[rank] = _digest(item.get("layer_digest"), f"rank[{rank}] layer")
    if set(seen) != set(range(ranks_expected)) or any(value != layer for value in seen.values()):
        raise ValueError("Every deployment rank must use the exact submitted layer digest")
    service = _string(deploy.get("service_id"), "deployment service_id")
    _string(bench.get("verifier_image_digest"), "verifier image digest")
    if bench.get("candidate_layer_attached") is not False or bench.get("candidate_layer_digest") is not None:
        raise ValueError("Benchmark Job must not receive the candidate layer")
    if bench.get("candidate_layer_mounts") != []:
        raise ValueError("Benchmark Job must not mount candidate-controlled artifacts")
    if bench.get("benchmark_workspace_writable_by_candidate") is not False or bench.get("evaluator_read_only") is not True:
        raise ValueError("Benchmark evaluator must be read-only and isolated from candidate writes")
    image_layers = bench.get("image_layer_digests")
    if not isinstance(image_layers, list):
        raise ValueError("Benchmark image_layer_digests must be a list")
    if layer in [_digest(value, "benchmark image layer") for value in image_layers]:
        raise ValueError("Candidate layer leaked into the independent benchmark image")
    if bench.get("target_service_id") != service:
        raise ValueError("Benchmark Job must target the separately deployed candidate service")
    for field in ("workload_sha256", "hardware_sha256", "task_contract_sha256"):
        _digest(bench.get(field), field)
    return {"run_id": _string(manifest.get("run_id"), "run_id"),
            "task_id": manifest["task_id"], "deployment_ranks": ranks_expected,
            "all_ranks_use_candidate_digest": True, "benchmark_job_candidate_layer_free": True,
            "service_id": service, "job_ids": ids}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    catalog_cmd = commands.add_parser("catalog")
    catalog_cmd.add_argument("catalog", type=Path)
    catalog_cmd.add_argument("--lite-set", type=Path)
    layer_cmd = commands.add_parser("inspect-submission")
    layer_cmd.add_argument("archive", type=Path)
    score_cmd = commands.add_parser("score")
    score_cmd.add_argument("result", type=Path)
    score_cmd.add_argument("--output", type=Path)
    aggregate_cmd = commands.add_parser("aggregate")
    aggregate_cmd.add_argument("results", type=Path)
    aggregate_cmd.add_argument("--output", type=Path)
    quality_cmd = commands.add_parser("verify-quality")
    quality_cmd.add_argument("task_id")
    quality_cmd.add_argument("evidence", type=Path)
    quality_cmd.add_argument("--catalog", type=Path, required=True)
    quality_cmd.add_argument("--gates", type=Path, required=True)
    quality_cmd.add_argument("--acceptance-accuracy", type=float)
    run_cmd = commands.add_parser("validate-run")
    run_cmd.add_argument("manifest", type=Path)
    run_cmd.add_argument("--catalog", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "catalog":
            catalog = load_catalog(args.catalog)
            lite = validate_lite_set(args.lite_set, catalog) if args.lite_set else []
            result = {"task_count": 20, "inference_count": 16, "training_count": 4,
                      "lite_set_task_ids": lite, "task_ids": [row["task_id"] for row in catalog["tasks"]]}
        elif args.command == "inspect-submission":
            result = inspect_oci_layer(args.archive)
        elif args.command == "score":
            result = score_result(read_json(args.result))
        elif args.command == "verify-quality":
            from rsi_bench.quality import evaluate_quality
            catalog = load_catalog(args.catalog)
            gates = read_json(args.gates)
            mapping = gates.get("task_to_gate", {})
            if args.task_id not in mapping:
                raise ValueError(f"Unknown task_id: {args.task_id}")
            result = {"task_id": args.task_id, "gate_id": mapping[args.task_id],
                      **evaluate_quality(mapping[args.task_id], read_json(args.evidence),
                                         args.acceptance_accuracy)}
        elif args.command == "aggregate":
            payload = read_json(args.results)
            result = aggregate_results(payload["results"], payload["eligible_task_ids"])
        else:
            catalog = load_catalog(args.catalog)
            manifest = read_json(args.manifest)
            by_id = {row["task_id"]: row for row in catalog["tasks"]}
            result = validate_run(manifest, by_id[manifest["task_id"]])
        if getattr(args, "output", None):
            write_json(args.output, result)
            print(f"Wrote {args.output}")
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
    except (OSError, KeyError, TypeError, ValueError) as exc:
        parser.exit(2, f"RSIBench-Infra error: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
