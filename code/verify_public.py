#!/usr/bin/env python3
"""Checks aggregate public outputs without exposing source rows."""
from pathlib import Path
import csv
import math

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def read(name):
    with (RESULTS / name).open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    performance = read("Performance.csv")
    gains = read("Gains.csv")
    frontier = read("Resource_frontier.csv")
    batches = read("Batch_summary.csv")

    assert performance and gains and frontier and batches
    assert all(math.isfinite(float(r["R2"])) for r in performance)
    assert all(float(r["Conditional_low"]) <= float(r["Gain"]) <= float(r["Conditional_high"]) for r in gains)
    assert all(abs(43 * float(r["Max_extra_cost_per_sample_in_assay_units"]) - int(r["Assays_avoided"])) < 1e-12 for r in frontier)
    assert all(0 <= float(r["Mean_recall"]) <= 1 for r in batches)
    print("PASS: aggregate public outputs satisfy structural and arithmetic checks.")


if __name__ == "__main__":
    main()
