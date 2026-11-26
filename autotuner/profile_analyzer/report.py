# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""Text rendering: overview and drill-down subcommands. Measurements only; no verdicts."""

from autotuner.profile_analyzer import memory, pipeline, summary, taxonomy

SHORT = {
    "gc": "gc",
    "allocator_cache_release": "cache-release",
    "device_sync_event_wait": "sync-wait",
    "blocking_allocation": "blocking-alloc",
    "host_device_copy_wait": "h<->d-copy",
    "comm_host_call": "comm-host",
    "data_loading": "data-load",
    "checkpoint_io": "ckpt-io",
    "optimizer_cpu_step": "optim-cpu",
    "kernel_launch_bound": "launch-bound",
    "python_other": "py-other",
}


def s_(us):
    return f"{us / 1000000.0:.2f}"


def pct(x, w):
    return 100.0 * x / w if w else 0.0


def trunc(s, n):
    s = str(s)
    return s if len(s) <= n else s[: n - 3] + "..."


def ok_ranks(run):
    return [r for r in run["ranks"] if not r.get("error")]


def coverage(run):
    rs = ok_ranks(run)
    cov = {
        "ranks_profiled": [r["coords"].get("rank") for r in rs],
        "errors": [
            {"path": r["path"], "error": r["error"]}
            for r in run["ranks"]
            if r.get("error")
        ],
    }
    if not rs:
        return cov
    ws = max((r["coords"].get("world_size") or 0) for r in rs)
    cov["world_size"] = ws
    pps = max((r["coords"].get("pp_size") or 1) for r in rs)
    cov["pp_size"] = pps
    cov["pp_stages_covered"] = sorted(
        {r["coords"].get("pp") for r in rs if r["coords"].get("pp") is not None}
    )
    cov["steps"] = sorted({r["primary"]["window"]["step"] for r in rs})
    cov["steps_per_rank"] = max(len(r["windows"]) for r in rs)
    cov["window_source"] = sorted({r["primary"]["window"]["source"] for r in rs})
    ev = {}
    ev["python_stacks"] = all(
        r["event_counts"].get("python_function", 0) > 0 for r in rs
    )
    ev["shapes"] = all(bool(r["flags"].get("record_shapes")) for r in rs)
    ev["memory_events"] = all(
        r["primary"]["memory"].get("has_memory_events") for r in rs
    )
    ev["flops_ops"] = sum(r.get("flops_ops", 0) for r in rs)
    ev["cuda_runtime"] = all(r["event_counts"].get("cuda_runtime", 0) > 0 for r in rs)
    ev["malloc_free_api"] = any(
        r["primary"]["memory"].get("malloc_free_recorded") for r in rs
    )
    nk = sum(r["comm_meta"]["n"] for r in rs)
    ninf = sum(r["comm_meta"]["no_pg"] for r in rs)
    ev["nccl_kernels"] = nk
    ev["nccl_pg_metadata_pct"] = (100.0 * (nk - ninf) / nk) if nk else None
    ev["nccl_inferred"] = {}
    for r in rs:
        for k, v in r["comm_meta"]["inferred"].items():
            ev["nccl_inferred"][k] = ev["nccl_inferred"].get(k, 0) + v
    cov["events"] = ev
    blind = []
    if ws and len(rs) < ws:
        blind.append(
            f"ranks not profiled: {int(ws - len(rs)):d} of {int(ws):d}; per-rank numbers cover only the listed ranks -> SLIME_PROFILE_ALL_RANKS=1 (profile all ranks)"
        )
    if pps > 1 and len(cov["pp_stages_covered"]) < pps:
        miss = [p for p in range(pps) if p not in cov["pp_stages_covered"]]
        blind.append(
            f"pipeline stages without a trace: {','.join(f'pp{int(p):d}' for p in miss)} -> the critical stage may be unprofiled"
        )
    if not ev["python_stacks"]:
        blind.append(
            "no python stacks: idle time resolves only to cpu_op/annotation names (gc, empty_cache, data "
            "loading callers invisible) -> with_stack=True (SLIME_PROFILE_WITH_STACK=1)"
        )
    if not ev["memory_events"]:
        blind.append(
            "no [memory] events: peak memory unknown -> profile_memory=True (SLIME_PROFILE_MEMORY=1)"
        )
    blind.append(
        "device free memory is not in the trace; allocator unreserved (device total - peak reserved) is "
        "NOT device free memory and overstates it (NCCL buffers, workspaces, fragmentation)"
    )
    if not ev["flops_ops"]:
        blind.append(
            "no FLOPs recorded: achieved TFLOP/s unknown -> with_flops=True (SLIME_PROFILE_WITH_FLOPS=1); "
            "TE / custom GEMMs report no FLOPs even then"
        )
    if not ev["malloc_free_api"]:
        blind.append(
            "cudaMalloc/cudaFree not in the trace: allocator churn visible only as blocking allocations "
            "and empty_cache calls"
        )
    if ninf:
        inf = ", ".join(
            f"{k!s} {int(v):d}"
            for k, v in sorted(ev["nccl_inferred"].items())
            if k != "deepep-kernel"
        )
        blind.append(
            f"{int(ninf):d} NCCL kernels carry no process-group metadata; dimension inferred ({inf!s})"
        )
    blind.append(
        "bus bandwidth = bytes / kernel duration, and kernel duration includes waiting for peers -> "
        "a lower bound on link speed, not a link measurement; PP p2p transfer time is only estimated "
        "(bytes / nominal link bandwidth)"
    )
    outside = [
        (
            r["coords"].get("rank"),
            r.get("outside_window_us", 0.0),
            r["primary"]["window"]["wall_us"],
        )
        for r in rs
        if r.get("outside_window_us", 0.0) > 0.05 * r["primary"]["window"]["wall_us"]
    ]
    if outside:
        blind.append(
            f"GPU activity outside the analyzed step window(s) is not decomposed: {', '.join((f'rank {k} {o / 1000000.0:.1f} s' for k, o, _ in outside[:6]))} -> inspect the raw trace or profile whole steps only"
        )
    if cov["steps_per_rank"] <= 1:
        blind.append(
            "one profiled step per rank: step-to-step variance unknown (profile >= 2 steps)"
        )
    blind.append(
        "host threads that launch no kernels (e.g. a gc/logging thread) are not used to attribute idle time"
    )
    cov["blind_spots"] = blind
    return cov


