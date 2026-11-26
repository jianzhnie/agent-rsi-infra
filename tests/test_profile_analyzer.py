"""Behavior regressions for local profiler analysis and trace caches."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

from autoresearch.profile_analyzer import (  # noqa: E402 -- numpy is optional outside profiler environments
    cli,
    intervals,
    parse,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def trace_path(tmp_path):
    path = tmp_path / "rank0.pt.trace.json"
    path.write_text(
        json.dumps(
            {
                "traceEvents": [
                    {
                        "ph": "X",
                        "cat": "kernel",
                        "name": "matmul",
                        "ts": 100,
                        "dur": 20,
                        "pid": 0,
                        "tid": 0,
                        "args": {"device": 0, "stream": 7},
                    }
                ]
            }
        )
    )
    return path


def test_same_size_rewrite_invalidates_parse_and_analysis_caches(
    trace_path, tmp_path
) -> None:
    """A trace rewritten within one second must not reuse its old timing results."""
    initial_time_ns = 1_700_000_000_100_000_000
    os.utime(trace_path, ns=(initial_time_ns, initial_time_ns))
    cache_directory = tmp_path / "cache"
    options = {"cache_dir": str(cache_directory)}
    first = cli.analyze_path((str(trace_path), options))
    assert first["primary"]["window"]["wall_us"] == 20
    assert cli.analyze_path((str(trace_path), options))["cache"]["analysis_from_cache"]

    original_size = trace_path.stat().st_size
    trace_path.write_text(trace_path.read_text().replace('"dur": 20', '"dur": 40'))
    os.utime(trace_path, ns=(initial_time_ns + 1, initial_time_ns + 1))
    assert trace_path.stat().st_size == original_size
    second = cli.analyze_path((str(trace_path), options))
    assert second["primary"]["window"]["wall_us"] == 40
    assert not second["cache"]["parse_from_cache"]
    assert not second["cache"]["analysis_from_cache"]


def test_unwritable_cache_does_not_prevent_trace_analysis(trace_path, tmp_path) -> None:
    """A cache directory that is a regular file must not hide valid trace results."""
    cache_path = tmp_path / "cache"
    cache_path.write_text("occupied")
    result = cli.analyze_path((str(trace_path), {"cache_dir": str(cache_path)}))
    assert result["primary"]["conservation"]["ok"]
    assert result["primary"]["window"]["wall_us"] == 20
    assert result["cache"]["cache_file"] is None


def test_module_cli_emits_json_without_writing_caches(trace_path, tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "autotuner.profile_analyzer",
            "--profile-dir",
            str(trace_path),
            "--json",
            "--no-cache",
            "--jobs",
            "1",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["ranks"][0]["primary"]["conservation"]["ok"]
    assert list(tmp_path.iterdir()) == [trace_path]


def test_interval_partition_conserves_duration_at_shared_boundaries() -> None:
    occupied = intervals.union([5, 0, 2], [7, 2, 5])
    gaps = intervals.complement(occupied, 0, 10)
    assert intervals.total(occupied) + intervals.total(gaps) == 10
    assert intervals.overlap_total(occupied, gaps) == 0
    assert intervals.contains_points(occupied, [0, 7]).tolist() == [True, False]
    assert intervals.intersect(occupied, intervals.union([8], [9]))[0].size == 0


def test_corrupt_parse_cache_is_rebuilt_from_trace(trace_path, tmp_path) -> None:
    cache_directory = tmp_path / "cache"
    _, _, from_cache = parse.load_rank(str(trace_path), cache_dir=str(cache_directory))
    assert not from_cache
    cache_file = next(cache_directory.glob("*.npz"))
    cache_file.write_bytes(b"not a numpy archive")
    _, arrays, from_cache = parse.load_rank(
        str(trace_path), cache_dir=str(cache_directory)
    )
    assert not from_cache
    assert arrays["g_dur"].tolist() == [20]


def test_non_object_analysis_cache_is_ignored(trace_path, tmp_path) -> None:
    """Valid JSON with the wrong shape must not prevent rebuilding an analysis."""
    cache_directory = tmp_path / "cache"
    options = {"cache_dir": str(cache_directory)}
    first = cli.analyze_path((str(trace_path), options))
    assert "error" not in first
    cache_file = next(cache_directory.glob("*.analysis.json"))
    cache_file.write_text("[]")
    result = cli.analyze_path((str(trace_path), options))
    assert result["primary"]["conservation"]["ok"]
    assert not result["cache"]["analysis_from_cache"]
