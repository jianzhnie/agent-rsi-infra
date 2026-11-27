# RSIBench-Infra paper implementation

Implementation entrypoint: [RSI experiment controller](rsi-experiment-controller.md).

Paper: [RSIBench-Infra, arXiv:2611.24395](https://arxiv.org/abs/2611.24395). The paper's core transferable system design is a fixed runnable baseline and workload contract, candidate changes captured reproducibly, independent quality validation, and end-to-end scoring isolated from candidate modifications. The implementation here is intentionally a lightweight evidence ledger; it does not claim to reproduce the 20 benchmark tasks, OCI deployment machinery, multi-node jobs, or the paper's measured results.

Run tests with: `python -m pytest tests/test_rsi_experiment.py -q`.
