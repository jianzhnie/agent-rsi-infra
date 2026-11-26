"""Shared helpers for unified LLM torch-profiler skill scripts."""

from __future__ import annotations

import gzip
import json
import re
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Sequence
from functools import lru_cache
from pathlib import Path

STAGE_ORDER = {"extend": 0, "prefill": 0, "decode": 1, "all": 2}
FRAMEWORK_LABELS = {
    "auto": "auto",
    "sglang": "SGLang",
    "vllm": "vLLM",
    "trtllm": "TensorRT-LLM",
    "tokenspeed": "TokenSpeed",
}
TRACE_FILE_PATTERNS = (
    "*.trace.json",
    "*.trace.json.gz",
    "*.pt.trace.json",
    "*.pt.trace.json.gz",
    "*.json",
    "*.json.gz",
)
TRACE_FILE_IGNORE_NAMES = {
    "server_args.json",
    "metadata.json",
    "config.json",
}
TRACE_METADATA_NAMES = {
    "process_name",
    "thread_name",
    "process_sort_index",
    "thread_sort_index",
}
NON_KERNEL_TRACE_CATEGORIES = ("python_function", "cpu_op", "trace")
PYTHON_SCOPE_NAME_PREFIXES = ("python/", "nn.module:")


@lru_cache(maxsize=65536)
def _normalize_text_cached(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    for token in (" ", "\t", "\n", "\r", "\v", "\f"):
        if token in text:
            return " ".join(text.split())
    return text


def normalize_text(value: object) -> str:
    return _normalize_text_cached(value if isinstance(value, str) else str(value))


def canonicalize_framework(value: object) -> str:
    lowered = normalize_text(value).lower().replace("_", "-")
    aliases = {
        "": "auto",
        "auto": "auto",
        "sglang": "sglang",
        "sgl": "sglang",
        "vllm": "vllm",
        "trt": "trtllm",
        "tllm": "trtllm",
        "trtllm": "trtllm",
        "tensorrt-llm": "trtllm",
        "tensorrtllm": "trtllm",
        "tokenspeed": "tokenspeed",
        "token-speed": "tokenspeed",
        "ts": "tokenspeed",
    }
    return aliases.get(lowered, "auto")


def framework_display_name(value: object) -> str:
    return FRAMEWORK_LABELS.get(canonicalize_framework(value), str(value))


@lru_cache(maxsize=65536)
def _normalize_repo_relative_path_cached(text: str) -> str:
    text = text.replace("\\", "/")
    lowered = text.lower()
    for marker, normalized_marker in (
        ("python/sglang/", "python/sglang/"),
        ("sgl_kernel/", "sgl_kernel/"),
        ("vllm/", "vllm/"),
        ("python/tokenspeed/", "python/tokenspeed/"),
        ("tokenspeed/", "tokenspeed/"),
        ("tensorrt_llm/", "tensorrt_llm/"),
        ("tensorrt-llm/", "tensorrt_llm/"),
    ):
        idx = lowered.find(marker)
        if idx != -1:
            suffix = text[idx + len(marker) :].lstrip("/")
            return f"{normalized_marker}{suffix}".lstrip("/")
    idx = lowered.find("sglang/")
    if idx != -1:
        return ("python/" + text[idx:]).lstrip("/")
    return text.lstrip("/")


def normalize_repo_relative_path(path: object) -> str:
    return _normalize_repo_relative_path_cached(normalize_text(path))


def contains_any_keyword(text: str, keywords: Iterable[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def coerce_optional_int(value: object) -> int | None:
    if value in (None, "", "None"):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def extract_trace_events(trace: object) -> Sequence[dict]:
    if isinstance(trace, dict):
        events = trace.get("traceEvents", [])
        return events if isinstance(events, list) else []
    if isinstance(trace, list):
        return trace
    return []


def is_trace_metadata_name(name: object) -> bool:
    return str(name) in TRACE_METADATA_NAMES


def is_complete_duration_event(event: dict) -> bool:
    if event.get("ph") != "X":
        return False
    dur = event.get("dur")
    ts = event.get("ts")
    if dur is None or ts is None:
        return False
    try:
        return float(dur) > 0
    except (TypeError, ValueError):
        return False


def is_annotation_event(name: object, category: object) -> bool:
    lowered_name = normalize_text(name).lower()
    lowered_category = normalize_text(category).lower()
    return "annotation" in lowered_category or lowered_name.startswith("## call ")


def is_non_kernel_trace_category(category: object) -> bool:
    lowered_category = normalize_text(category).lower()
    return any(token in lowered_category for token in NON_KERNEL_TRACE_CATEGORIES)


def looks_like_python_scope_name(name: object) -> bool:
    lowered_name = normalize_text(name).lower()
    return ".py(" in lowered_name or lowered_name.startswith(PYTHON_SCOPE_NAME_PREFIXES)


def has_stream_marker(args: dict | None) -> bool:
    trace_args = args or {}
    return "stream" in trace_args or "cuda_stream" in trace_args


def load_trace_json(path: Path) -> dict:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return json.load(handle)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_server_args(path: Path) -> dict | None:
    resolved = path.resolve()
    candidate_dirs: list[Path] = []
    if resolved.is_file():
        candidate_dirs.extend([resolved.parent, resolved.parent.parent])
    else:
        candidate_dirs.extend([resolved, resolved.parent])

    seen: set[Path] = set()
    for candidate_dir in candidate_dirs:
        if candidate_dir in seen:
            continue
        seen.add(candidate_dir)
        candidate = candidate_dir / "server_args.json"
        if candidate.exists():
            with open(candidate, encoding="utf-8") as handle:
                return json.load(handle)
    return None


def detect_framework_from_text(text: object) -> str | None:
    lowered = normalize_text(text).lower()
    if not lowered:
        return None
    if any(token in lowered for token in ("tokenspeed", "token-speed", "/ts/")):
        return "tokenspeed"
    if any(
        token in lowered
        for token in (
            "tensorrt_llm",
            "tensorrt-llm",
            "trtllm",
            "pyexecutor",
        )
    ):
        return "trtllm"
    if "vllm" in lowered:
        return "vllm"
    if any(token in lowered for token in ("python/sglang/", "sgl_kernel/", "sglang/")):
        return "sglang"
    return None


def detect_framework_from_server_args(server_args: dict | None) -> str | None:
    if not isinstance(server_args, dict) or not server_args:
        return None
    lowered_keys = {normalize_text(key).lower() for key in server_args}
    text = json.dumps(server_args, sort_keys=True)
    if any(token in text.lower() for token in ("tokenspeed", "token-speed")):
        return "tokenspeed"
    if lowered_keys & {
        "attn_tp_size",
        "dense_tp_size",
        "moe_tp_size",
        "enable_mla_l1_5_cache",
        "mla_chunk_multiplier",
        "comm_fusion_max_num_tokens",
        "enable_allreduce_fusion",
    }:
        return "tokenspeed"
    text_hint = detect_framework_from_text(text)
    if text_hint:
        return text_hint
    if lowered_keys & {
        "attention_backend",
        "sampling_backend",
        "disable_cuda_graph",
        "disable_piecewise_cuda_graph",
        "chunked_prefill_size",
        "schedule_policy",
    }:
        return "sglang"
    return None


def detect_framework_from_trace(trace: object) -> str | None:
    text_samples: list[str] = []
    for event in extract_trace_events(trace)[:256]:
        text_samples.extend(
            [
                str(event.get("name", "")),
                str(event.get("cat", "")),
                str(event.get("pid", "")),
            ]
        )
        trace_args = event.get("args")
        if isinstance(trace_args, dict):
            for key, value in list(trace_args.items())[:8]:
                text_samples.append(str(key))
                if isinstance(value, str):
                    text_samples.append(value)
    return detect_framework_from_text(" ".join(text_samples))


def detect_framework_from_path(path: Path) -> str | None:
    hint = detect_framework_from_text(str(path))
    if hint:
        return hint
    server_args = load_server_args(path)
    hint = detect_framework_from_server_args(server_args)
    if hint:
        return hint
    if path.is_file():
        try:
            return detect_framework_from_trace(load_trace_json(path))
        except (OSError, ValueError, EOFError):
            return None
    trace_files = discover_trace_files(path, recursive=True, limit=3)
    for trace_file in trace_files:
        try:
            hint = detect_framework_from_trace(load_trace_json(trace_file))
        except (OSError, ValueError, EOFError):
            hint = None
        if hint:
            return hint
    return None


def resolve_framework(
    requested: object,
    *,
    input_path: Path | None = None,
    server_args: dict | None = None,
) -> str:
    explicit = canonicalize_framework(requested)
    if explicit != "auto":
        return explicit
    for hint in (
        detect_framework_from_server_args(server_args),
        detect_framework_from_path(input_path) if input_path else None,
    ):
        if hint:
            return hint
    return "sglang"


def parse_stage(path: Path) -> str:
    parts = [part.lower() for part in path.parts[-6:]]
    name = " ".join(parts)
    segment_path = "/" + "/".join(parts) + "/"
    if any(marker in name for marker in ("-extend", "-prefill", "_extend", "_prefill")):
        return "extend"
    if any(f"/{segment}/" in segment_path for segment in ("extend", "prefill")):
        return "extend"
    if any(marker in name for marker in ("-decode", "_decode")):
        return "decode"
    if "/decode/" in segment_path:
        return "decode"
    return "all"


def parse_tp_rank(path: Path) -> int | None:
    for pattern in (
        r"(?:^|[_-])tp(\d+)(?:[_.-]|$)",
        r"TP-(\d+)",
        r"(?:^|[_-])rank(\d+)(?:[_.-]|$)",
        r"(?:^|[_-])worker(\d+)(?:[_.-]|$)",
    ):
        match = re.search(pattern, path.name, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def file_looks_like_trace(path: Path) -> bool:
    name = path.name.lower()
    if name in TRACE_FILE_IGNORE_NAMES:
        return False
    if path.is_dir():
        return False
    if any(name.endswith(suffix) for suffix in (".trace.json", ".trace.json.gz")):
        return True
    if ".pt.trace.json" in name:
        return True
    if not any(name.endswith(suffix) for suffix in (".json", ".json.gz")):
        return False
    try:
        trace = load_trace_json(path)
    except (OSError, ValueError, EOFError):
        return False
    if isinstance(trace, dict):
        return isinstance(trace.get("traceEvents"), list)
    if isinstance(trace, list):
        return bool(trace) and all(isinstance(item, dict) for item in trace[:8])
    return False


def discover_trace_files(
    path: Path,
    *,
    recursive: bool,
    limit: int | None = None,
) -> list[Path]:
    if path.is_file():
        return [path] if file_looks_like_trace(path) else []

    candidates: list[Path] = []
    seen: set[Path] = set()
    for pattern in TRACE_FILE_PATTERNS:
        iterator = path.rglob(pattern) if recursive else path.glob(pattern)
        for candidate in iterator:
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            candidates.append(resolved)
    candidates = [
        candidate
        for candidate in candidates
        if candidate.exists() and file_looks_like_trace(candidate)
    ]
    candidates.sort(key=lambda item: item.stat().st_mtime)
    if limit is not None and limit >= 0:
        return candidates[-limit:] if limit else []
    return candidates


def newest_trace_dir(path: Path) -> Path:
    if path.is_file():
        return path.parent
    direct = discover_trace_files(path, recursive=False)
    if direct:
        return path
    traces = discover_trace_files(path, recursive=True)
    trace_dirs = list({trace.parent for trace in traces})
    if not trace_dirs:
        raise FileNotFoundError(f"No trace files found under {path}")
    trace_dirs.sort(
        key=lambda item: max(
            trace.stat().st_mtime for trace in traces if trace.parent == item
        )
    )
    return trace_dirs[-1]


def discover_trace_targets(
    path: Path, all_traces: bool
) -> tuple[list[Path], dict | None]:
    if path.is_file():
        return [path], load_server_args(path)

    direct_traces = discover_trace_files(path, recursive=False)
    recursive_traces = discover_trace_files(path, recursive=True)
    recursive_stages = {parse_stage(trace) for trace in recursive_traces}
    if (
        not direct_traces
        and recursive_traces
        and any(stage != "all" for stage in recursive_stages)
    ):
        traces = recursive_traces
        trace_dir = path
    else:
        trace_dir = newest_trace_dir(path)
        traces = discover_trace_files(trace_dir, recursive=False)
    if not traces:
        raise FileNotFoundError(f"No trace files found under {trace_dir}")

    non_merged = [trace for trace in traces if not trace.name.startswith("merged-")]
    selected = non_merged or traces
    if not all_traces:
        ranks = sorted(
            {
                rank
                for rank in (parse_tp_rank(trace) for trace in selected)
                if rank is not None
            }
        )
        if ranks:
            rank = 0 if 0 in ranks else ranks[0]
            selected = [trace for trace in selected if parse_tp_rank(trace) == rank]
        grouped: dict[str, list[Path]] = defaultdict(list)
        for trace in selected:
            grouped[parse_stage(trace)].append(trace)
        selected = [
            sorted(group, key=lambda item: item.stat().st_mtime)[-1]
            for group in grouped.values()
        ]

    selected.sort(key=lambda item: (STAGE_ORDER.get(parse_stage(item), 99), item.name))
    return selected, load_server_args(trace_dir)


def select_heaviest_pid(
    events: Sequence[dict],
    event_filter: Callable[[dict], bool],
    pid_substring: str | None = None,
    preferred_substrings: Iterable[str] = (),
) -> str | None:
    durations: Counter = Counter()
    for event in events:
        if not event_filter(event):
            continue
        pid = str(event.get("pid"))
        if pid_substring and pid_substring not in pid:
            continue
        durations[pid] += float(event["dur"])
    if not durations:
        return None

    for substring in preferred_substrings:
        preferred = [pid for pid in durations if substring in pid]
        if preferred:
            return max(preferred, key=lambda pid: durations[pid])
    return max(durations, key=lambda pid: durations[pid])
