import io
import json
import tarfile
from pathlib import Path

import pytest

from rsi_bench.protocol import (
    aggregate_results,
    inspect_oci_layer,
    load_catalog,
    score_result,
    sol_score,
    validate_lite_set,
    validate_run,
)
from rsi_bench.quality import evaluate_quality

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "benchmarks/rsibench_infra/tasks.json"
LITE_PATH = ROOT / "benchmarks/rsibench_infra/lite_set.json"


def passing_row(**overrides):
    row = {
        "task_id": "task-a", "agent_model": "agent-x", "evaluation_status": "completed",
        "deployment_status": "passed", "compliance_status": "passed",
        "quality_gate_status": "passed", "performance_status": "passed",
        "baseline_throughput": 100.0, "candidate_throughput": 120.0,
        "sol_throughput": 200.0, "throughput_unit": "tokens/s",
        "workload_sha256": "sha256:" + "a" * 64,
        "hardware_sha256": "sha256:" + "b" * 64,
    }
    row.update(overrides)
    return row


def test_paper_catalog_and_lite_set_are_complete():
    catalog = load_catalog(CATALOG_PATH)
    lite = validate_lite_set(LITE_PATH, catalog)
    assert len(catalog["tasks"]) == 20
    assert sum(t["kind"] == "inference" for t in catalog["tasks"]) == 16
    assert sum(t["kind"] == "training" for t in catalog["tasks"]) == 4
    assert len(lite) == 5


def test_sol_score_anchor_points_and_saturation():
    assert sol_score(100, 100, 200) == pytest.approx(0.5)
    assert sol_score(100, 200, 200) == pytest.approx(1.0)
    assert sol_score(100, 300, 200) == pytest.approx(1.0)


def test_formal_failures_are_zero_and_not_run_is_unscored():
    failed = score_result(passing_row(quality_gate_status="failed", candidate_throughput=500))
    assert failed["formal"] is True and failed["speedup"] == 0
    not_run = score_result({"task_id": "x", "agent_model": "a",
                            "evaluation_status": "not_run", "reason": "API quota"})
    assert not_run["formal"] is False and not_run["speedup"] is None


def test_slowdowns_and_strict_faster_threshold_are_preserved():
    assert score_result(passing_row(candidate_throughput=90))["speedup"] == pytest.approx(0.9)
    assert score_result(passing_row(candidate_throughput=110))["faster"] is False
    assert score_result(passing_row(candidate_throughput=110.01))["faster"] is True


def test_aggregate_keeps_formal_zeroes_and_exact_denominator():
    fast = score_result(passing_row(task_id="a", candidate_throughput=120))
    zero = score_result(passing_row(task_id="b", quality_gate_status="failed"))
    report = aggregate_results([fast, zero], ["a", "b"])
    assert report["eligible_tasks"] == 2
    assert report["faster_rate_percent"] == 50
    with pytest.raises(ValueError, match="exactly"):
        aggregate_results([fast], ["a", "b"])


def test_layer_inspection_is_structural_and_returns_both_digests(tmp_path):
    archive = tmp_path / "submit_oci.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        data = b"#!/bin/sh\nexec python serve.py\n"
        info = tarfile.TarInfo("launch.sh")
        info.mode = 0o755
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    result = inspect_oci_layer(archive)
    assert result["digest"].startswith("sha256:")
    assert result["diff_id"].startswith("sha256:")
    assert result["validation"] == "structural_only"


def run_manifest():
    digests = {name: "sha256:" + name * 64 for name in "abcd"}
    task = load_catalog(CATALOG_PATH)["tasks"][0]
    ranks = [{"rank": i, "layer_digest": digests["c"]}
             for i in range(task["hardware"]["devices_total"])]
    return task, {
        "schema_version": 1, "run_id": "r1", "task_id": task["task_id"],
        "agent_job": {"job_id": "agent", "baseline_image_digest": digests["a"],
                      "submission_layer_digest": digests["c"], "submission_diff_id": digests["d"]},
        "deployment_job": {"job_id": "serve", "baseline_image_digest": digests["a"],
                           "applied_layer_digest": digests["c"], "rank_layer_digests": ranks,
                           "service_id": "candidate-service"},
        "benchmark_job": {"job_id": "benchmark", "verifier_image_digest": digests["b"],
                          "image_layer_digests": [digests["a"], digests["b"]],
                          "candidate_layer_attached": False, "candidate_layer_digest": None,
                          "candidate_layer_mounts": [], "benchmark_workspace_writable_by_candidate": False,
                          "evaluator_read_only": True, "target_service_id": "candidate-service",
                          "workload_sha256": digests["d"], "hardware_sha256": digests["b"],
                          "task_contract_sha256": digests["a"]},
    }