def overview(run, top_contrasts=5, quick=False):
    """Summary (key facts, first ~40 lines) then detail sections."""
    L, _ = summary.build(run)
    rs = ok_ranks(run)
    if quick or not rs:
        if quick:
            L.append(
                "(--quick: summary only; run without --quick for coverage, kernel shares, pipeline, comm, memcpy "
                "and host detail)"
            )
        return "\n".join(L)
    L.append("")
    L.append("======== detail ========")
    L.append(f"traces ({int(len(run['ranks'])):d}, rank order):")
    shown = run["ranks"] if len(run["ranks"]) <= 8 else run["ranks"][:6]
    for r in shown:
        L.append(
            f"  rank {r.get('rank', '?')!s:<4} {r['path']!s}{('  ERROR: ' + r['error'] if r.get('error') else '')!s}"
        )
    if len(run["ranks"]) > len(shown):
        L.append(f"  ... {int(len(run['ranks']) - len(shown)):d} more (see `ranks`)")
    cov = run["coverage"]
    L.append("")
    L.append("== Coverage ==")
    L.append(
        f"ranks profiled: {int(len(rs)):d} of world {cov.get('world_size')!s}: {trunc(cov['ranks_profiled'], 90)!s}"
    )
    if cov.get("pp_size", 1) > 1:
        L.append(
            f"pipeline stages covered: {','.join(f'pp{int(p):d}' for p in cov['pp_stages_covered'])!s} of PP={int(cov['pp_size']):d}"
        )
    L.append(
        f"step window: {','.join(cov['steps'])!s}; {int(cov['steps_per_rank']):d} step(s) per trace; {'; '.join(cov['window_source'])!s}"
    )
    ev = cov["events"]

    def yn(b):
        return "yes" if b else "NO"

    L.append(
        f"""events: python stacks {yn(ev["python_stacks"])} | shapes {yn(ev["shapes"])} | [memory] {yn(ev["memory_events"])} | FLOPs {yn(ev["flops_ops"])} | CUDA runtime {yn(ev["cuda_runtime"])} | cudaMalloc/Free {yn(ev["malloc_free_api"])} | NCCL PG metadata {(f"{ev['nccl_pg_metadata_pct']:.1f}%" if ev["nccl_pg_metadata_pct"] is not None else "n/a")}"""
    )
    L.append("cannot answer from this trace (-> what would):")
    for b in cov["blind_spots"]:
        L.append("  - " + b)
    L.append(
        "host = idle >= 1 ms spanned by a host frame on a kernel-launching thread; unattr = idle >= 1 ms with no "
        "such frame (or only step-level frames); fine = idle intervals < 1 ms"
    )
    multi = [r for r in rs if len(r.get("per_step") or []) > 1]
    if multi:
        r0 = multi[0]
        L.append(
            f"""per-step walls (rank {r0["coords"].get("rank")}): {", ".join(f"{x['step'].split('#')[-1]} {x['wall_us'] / 1000000.0:.2f} s" for x in r0["per_step"])}; tables show the last complete step (--step N selects another)"""
        )
    ks = [r["primary"]["kernels"] for r in rs if r["primary"]["kernels"].get("count")]
    if ks:
        lb = [
            pct(
                r["primary"]["idle"]["launch_api_overlap_idle_us"],
                r["primary"]["window"]["wall_us"],
            )
            for r in rs
        ]
        L.append(
            f"kernels: median {min(k['median_us'] for k in ks):.1f}-{max(k['median_us'] for k in ks):.1f} us, {min(k['small_lt10us_count_pct'] for k in ks):.0f}-{max(k['small_lt10us_count_pct'] for k in ks):.0f}% of launches < 10 us; GPU idle while host in launch APIs {min(lb):.1f}-{max(lb):.1f}% of wall"
        )

    L.append("")
    L += share_table(rs)

    pv = run["pipeline"]
    if pv.get("pp_size", 1) > 1 and pv.get("stages"):
        L.append("")
        L.append(
            f"== Pipeline (PP={int(pv['pp_size']):d}, {pv.get('microbatches') or '?'!s} microbatches) =="
        )
        L.append(
            f"{'stage'!s:<6} {'ranks'!s:<10} {'wall s'!s:>8} {'work s'!s:>8} {'p2p-wait s'!s:>11} {'host s'!s:>8} {'peak GiB'!s:>9} {'p2p-kern s'!s:>11} {'xfer-est'!s:>9}  {'waits on (receives from)'!s}"
        )
        for st in pv["stages"]:
            L.append(
                f"""{f"pp{int(st['pp']):d}"!s:<6} {trunc(",".join(str(x) for x in st["ranks"]), 10)!s:<10} {st["wall_us"] / 1000000.0:8.2f} {st["work_us"] / 1000000.0:8.2f} {st["p2p_wait_us"] / 1000000.0:11.2f} {st["host_stall_us"] / 1000000.0:8.2f} {(f"{st['peak_alloc_gib']:.1f}" if st["peak_alloc_gib"] is not None else "n/a")!s:>9} {st.get("p2p_kernel_us", 0.0) / 1000000.0:11.2f} {st.get("p2p_transfer_est_us", 0.0) / 1000000.0:9.2f}  {pipeline.waits_text(st, 3)!s}"""
            )
        L.append(
            "work = GPU busy minus PP p2p kernels not overlapped by compute; p2p wait = those kernels. A p2p kernel "
            "runs from launch until the peer's matching send/recv completes, so its duration includes waiting for "
            "the peer; xfer-est = bytes / nominal link bandwidth (estimate)"
        )

    L.append("")
    L.append(
        "== Communication by dimension (mean per profiled rank; exposed = not overlapped by compute) =="
    )
    L.append(
        f"{'dim'!s:<6} {'collectives (count/rank)'!s:<34} {'GB'!s:>7} {'kern s'!s:>8} {'union s'!s:>8} {'exposed s (min-max)'!s:>16} {'busbw GB/s'!s:>9} {'placement'!s:<11} {'vs nom'!s:>7}"
    )
    for row in comm_by_dim(run):
        exposure_text = f"{row['exposed_us'] / 1000000.0:.2f} ({row['exposed_min_us'] / 1000000.0:.2f}-{row['exposed_max_us'] / 1000000.0:.2f})"
        bandwidth_text = (
            f"{row['busbw']:.0f}" if row["busbw"] and row["bw_cov"] >= 0.5 else "n/a"
        )
        nominal_ratio_text = (
            f"{row['vs_nominal']:.2f}"
            if row["vs_nominal"] and row["bw_cov"] >= 0.5
            else "n/a"
        )
        L.append(
            f"{('other' if row['dim'] == 'other_comm' else row['dim'])!s:<6} {trunc(row['colls'], 34)!s:<34} {row['gb']:7.1f} {row['sum_us'] / 1000000.0:8.2f} {row['union_us'] / 1000000.0:8.2f} {exposure_text!s:>16} {(bandwidth_text)!s:>9} {row['placement']!s:<11} {(nominal_ratio_text)!s:>7}"
        )
    L.append(
        "busbw n/a when bytes are known for < 50% of the dimension's kernel time (e.g. coalesced p2p)"
    )
    L.append(
        "busbw uses NCCL factors (all-reduce 2(n-1)/n, all-gather/reduce-scatter/all-to-all (n-1)/n, p2p 1) and "
        "'vs nom' is against nominal NVLink/network per GPU; kernel time includes waiting for peers"
    )

    mc = [
        r
        for r in rs
        if pct(
            r["primary"]["buckets_us"]["memcpy_exposed"],
            r["primary"]["window"]["wall_us"],
        )
        >= 1.0
    ]
    if mc:
        L.append("")
        L.append(
            "== Exposed memcpy by direction (ranks with >= 1% of wall; s exposed / s overlapping compute / GB) =="
        )
        for r in mc[:8]:
            p = r["primary"]
            parts = [
                f"{d} {v['exposed_us'] / 1000000.0:.2f}/{v['overlap_compute_us'] / 1000000.0:.2f}/{v['bytes'] / 1000000000.0:.1f}"
                for d, v in p["memcpy"].items()
                if v["count"] and (v["union_us"] >= 0.001 * p["window"]["wall_us"])
            ]
            L.append(f"  rank {r['coords'].get('rank')!s:<5} {' | '.join(parts)!s}")
        if len(mc) > 8:
            L.append(f"  ... {int(len(mc) - 8):d} more ranks")

    heavy = [
        r
        for r in rs
        if pct(
            r["primary"]["buckets_us"]["host_total"], r["primary"]["window"]["wall_us"]
        )
        >= 5.0
    ]
    L.append("")
    L.append("== Host-side idle by class (ranks with host >= 5% of wall) ==")
    if not heavy:
        mx = max(
            rs,
            key=lambda r: pct(
                r["primary"]["buckets_us"]["host_total"],
                r["primary"]["window"]["wall_us"],
            ),
        )
        L.append(
            f"  none; largest is rank {mx['coords'].get('rank')} at {pct(mx['primary']['buckets_us']['host_total'], mx['primary']['window']['wall_us']):.1f}% of wall"
        )
    for r in heavy[:8]:
        p = r["primary"]
        w = p["window"]["wall_us"]
        cl = sorted(p["host_classes"].items(), key=lambda kv: -kv[1]["us"])
        L.append(
            f"  rank {r['coords'].get('rank')}: host {p['buckets_us']['host_total'] / 1000000.0:.1f} s = {pct(p['buckets_us']['host_total'], w):.1f}% of wall"
        )
        for c, v in cl[:4]:
            if v["us"] < 0.005 * w:
                continue
            fr = v["top_frames"][0]["frame"] if v["top_frames"] else ""
            L.append(
                f"     {SHORT.get(c, c)!s:<15} {v['us'] / 1000000.0:7.2f} s  {int(v['n_calls']):5d} calls  top: {trunc(fr, 70)!s}"
            )
        mem = p["memory"]
        extra = []
        if mem.get("empty_cache_calls"):
            extra.append(
                f"empty_cache calls {int(mem['empty_cache_calls']):d} ({mem['empty_cache_ms']:.0f} ms)"
            )
        if mem.get("blocking_alloc_ge5ms_n"):
            extra.append(
                f"allocations >= 5 ms: {int(mem['blocking_alloc_ge5ms_n']):d} ({mem['blocking_alloc_ge5ms_ms']:.0f} ms)"
            )
        if extra:
            L.append("     " + "; ".join(extra))
    if len(heavy) > 8:
        L.append(f"  ... {int(len(heavy) - 8):d} more ranks (see `rank R`)")
    L.append("")
    worst = max(rs, key=lambda r: r["primary"]["buckets_us"]["host_total"])
    L.append(
        "drill down: rank {} | gaps {} --top 20 | phases {} | memory {} | comm --dim EP | kernels --class gemm | "
        "stack {} --t0 MS --t1 MS | diff DIR_A DIR_B | --json [--json-full] | --quick".format(
            *tuple([worst["coords"].get("rank")] * 5)
        )
    )
    return "\n".join(L)


