"""Exercise offline diagnosis with synthetic logs, without torch or a model."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / ".agents/skills/training-inference-change/scripts/compare_numerics.py"
)
spec = importlib.util.spec_from_file_location("offline_compare_numerics", SCRIPT)
compare = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = compare
spec.loader.exec_module(compare)


def log(key="layers.0/op_0_mul", *, mean="0.0", phase="forward", output_hash="4.0"):
    return (
        "Excluded ops dispatched: aten.empty, aten.detach\n"
        f"[{key}]\n"
        "  Shape: torch.Size([2, 4]), Dtype: torch.float32\n"
        "  L2 norm: 2.0\n"
        "  Min: -1.0\n"
        "  Max: 1.0\n"
        f"  Mean: {mean}\n"
        f"  Output hash: {output_hash}\n"
        "  Location: model.py:10\n"
        f"  Phase: {phase}\n"
    )


def entries(tmp_path, left, right):
    a, b = tmp_path / "a.log", tmp_path / "b.log"
    a.write_text(left)
    b.write_text(right)
    return compare.parse_log(a)[0], compare.parse_log(b)[0]


def test_parses_stats_phases_and_excluded_ops(tmp_path):
    path = tmp_path / "run.log"
    path.write_text(log(phase="backward"))
    captured, excluded = compare.parse_log(path)
    assert excluded == {"aten.empty", "aten.detach"}
    assert captured[0].phase == "backward"
    assert captured[0].stats["Mean"] == "0.0"
    assert captured[0].location == "model.py:10"


@pytest.mark.parametrize("output_hash", ["4.0", ""])
def test_stat_drift_is_not_hidden_by_equal_or_missing_hash(tmp_path, output_hash):
    a, b = entries(
        tmp_path, log(output_hash=output_hash), log(mean="0.5", output_hash=output_hash)
    )
    result = compare.match_entries(a, b)
    assert result[0][2] == "diff"
    assert result[0][3]["Mean"] > 0


def test_does_not_pair_forward_with_backward(tmp_path):
    a, b = entries(tmp_path, log(), log(phase="backward"))
    assert [row[2] for row in compare.match_entries(a, b)] == [
        "eager_only",
        "traced_only",
    ]


@pytest.mark.parametrize(
    ("other_key", "strategy"),
    [("layers.0/op_3_mul", "fuzzy"), ("another/op_2_mul", "stats")],
)
def test_heuristic_matching_records_strategy(tmp_path, other_key, strategy):
    a, b = entries(tmp_path, log(), log(key=other_key))
    result = compare.match_entries(a, b)
    assert result[0][2] == "match"
    assert result[0][4] == strategy


def test_manual_matching_consumes_pair_once_and_keeps_unmatched(tmp_path):
    a, b = entries(
        tmp_path,
        log(key="a/op_0_mul") + log(key="b/op_0_mul"),
        log(key="other/op_0_add"),
    )
    result = compare.match_entries(
        a, b, overrides={"a/op_0_mul": "other/op_0_add", "b/op_0_mul": "other/op_0_add"}
    )
    assert result[0][4] == "override"
    assert result[1][2] == "eager_only"


@pytest.mark.parametrize(
    ("left", "right"), [("inf", "0"), ("inf", "-inf"), ("nan", "0")]
)
def test_nonfinite_stats_render_without_crashing(tmp_path, left, right):
    a, b = entries(tmp_path, log(mean=left), log(mean=right))
    result = compare.match_entries(a, b)
    assert result[0][2] == "diff"
    report = compare.generate_html(result, "a", "b")
    assert "has-diff" in report


def test_report_escapes_log_fields_and_explains_limits(tmp_path):
    payload = '<img src=x onerror="alert(1)">'
    a, b = entries(tmp_path, log(key=payload), log(key=payload))
    a[0].location = payload
    a[0].stats["Shape"] = payload
    report = compare.generate_html(compare.match_entries(a, b), "a", "b", name1=payload)
    assert payload not in report
    assert "&lt;img" in report
    assert "do not prove tensor equality" in report


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_cli_creates_report_with_differences_without_claiming_parity(tmp_path):
    a, b = tmp_path / "基准 日志.log", tmp_path / "candidate.log"
    a.write_text(log())
    b.write_text(log(mean="0.5"))
    output = tmp_path / "comparison.html"
    result = run(a, b, "-o", output)
    assert result.returncode == 0, result.stderr
    assert "1 diffs" in output.read_text()
    assert "not parity" in output.read_text()
    output.write_text("existing report")
    assert run(a, b, "-o", output).returncode != 0
    assert output.read_text() == "existing report"
    assert run(a, b, "-o", output, "--overwrite").returncode == 0


@pytest.mark.parametrize("alias", ["same", "symlink", "hardlink"])
def test_cli_never_overwrites_input(tmp_path, alias):
    a, b = tmp_path / "a.log", tmp_path / "b.log"
    a.write_text(log())
    b.write_text(log())
    output = a
    if alias != "same":
        output = tmp_path / "alias.html"
        if alias == "symlink":
            output.symlink_to(a)
        else:
            output.hardlink_to(a)
    original = a.read_bytes()
    assert run(a, b, "-o", output, "--overwrite").returncode != 0
    assert a.read_bytes() == original


@pytest.mark.parametrize(
    "bad", ["", "not an activation log", "[op]\n", log(phase="unknown")]
)
def test_cli_rejects_unusable_logs_without_report(tmp_path, bad):
    a, b, output = tmp_path / "a.log", tmp_path / "b.log", tmp_path / "out.html"
    a.write_text(log())
    b.write_text(bad)
    result = run(a, b, "-o", output)
    assert result.returncode != 0
    assert not output.exists()
