#!/usr/bin/env python3
"""Synthetic smoke test for the public-safe analysis code.

No study data are embedded here. The fixture is generated deterministically only to
check that grouped fitting, nested selection, triage, and resource accounting execute.
"""
from pathlib import Path
import sys
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from analyse_public import Experiment, METALS, summarize_batches, resource_frontier


def make_rows():
    rows = []
    for i in range(1, 31):
        block = (i - 1) // 5 + 1
        fine = 20.0 + 1.8 * i
        coarse = 25.0 + 1.3 * i + 0.4 * block
        ffd = 0.5 + 0.07 * (i % 7)
        cfd = 0.7 + 0.05 * (i % 5)
        row = {
            "Sample": str(i),
            "Block": str(block),
            "Fine_LF": str(fine),
            "Coarse_LF": str(coarse),
            "Fine_FD_pct": str(ffd),
            "Coarse_FD_pct": str(cfd),
        }
        for j, metal in enumerate(METALS):
            # Positive deterministic pseudo-chemistry; coefficients differ by metal.
            value = 10.0 + (j + 1) * 0.8 * fine + (9 - j) * 0.3 * coarse + 0.2 * block
            row[f"{metal}_mgkg"] = str(value)
        rows.append(row)
    return rows


def main():
    exp = Experiment(make_rows())
    pred = exp.blocked_cv()
    assert exp.n == 30
    assert len(np.unique(exp.blocks)) == 6
    assert all(np.isfinite(v).all() for v in pred.values())

    metrics = exp.metrics(pred)
    assert len(metrics) == len(pred) * len(METALS)

    gains = exp.gain_summary(pred)
    assert len(gains) == len(METALS)
    assert all(float(r["Conditional_low"]) <= float(r["Conditional_high"]) for r in gains)

    curves = exp.triage(pred, high_n=7)
    for metal in METALS:
        for model in pred:
            seq = [r for r in curves if r["Metal"] == metal and r["Model"] == model]
            hits = [int(r["Hits"]) for r in seq]
            assert all(a <= b for a, b in zip(hits, hits[1:]))
            assert hits[-1] == 7

    batches = exp.heldout_pair_batches()
    summary = summarize_batches(batches)
    assert summary and all(0.0 <= float(r["Mean_recall"]) <= 1.0 for r in summary)

    frontier = resource_frontier(curves)
    assert frontier
    print("PASS: synthetic public smoke test; no study data used.")


if __name__ == "__main__":
    main()