def _share_cols(rs):
    cols = ["compute"]
    for d in taxonomy.COMM_DIMS:
        if any(
            d in (r["primary"].get("kernel_share") or {}).get("rows", {}) for r in rs
        ):
            cols.append(d)
    cols.append("memcpy")
    return cols


def share_table(rs, title=True):
    """Each compute/comm/memcpy bucket as a share of summed GPU activity time and of step wall, side by side."""
    cols = _share_cols(rs)
    L = []
    if title:
        L.append("== Kernel-time share vs step-wall share per rank (kern%/step%) ==")
    L.append(
        f"""{"rank"!s:<6} {"pp"!s:<4} {" ".join(f"{('other' if c == 'other_comm' else c)!s:>13}" for c in cols)!s}"""
    )
    for r in rs[:24]:
        rows = (r["primary"].get("kernel_share") or {}).get("rows", {})
        cells = []
        for c in cols:
            v = rows.get(c)
            kernel_share_text = (
                f"{v['pct_of_gpu_activity_sum']:.1f}/{v['pct_of_step']:.1f}"
                if v
                else "-"
            )
            cells.append(f"{(kernel_share_text)!s:>13}")
        L.append(f"{r['coords'].get('rank')!s:<6} {_pp(r)!s:<4} {' '.join(cells)!s}")
    L.append(
        "kern% = share of summed GPU kernel+memcpy durations (overlapping streams counted twice; what v1's "
        "'Communication / Total Kernel' measured); step% = exposed share of step wall (the conserved buckets)"
    )
    return L