def test_run_contract_enforces_same_layer_on_every_rank_and_separate_evaluator():
    task, manifest = run_manifest()
    result = validate_run(manifest, task)
    assert result["deployment_ranks"] == 32
    manifest["deployment_job"]["rank_layer_digests"][0]["layer_digest"] = "sha256:" + "e" * 64
    with pytest.raises(ValueError, match="Every deployment rank"):
        validate_run(manifest, task)


def test_run_contract_rejects_candidate_layer_in_benchmark_image():
    task, manifest = run_manifest()
    manifest["benchmark_job"]["image_layer_digests"].append(
        manifest["agent_job"]["submission_layer_digest"])
    with pytest.raises(ValueError, match="leaked"):
        validate_run(manifest, task)


def test_quality_gate_checks_task_specific_acceptance():
    assert evaluate_quality("gsm8k_088", {"accuracy": 0.9})["passed"]
    longbench = {"question_count": 100, "accuracy": 0.81}
    with pytest.raises(ValueError, match="acceptance_accuracy"):
        evaluate_quality("longbench_v2_100q_256k", longbench)
    assert evaluate_quality("longbench_v2_100q_256k", longbench, 0.8)["passed"]


def test_quality_gate_uses_all_reference_video_cases():
    good = {name: value for name, value in {
        "mean_framewise_lpips": 0.2, "worst_frame_lpips": 0.3,
        "mean_temporal_difference_mae": 0.04, "worst_pair_temporal_difference_mae": 0.1,
        "motion_magnitude_ratio": 1.0, "absolute_duration_error_seconds": 0.0001,
        "absolute_frame_timestamp_error_seconds": 0.00001,
        "video_dimensions_match": True, "video_frame_count_match": True,
        "video_frame_rate_match": True, "video_encoding_valid": True,
        "timestamps_valid": True,
    }.items()}
    assert evaluate_quality("wan22_video", {"cases": [good.copy() for _ in range(4)]})["passed"]
    good["motion_magnitude_ratio"] = 1.2
    assert not evaluate_quality("wan22_video", {"cases": [good] * 4})["passed"]


def test_reference_frame_and_action_gates_require_shape_and_count_contracts():
    chunks = [{
        "frame_count_matches": True, "frame_shape_matches": True,
        "event_id_matches": True, "mean_absolute_pixel_error": 1.0, "psnr_db": 36.0,
    } for _ in range(16)]
    good_world = {"chunk_count": 16, "total_frames": 189, "chunks": chunks}
    assert evaluate_quality("lingbot_world_frames", good_world)["passed"]
    chunks[3]["frame_count_matches"] = False
    assert not evaluate_quality("lingbot_world_frames", good_world)["passed"]

    cases = [{
        "action_shape_matches": True, "max_absolute_error": 0.04, "mean_absolute_error": 0.005,
    } for _ in range(16)]
    assert evaluate_quality("pi05_reference_actions", {"cases": cases})["passed"]
    cases[0]["action_shape_matches"] = False
    assert not evaluate_quality("pi05_reference_actions", {"cases": cases})["passed"]


def test_training_replay_rejects_missing_or_reordered_update_contract():
    update = {
        "update_index": 0, "finite": True, "masks_match": True,
        "input_count_matches": True, "optimizer_update_count_matches": True,
        "candidate_loss": 1.0, "reference_loss": 1.0,
        "candidate_global_grad_norm": 2.0, "reference_global_grad_norm": 2.0,
    }
    with pytest.raises(ValueError, match="admission"):
        evaluate_quality("training_curve_16", {"updates": [update] * 16})
    rows = [dict(update, update_index=i) for i in range(16)]
    rows[4]["update_index"] = 5
    with pytest.raises(ValueError, match="reordered"):
        evaluate_quality("training_curve_16", {
            "admission_checks_passed": True, "updates": rows,
        })
