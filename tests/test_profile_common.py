"""Profiler helpers preserve request failures and distinguish invalid input from code defects."""

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / ".agents/skills/llm-torch-profiler-analysis/scripts/profile_common.py"
)
spec = importlib.util.spec_from_file_location("profiler_common_regression", SCRIPT)
helpers = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helpers
spec.loader.exec_module(helpers)


@pytest.mark.parametrize("status_code", [404, 405, 501])
def test_missing_chat_endpoint_uses_completion_api(status_code: int) -> None:
    """Servers without a chat endpoint can still use the completion endpoint."""
    error = HTTPError(
        "http://localhost/v1/chat/completions", status_code, "unsupported", {}, None
    )
    with patch.object(helpers.request, "urlopen") as open_url:
        response = open_url.return_value
        response.__enter__.return_value.read.return_value = b"{}"
        open_url.side_effect = [error, response]
        helpers.send_probe_request(
            "http://localhost", "hello", 8, 42, "vllm", "test-model"
        )
        requests = [call.args[0] for call in open_url.call_args_list]
    assert [request.full_url for request in requests] == [
        "http://localhost/v1/chat/completions",
        "http://localhost/v1/completions",
    ]
    assert json.loads(requests[1].data) == {
        "model": "test-model",
        "prompt": "hello",
        "temperature": 0.0,
        "max_tokens": 8,
        "stream": False,
    }


@pytest.mark.parametrize("failure", [401, 500, "timeout"])
def test_failed_request_is_not_submitted_again(failure: int | str) -> None:
    """Authentication errors, server failures and timeouts must not trigger a second generation."""
    error = (
        TimeoutError("request timed out")
        if failure == "timeout"
        else HTTPError(
            "http://localhost/v1/chat/completions", failure, "failed", {}, None
        )
    )
    with patch.object(helpers.request, "urlopen", side_effect=error) as open_url:
        with pytest.raises(type(error)) as raised:
            helpers.send_probe_request(
                "http://localhost", "hello", 8, 42, "vllm", "test-model"
            )
        assert raised.value is error
        assert open_url.call_count == 1


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