def _pp(r):
    c = r["coords"]
    return (
        (f"pp{int(c['pp']):d}")
        if c.get("pp") is not None and (c.get("pp_size") or 1) > 1
        else "-"
    )


def _cnt(x):
    return (f"{int(round(x)):d}") if x >= 1 else (f"{x:.1f}")


def comm_by_dim(run):
    rs = ok_ranks(run)
    n = float(len(rs)) or 1.0
    rows = []
    for dim in taxonomy.COMM_DIMS:
        tot = {
            "count": 0,
            "sum_us": 0.0,
            "union_us": 0.0,
            "exposed_us": 0.0,
            "bytes": 0.0,
        }
        exps, colls, place, nom = [], {}, set(), []
        for r in rs:
            c = r["primary"]["comm"][dim]
            tot["sum_us"] += c["sum_us"]
            tot["union_us"] += c["union_us"]
            tot["exposed_us"] += c["exposed_us"]
            tot["count"] += c["count"]
            exps.append(c["exposed_us"])
            for ct, v in (r["primary"]["comm_bw"].get(dim) or {}).items():
                colls[ct] = colls.get(ct, 0) + v["count"]
                tot["bytes"] += v["bytes"]
                place.add(v["placement"])
                if v["nominal_gbps"]:
                    nom.append(v["nominal_gbps"])
        if tot["count"] == 0:
            continue
        # aggregate bus bandwidth: sum(bus_bytes)/sum(time with bytes) over all ranks and collective types
        bus_b, bus_t = 0.0, 0.0
        for r in rs:
            for v in (r["primary"]["comm_bw"].get(dim) or {}).values():
                if v.get("bus_bytes") and v.get("bw_time_us"):
                    bus_b += v["bus_bytes"]
                    bus_t += v["bw_time_us"]
        busbw = bus_b / (bus_t * 1e-6) / 1e9 if bus_t > 0 else None
        pls = sorted(p for p in place if p != "unknown") or ["unknown"]
        if len(pls) > 1:
            pls = ["mixed"]
        nomv = max(nom) if nom and len(pls) == 1 else (min(nom) if nom else None)
        rows.append(
            {
                "dim": dim,
                "colls": ", ".join(
                    f"{k} {_cnt(v / n)}"
                    for k, v in sorted(colls.items(), key=lambda kv: -kv[1])
                ),
                "gb": tot["bytes"] / n / 1e9,
                "sum_us": tot["sum_us"] / n,
                "union_us": tot["union_us"] / n,
                "exposed_us": tot["exposed_us"] / n,
                "exposed_min_us": min(exps),
                "exposed_max_us": max(exps),
                "busbw": busbw,
                "bw_cov": (bus_t / tot["sum_us"]) if tot["sum_us"] else 0.0,
                "placement": "/".join(pls),
                "vs_nominal": (busbw / nomv) if (busbw and nomv) else None,
            }
        )
    return rows


def ranks_table(run):
    L = [
        f"{'rank'!s:<6} {'pp'!s:<5} {'coords'!s:<24} {'wall s'!s:>8} {'busy%'!s:>6} {'trace'!s}"
    ]
    for r in run["ranks"]:
        if r.get("error"):
            L.append(f"{r.get('rank', '?')!s:<6} ERROR {r['error']!s}  {r['path']!s}")
            continue
        c = r["coords"]
        cs = " ".join(
            f"{k}{c[k]}/{c.get(k + '_size')}"
            for k in ("tp", "cp", "dp", "ep")
            if c.get(k) is not None
        )
        p = r["primary"]
        L.append(
            f"{c.get('rank')!s:<6} {_pp(r)!s:<5} {cs!s:<24} {p['window']['wall_us'] / 1000000.0:8.2f} {pct(p['gpu_busy_us'], p['window']['wall_us']):6.1f} {r['path']!s}"
        )
    return "\n".join(L)


