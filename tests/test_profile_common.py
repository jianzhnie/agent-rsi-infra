"""Offline profiler inputs reject live capture and keep trace failures visible."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / ".agents/skills/llm-torch-profiler-analysis/scripts/profile_common.py"
)
spec = importlib.util.spec_from_file_location("profiler_common_regression", SCRIPT)
helpers = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helpers
spec.loader.exec_module(helpers)


def test_trace_discovery_does_not_hide_programming_errors(tmp_path: Path) -> None:
    """Malformed files may be skipped, but implementation errors must remain visible."""
    trace_path = tmp_path / "capture.json"
    trace_path.write_text("invalid JSON")
    assert not helpers.file_looks_like_trace(trace_path)
    assert helpers.detect_framework_from_path(trace_path) is None
    with patch.object(
        helpers, "load_trace_json", side_effect=RuntimeError("parser defect")
    ):
        with pytest.raises(RuntimeError, match="parser defect"):
            helpers.file_looks_like_trace(trace_path)
        with pytest.raises(RuntimeError, match="parser defect"):
            helpers.detect_framework_from_path(trace_path)


@pytest.mark.parametrize(
    "options",
    [["--url", "http://localhost"], ["--mapping-url", "http://localhost"], []],
)
def test_cli_rejects_online_or_missing_inputs(options: list[str]) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT.parent / "analyze_llm_torch_profile.py"),
            "triage",
            *options,
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "error:" in result.stderr


def test_cli_analyzes_local_trace_without_changing_input(tmp_path: Path) -> None:
    trace_path = tmp_path / "sglang_prefill.trace.json"
    trace_path.write_text(
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
    original = trace_path.read_bytes()
    for options in (
        ["--input", str(trace_path)],
        ["--mapping-input", str(trace_path), "--formal-input", str(trace_path)],
    ):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT.parent / "analyze_llm_torch_profile.py"),
                "triage",
                "--framework",
                "sglang",
                *options,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, result.stderr
        assert "matmul" in result.stdout
        assert trace_path.read_bytes() == original


def test_local_framework_detection_never_contacts_server(tmp_path: Path) -> None:
    trace_path = tmp_path / "profile.trace.json"
    trace_path.write_text(json.dumps({"traceEvents": []}))
    (tmp_path / "server_args.json").write_text(
        json.dumps({"model_path": "test", "tp_size": 2})
    )
    assert helpers.resolve_framework("vllm", input_path=trace_path) == "vllm"
    assert helpers.resolve_framework("auto", input_path=trace_path) == "sglang"
