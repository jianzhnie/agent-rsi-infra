# Paper-inspired RSI experiment controller

This is a small adaptation of [RSIBench-Infra](https://arxiv.org/abs/2611.24395), not a reproduction of its 20 production tasks or reported results. The paper begins with runnable baselines, permits cross-stack changes, captures submissions reproducibly, and scores end-to-end performance only after independent task-specific quality checks. This repository implements an evidence/control-plane primitive, not the paper's expensive workload suite.

## Workflow

1. Freeze task, baseline revision, quality contract, workload, environment, and measurement boundary.
2. Run an authorized agent/toolchain in a disposable workspace outside this ledger.
3. Independently execute correctness/quality verification and end-to-end benchmark; preserve raw outputs.
4. Record candidate revision, verifier verdict, repeated latency samples, command, and artifact locator.
5. Review the report. Only quality-passed trials may produce validated speedup. Default eligibility threshold is 1.10x; promotion is always human-only.

The script never launches commands, modifies candidate source, validates artifact contents, or auto-promotes. SHA-256 fingerprints supplied trial metadata; it is not a provenance attestation.

## CLI

Task JSON requires non-empty task_id, objective, baseline_revision, quality_contract, workload, and environment:

~~~bash
python scripts/rsi_experiment.py init experiments/run.json task.json
python scripts/rsi_experiment.py record experiments/run.json trial.json
python scripts/rsi_experiment.py report experiments/run.json --output experiments/report.json
~~~

Trial JSON requires trial_id, candidate_revision, quality_gate (passed / failed / not_run), quality_evidence, command, artifact, and at least two positive end-to-end latency_samples. Quality-passed trials also require baseline_median_latency. Record sample units and measurement boundaries in the task contract/evidence.

Keep evidence and artifacts immutable/versioned. A future production executor should bind an OCI layer digest, apply the same candidate digest to each worker/rank, and run the benchmark in a separate environment that cannot see candidate-side benchmark modifications. This isolation is documented, not implemented by this ledger.

| Paper principle | This repository |
|---|---|
| Runnable fixed baseline | task contract pins baseline revision |
| Cross-stack candidate | candidate revision + artifact locator |
| Reproducible submission | evidence metadata fingerprint; external digest recommended |
| Independent quality gate | quality verdict required before scoring |
| End-to-end evaluation | repeated latency samples, contract owns boundary |
| Thresholded validated gain | 1.10x default eligibility |
| Human review | no automatic promotion |