def rank_detail(r, top_n=10):
    if r.get("error"):
        return f"rank {r.get('rank')}: ERROR {r['error']} ({r['path']})"
    p = r["primary"]
    w = p["window"]["wall_us"]
    b = p["buckets_us"]
    L = [
        f"RANK {r['coords'].get('rank')}  {r['path']}  coords {_coords_str(r['coords'])}"
    ]
    L.append(
        f"device {r['device'].get('name')} | step {p['window']['step']} | window {w / 1000000.0:.2f} s ({p['window']['source']}) | driver threads {r['driver_threads']}"
    )
    L.append("")
    L.append("Decomposition of step wall (sums to 100%):")
    L.append(f"  {'bucket'!s:<44} {'s'!s:>9} {'%'!s:>6}")
    L.append(
        f"  {'compute (any compute kernel running)'!s:<44} {s_(b['compute'])!s:>9} {pct(b['compute'], w):6.1f}"
    )
    for c, v in p["compute"].items():
        if v["exclusive_us"] > 0:
            L.append(
                f"    {c!s:<42} {s_(v['exclusive_us'])!s:>9} {pct(v['exclusive_us'], w):6.1f}   work(sum) {s_(v['sum_us'])!s} s, overlap {s_(max(v['sum_us'] - v['union_us'], 0))!s} s, n={int(v['count']):d}"
            )
    L.append(
        f"  {'communication exposed (no compute running)'!s:<44} {s_(b['comm_exposed'])!s:>9} {pct(b['comm_exposed'], w):6.1f}"
    )
    for c, v in p["comm"].items():
        if v["count"]:
            L.append(
                f"    {c!s:<42} {s_(v['exclusive_us'])!s:>9} {pct(v['exclusive_us'], w):6.1f}   own union {s_(v['union_us'])!s} s: exposed {s_(v['exposed_us'])!s}, overlapped {s_(v['overlapped_us'])!s}; n={int(v['count']):d}"
            )
    L.append(
        f"  {'memcpy/memset exposed (no compute/comm)'!s:<44} {s_(b['memcpy_exposed'])!s:>9} {pct(b['memcpy_exposed'], w):6.1f}"
    )
    for c, v in p["memcpy"].items():
        if v["count"]:
            L.append(
                f"    {c!s:<42} {s_(v['exclusive_us'])!s:>9} {pct(v['exclusive_us'], w):6.1f}   union {s_(v['union_us'])!s} s, overlaps compute {s_(v['overlap_compute_us'])!s} s, {v['bytes'] / 1000000000.0:.2f} GB, n={int(v['count']):d}"
            )
    L.append(
        f"  {'host-side idle (>= 1 ms, host frame active)'!s:<44} {s_(b['host_total'])!s:>9} {pct(b['host_total'], w):6.1f}"
    )
    for c in taxonomy.HOST_CLASSES:
        v = p["host_classes"].get(c)
        if not v:
            continue
        L.append(
            f"""    {taxonomy.HOST_CLASS_LABEL[c]!s:<42} {s_(v["us"])!s:>9} {pct(v["us"], w):6.1f}   {int(v["n_calls"]):d} calls; top: {"; ".join(f"{trunc(f['frame'], 60)!s} {f['us'] / 1000.0:.0f} ms x{int(f['n']):d}" for f in v["top_frames"][:2])!s}"""
        )
    L.append(
        f"  {'unattributed idle (>= 1 ms, no host frame)'!s:<44} {s_(b['unattributed_idle'])!s:>9} {pct(b['unattributed_idle'], w):6.1f}"
    )
    L.append(
        f"  {'fine-grained idle (intervals < 1 ms)'!s:<44} {s_(b['fine_idle'])!s:>9} {pct(b['fine_idle'], w):6.1f}   {int(p['idle']['fine_n']):d} intervals; host in launch APIs during them {s_(p['idle']['launch_api_overlap_fine_us'])!s} s"
    )
    c = p["conservation"]
    L.append(
        f"  conservation: sum {s_(c['sum_us'])} s vs wall {s_(c['wall_us'])} s, residual {c['residual_us'] / 1000.0:.3f} ms ({c['residual_pct']:.4f}%) {('OK' if c['ok'] else 'VIOLATED')}"
    )
    L.append(
        f"  GPU busy {pct(p['gpu_busy_us'], w):.1f}% | launch-bound signal: GPU idle while host in launch APIs {s_(p['idle']['launch_api_overlap_idle_us'])} s"
    )
    lg = summary.largest(r)
    L.append(
        f"""  largest bucket: {lg["name"]} {lg["pct"]:.1f}% of step{(f" [{lg['note']}]" if lg["note"] else "")} (next: {lg["next_name"]} {lg["next_pct"]:.1f}%)"""
    )
    L.append("")
    L += share_table([r])
    x = p.get("p2p") or {}
    if x.get("kernels"):
        L.append("")
        L.append(
            f"PP p2p: {int(x['kernels']):d} kernels, {x['kernel_us'] / 1000000.0:.2f} s kernel time (exposed {p['comm']['PP']['exposed_us'] / 1000000.0:.2f} s); longest {x.get('max_kernel_us', 0) / 1000000.0:.2f} s, median {x.get('median_kernel_us', 0) / 1000.0:.1f} ms"
        )
        L.append(f"  {x['note']}")
        L.append(
            f"  bytes known for {x.get('bytes_known_kernel_us', 0) / 1000000.0:.2f} s of kernel time ({x.get('bytes', 0) / 1000000000.0:.2f} GB): est. transfer {x.get('transfer_est_us', 0) / 1000000.0:.2f} s, wait {x.get('wait_est_us', 0) / 1000000.0:.2f} s; bytes unknown for {x.get('bytes_unknown_kernel_us', 0) / 1000000.0:.2f} s (transfer/wait split unknown there)"
        )
        prk = r["coords"].get("pp_ranks") or []
        for bp in (x.get("by_peer") or [])[:4]:
            who = (
                (f"rank {bp['peer']!s} (pp{int(prk.index(bp['peer'])):d})")
                if bp["peer"] in prk
                else f"rank {bp['peer']}"
            )
            L.append(
                f"  {bp['role']!s:<9} {who!s:<18} {int(bp['n']):4d} kernels {bp['kernel_us'] / 1000000.0:8.2f} s kernel, est. wait {bp['wait_est_us'] / 1000000.0:8.2f} s"
            )
    o = p.get("optimizer") or {}
    if o:
        L.append("")
        L += (
            summary.optimizer_lines([r])
            if o.get("cpu_update_frames_present")
            else [
                f"optimizer: no CPU-offload frames; phase {o.get('phase_wall_us', 0) / 1000000.0:.2f} s, GPU optimizer kernels {o.get('gpu_optimizer_kernel_us', 0) / 1000000.0:.2f} s, GPU-idle host optimizer frames {o.get('host_optimizer_us', 0) / 1000000.0:.2f} s"
            ]
        )
    L.append("")
    L.append(phases_text(r, header=False))
    k = p["kernels"]
    if k.get("count"):
        L.append("")
        L.append(
            f"Kernels: {int(k['count']):d}, median {k['median_us']:.1f} us, {k['small_lt10us_count_pct']:.1f}% under 10 us ({k['small_lt10us_time_pct']:.1f}% of kernel time)"
        )
        for t in k["top"][:top_n]:
            L.append(
                f"  {t['us'] / 1000.0:8.1f} ms  n={int(t['count']):<6d} {t['class']!s:<16} {trunc(t['kernel'], 80)!s}"
            )
        if k.get("tflops"):
            for cn, v in k["tflops"].items():
                L.append(
                    f"""  achieved {cn!s}: {v["tflops"]:.0f} TFLOP/s ({(f"{v['vs_dense_bf16_peak'] * 100:.0f}%" if v["vs_dense_bf16_peak"] else "?")!s} of dense BF16 peak) over {int(v["kernels_with_flops"]):d}/{int(v["of_class_kernels"]):d} kernels with FLOPs"""
                )
        else:
            L.append(
                "  achieved TFLOP/s: unknown (no FLOPs recorded for GEMM/attention kernels)"
            )
    L.append("")
    L.append(memory_text(r, None, header=False))
    return "\n".join(L)


def _coords_str(c):
    return " ".join(
        f"{k}{c[k]}/{c.get(k + '_size')}"
        for k in ("pp", "tp", "cp", "dp", "ep", "etp")
        if c.get(k) is not None
    )


def phases_text(r, header=True):
    p = r["primary"]
    L = []
    if header:
        L.append(f"RANK {r['coords'].get('rank')} phases ({p['window']['step']})")
    L.append(
        f"Phases (host-timeline windows; method: {'; '.join(p['phase_method']) or 'none found'!s}):"
    )
    L.append(
        f"  {'phase'!s:<10} {'wall s'!s:>8} {'compute'!s:>8} {'comm-exp'!s:>9} {'memcpy-x'!s:>9} {'host'!s:>8} {'unattr'!s:>8} {'fine'!s:>7}  top host class"
    )
    for ph in taxonomy.PHASES:
        v = p["phases"].get(ph)
        if not v:
            continue
        host = sum(v["host"].values())
        top = max(v["host"].items(), key=lambda kv: kv[1]) if v["host"] else None
        L.append(
            f"  {ph!s:<10} {v['wall_us'] / 1000000.0:8.2f} {v['compute'] / 1000000.0:8.2f} {v['comm_exposed'] / 1000000.0:9.2f} {v['memcpy_exposed'] / 1000000.0:9.2f} {host / 1000000.0:8.2f} {v['unattributed_idle'] / 1000000.0:8.2f} {v['fine_idle'] / 1000000.0:7.2f}  {(f'{SHORT.get(top[0], top[0])} {top[1] / 1000000.0:.2f} s' if top and top[1] > 0 else '-')!s}"
        )
    if p.get("microbatches"):
        L.append(f"  microbatches (forward_step frames): {int(p['microbatches']):d}")
    return "\n".join(L)


def memory_text(r, tl=None, header=True):
    m = r["primary"]["memory"]
    L = []
    if header:
        L.append(
            f"RANK {r['coords'].get('rank')} memory ({r['primary']['window']['step']})"
        )
    if m.get("has_memory_events") and m.get("peak_allocated_gib") is not None:
        L.append(
            f"Memory: peak allocated {m['peak_allocated_gib']:.2f} GiB at +{m['peak_allocated_t_ms']:.0f} ms ({m['peak_allocated_phase']}); peak reserved {m['peak_reserved_gib']:.2f} GiB at +{m['peak_reserved_t_ms']:.0f} ms ({m['peak_reserved_phase']}); device {m['device_total_gib'] or 0:.1f} GiB"
        )
        if m.get("allocator_unreserved_gib") is not None:
            L.append(
                f"  {memory.UNRESERVED_LABEL}: {m['allocator_unreserved_gib']:.2f} GiB"
            )
    else:
        L.append(
            "Memory: no [memory] events in this trace (profile_memory=True / SLIME_PROFILE_MEMORY=1)"
        )
    L.append(
        f"""  churn: empty_cache calls {int(m["empty_cache_calls"]):d} ({m["empty_cache_ms"]:.0f} ms); allocations >= 5 ms {int(m["blocking_alloc_ge5ms_n"]):d} ({m["blocking_alloc_ge5ms_ms"]:.0f} ms); allocator API: {", ".join((f"{k!s} n={int(v['count']):d}" for k, v in list(m["allocator_api"].items())[:4])) or "none recorded"!s}"""
    )
    mm = r["primary"].get("memory_mgmt")
    if mm:
        L.append(
            f"""  memory management (host-side cleanup, whether or not the GPU idles): {mm["host_s"]:.2f} s = {mm["pct_of_step"]:.1f}% of step, GPU idle {mm["gpu_idle_s"]:.2f} s, {int(mm["calls"]):d} calls; {", ".join((f"{k!s} {v['s']:.2f} s x{int(v['calls']):d}" for k, v in mm["by_kind"].items())) or "none"!s}; longest {", ".join(f"{x:.2f}" for x in mm["longest_calls_s"][:3]) or "-"!s} s; called from: {", ".join(f"{trunc(c['frame'], 70)!s} x{int(c['calls']):d}" for c in mm["callers"]) or "-"!s}"""
        )
    if tl:
        L.append("  timeline (max per bin, GiB):  t(ms)   alloc  reserved")
        for x in tl:
            if x["max_alloc_gib"] is None:
                continue
            L.append(
                f"                              {x['t_ms']:7.0f}  {x['max_alloc_gib']:6.2f}  {x['max_reserved_gib']:6.2f}{('' if x['samples'] else '  (carried)')}"
            )
    return "\n".join(L)


def gaps_text(r, top=20):
    p = r["primary"]
    L = [
        f"RANK {r['coords'].get('rank')} largest GPU-idle intervals (>= 1 ms) in {p['window']['step']}; t = ms from step start"
    ]
    L.append(
        f"  {'t ms'!s:>9} {'dur ms'!s:>9} {'class'!s:<15} {'attr%'!s:>6}  deciding frame | innermost frame | outer->inner chain"
    )
    for g in p["gaps_top"][:top]:
        chain = " > ".join(trunc(x, 40) for x in reversed(g.get("chain", [])[:5]))
        L.append(
            f"  {g['t_ms']:9.1f} {g['dur_ms']:9.2f} {SHORT.get(g.get('class'), g.get('class', '?'))!s:<15} {g.get('attributed_pct', 0):6.0f}  {trunc(g.get('decided_by', '-'), 50)!s} | {trunc(g.get('innermost', '-'), 50)!s} | {chain!s}"
        )
    L.append(
        f"  coarse idle: {int(p['idle']['coarse_n']):d} intervals, {p['idle']['coarse_us'] / 1000000.0:.2f} s; fine idle: {int(p['idle']['fine_n']):d} intervals, {p['idle']['fine_us'] / 1000000.0:.2f} s"
    )
    return "\n".join(L)


def comm_text(run, dim=None):
    L = [
        f"{'rank'!s:<6} {'pp'!s:<5} {'dim'!s:<6} {'collective'!s:<15} {'count'!s:>7} {'GB'!s:>9} {'kern s'!s:>9} {'busbw GB/s'!s:>10} {'placement'!s:<11} {'vs nom'!s:>6}  {'groups'!s}"
    ]
    for r in ok_ranks(run):
        p = r["primary"]
        for d in taxonomy.COMM_DIMS:
            if dim and d.upper() != dim.upper():
                continue
            for ct, v in sorted(
                (p["comm_bw"].get(d) or {}).items(), key=lambda kv: -kv[1]["time_us"]
            ):
                bandwidth_text = f"{v['busbw_gbps']:.0f}" if v["busbw_gbps"] else "n/a"
                nominal_ratio_text = (
                    f"{v['vs_nominal']:.2f}" if v["vs_nominal"] else "n/a"
                )
                L.append(
                    f"{r['coords'].get('rank')!s:<6} {_pp(r)!s:<5} {d!s:<6} {ct!s:<15} {int(v['count']):7d} {v['bytes'] / 1000000000.0:9.2f} {v['time_us'] / 1000000.0:9.2f} {(bandwidth_text)!s:>10} {v['placement']!s:<11} {(nominal_ratio_text)!s:>6}  n={v['group_sizes']!s} {','.join(v['pg_descs'])[:60]!s}{(' inferred:' + ','.join(v['inferred']) if v['inferred'] else '')!s}"
                )
    L.append("")
    L.append("exposure per rank and dim (s): union / exposed / overlapped")
    for r in ok_ranks(run):
        p = r["primary"]
        parts = []
        for d in taxonomy.COMM_DIMS:
            if dim and d.upper() != dim.upper():
                continue
            c = p["comm"][d]
            if c["count"]:
                parts.append(
                    f"{d} {c['union_us'] / 1000000.0:.2f}/{c['exposed_us'] / 1000000.0:.2f}/{c['overlapped_us'] / 1000000.0:.2f}"
                )
        L.append(f"  rank {r['coords'].get('rank')!s:<5} {' | '.join(parts)!s}")
    return "\n".join(L)


def kernels_text(run, cls=None, rank=None, top_n=20):
    L = []
    for r in ok_ranks(run):
        if rank is not None and r["coords"].get("rank") != rank:
            continue
        k = r["primary"]["kernels"]
        if not k.get("count"):
            continue
        L.append(
            f"rank {r['coords'].get('rank')!s}: {int(k['count']):d} kernels, median {k['median_us']:.1f} us, {k['small_lt10us_count_pct']:.1f}% under 10 us"
        )
        L.append(
            f"  {'class'!s:<16} {'count'!s:>7} {'sum s'!s:>9} {'union s'!s:>9} {'median us'!s:>9} {'<10us %'!s:>8}"
        )
        for c, v in sorted(k["by_class"].items(), key=lambda kv: -kv[1]["sum_us"]):
            if cls and c != cls:
                continue
            un = r["primary"]["compute"].get(
                c, r["primary"]["comm"].get(c, r["primary"]["memcpy"].get(c, {}))
            )
            L.append(
                f"  {c!s:<16} {int(v['count']):7d} {v['sum_us'] / 1000000.0:9.2f} {un.get('union_us', 0) / 1000000.0:9.2f} {v['median_us']:9.1f} {v['small_lt10us_count_pct']:8.1f}"
            )
        n = 0
        for t in k["top"]:
            if cls and t["class"] != cls:
                continue
            L.append(
                f"    {t['us'] / 1000.0:8.1f} ms n={int(t['count']):<6d} {t['class']!s:<16} {trunc(t['kernel'], 90)!s}"
            )
            n += 1
            if n >= top_n:
                break
    return "\n".join(L) if L else "no kernels matched"


def _bucket_rows(p):
    b = p["buckets_us"]
    rows = [("compute", b["compute"])]
    for d in taxonomy.COMM_DIMS:
        rows.append(("comm-exposed " + d, p["comm"][d]["exclusive_us"]))
    for d in taxonomy.MEMCPY_DIRS:
        rows.append(("memcpy-exposed " + d, p["memcpy"][d]["exclusive_us"]))
    for c in taxonomy.HOST_CLASSES:
        rows.append(("host " + SHORT[c], b["host"].get(c, 0.0)))
    rows.append(("unattributed idle", b["unattributed_idle"]))
    rows.append(("fine idle", b["fine_idle"]))
    return rows


def diff_text(runA, runB):
    A = {pipeline.role_key(r["coords"]): r for r in ok_ranks(runA)}
    B = {pipeline.role_key(r["coords"]): r for r in ok_ranks(runB)}
    L = [f"DIFF  A={runA['dir']}\n      B={runB['dir']}"]
    keys = [k for k in A if k in B]
    how = "role (pp, tp, cp, ep, dp)"
    if not keys:
        A = {r["coords"].get("rank"): r for r in ok_ranks(runA)}
        B = {r["coords"].get("rank"): r for r in ok_ranks(runB)}
        keys = [k for k in A if k in B]
        how = "global rank (roles differ between runs)"
    L.append(
        f"matched {int(len(keys)):d} rank(s) by {how!s}; unmatched A={int(len(A) - len(keys)):d} B={int(len(B) - len(keys)):d}"
    )
    keys.sort(
        key=lambda k: (
            A[k]["coords"].get("pp") is None,
            A[k]["coords"].get("pp") or 0,
            A[k]["coords"].get("rank") or 0,
        )
    )
    for k in keys:
        a, b = A[k], B[k]
        pa, pb = a["primary"], b["primary"]
        wa, wb = pa["window"]["wall_us"], pb["window"]["wall_us"]
        L.append("")
        L.append(
            f"{(_pp(a) if _pp(a) != '-' else 'role')}: A rank {a['coords'].get('rank')} -> B rank {b['coords'].get('rank')} | wall {wa / 1000000.0:.2f} -> {wb / 1000000.0:.2f} s ({(wb - wa) / 1000000.0:+.2f} s) | busy {pct(pa['gpu_busy_us'], wa):.1f}% -> {pct(pb['gpu_busy_us'], wb):.1f}%"
        )
        ra, rb = _bucket_rows(pa), _bucket_rows(pb)
        for (name, va), (_, vb) in zip(ra, rb, strict=False):
            if max(va, vb) < 0.01 * max(wa, wb):
                continue
            L.append(
                f"   {name!s:<24} {va / 1000000.0:8.2f} -> {vb / 1000000.0:8.2f} s  ({(vb - va) / 1000000.0:+8.2f})   {pct(va, wa):5.1f}% -> {pct(vb, wb):5.1f}% of wall"
            )
    pa_, pb_ = runA.get("pipeline", {}), runB.get("pipeline", {})
    if pa_.get("stages") and pb_.get("stages"):
        L.append("")
        L.append(
            f"pipeline: critical stage A pp{pa_.get('critical_pp')} -> B pp{pb_.get('critical_pp')}"
        )
    return "\n".join(L)


def stack_text(r, rank_obj, t0_ms, t1_ms, max_lines=80):
    """Host frames on kernel-launching threads around [t0, t1] (ms from step start).

    Frames enclosing the whole window are collapsed into one context line; the rest are depth-indented."""
    p = r["primary"]
    base = p["window"]["t0"]
    t0, t1 = base + t0_ms * 1e3, base + t1_ms * 1e3
    a = rank_obj.a

    def nm(i):
        return rank_obj.hnames[int(a["h_name"][i])]

    L = [
        f"RANK {r['coords'].get('rank')} host frames overlapping +{t0_ms:.1f}..+{t1_ms:.1f} ms ({p['window']['step']}); columns: start ms, dur ms, frame"
    ]
    for tid in rank_obj.driver_tids:
        idx = rank_obj.thread_frames(tid)
        s = rank_obj.h_start[idx]
        e = rank_obj.h_end[idx]
        sel = idx[(s < t1) & (e > t0)]
        enc = [
            i
            for i in sel.tolist()
            if rank_obj.h_start[i] <= t0 and rank_obj.h_end[i] >= t1
        ]
        inner = [
            i
            for i in sel.tolist()
            if not (rank_obj.h_start[i] <= t0 and rank_obj.h_end[i] >= t1)
        ]
        L.append(
            f"thread {tid!s} ({r.get('thread_names', {}).get(str(tid), '?')!s}): {int(len(enc)):d} enclosing frames, {int(len(inner)):d} inside/partial"
        )
        if enc:
            L.append(
                "  enclosing (outer->inner, last 8): "
                + " > ".join(trunc(nm(i), 60) for i in enc[-8:])
            )
        stack = []
        n = 0
        for i in inner:
            while stack and rank_obj.h_end[stack[-1]] <= rank_obj.h_start[i]:
                stack.pop()
            depth = len(stack)
            stack.append(i)
            if n < max_lines:
                L.append(
                    f"  {(rank_obj.h_start[i] - base) / 1000.0:+10.2f} {a['h_dur'][i] / 1000.0:9.2f} {'  ' * min(depth, 12)}{trunc(nm(i), 110)}"
                )
            n += 1
        if n > max_lines:
            L.append(f"  ... {int(n - max_lines):d} more frames (narrow the window)")
    g = rank_obj.g_sel
    m = (rank_obj.g_start[g] < t1) & (rank_obj.g_end[g] > t0)
    L.append(f"GPU activities overlapping the window: {int(int(m.sum())):d}")
    return "\n".join(L)
