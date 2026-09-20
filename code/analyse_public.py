#!/usr/bin/env python3
"""Public-safe implementation of the central V4 screening analysis.

The controlled source workbook is not distributed in this repository. This script
expects a publication-safe input CSV described in `data/README.md` and writes
aggregate outputs only: no selected sample IDs, row-level predictions, or source
trace tables are emitted.
"""
from __future__ import annotations
from pathlib import Path
import csv
import itertools
import math
import numpy as np
from scipy.stats import spearmanr, hypergeom

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "analysis_input.csv"
OUT = ROOT / "results"
METALS = ["Fe", "Zn", "Cu", "Cr", "Co", "Ni", "Mn", "Pb", "Cd"]
SEED = 20260920


def read_rows(path: Path):
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def stable_order(scores, ids):
    """Descending score with deterministic sample-ID tie breaking."""
    return np.lexsort((ids, -scores))


class Experiment:
    def __init__(self, rows):
        self.rows = rows
        self.n = len(rows)
        self.ids = np.array([int(r["Sample"]) for r in rows])
        self.blocks = np.array([int(r["Block"]) for r in rows])
        self.y = np.log10(np.array([[float(r[f"{m}_mgkg"]) for m in METALS] for r in rows]))

        f = np.log10(np.array([float(r["Fine_LF"]) for r in rows]))
        c = np.log10(np.array([float(r["Coarse_LF"]) for r in rows]))
        ffd = np.array([float(r["Fine_FD_pct"]) for r in rows])
        cfd = np.array([float(r["Coarse_FD_pct"]) for r in rows])

        self.x = {
            "F": f[:, None],
            "C": c[:, None],
            "Ffreq": np.c_[f, ffd],
            "Cfreq": np.c_[c, cfd],
            "FC": np.c_[f, c],
        }
        self.cache = {}

    def fit_predict(self, name, train, test):
        key = (name, tuple(train), tuple(test))
        if key in self.cache:
            return self.cache[key]
        x = self.x[name]
        mu = x[train].mean(0)
        sd = x[train].std(0)
        sd[sd < 1e-12] = 1.0
        a = np.c_[np.ones(len(train)), (x[train] - mu) / sd]
        b = np.c_[np.ones(len(test)), (x[test] - mu) / sd]
        pred = b @ np.linalg.lstsq(a, self.y[train], rcond=None)[0]
        self.cache[key] = pred
        return pred

    def select_single(self, train, family=("F", "C", "Ffreq", "Cfreq")):
        """Select one single-fraction configuration per metal using inner grouped MAE."""
        errors = []
        for name in family:
            e = np.zeros((len(train), len(METALS)))
            for block in np.unique(self.blocks[train]):
                inner_test = train[self.blocks[train] == block]
                inner_train = train[self.blocks[train] != block]
                loc = np.flatnonzero(self.blocks[train] == block)
                e[loc] = np.abs(self.y[inner_test] - self.fit_predict(name, inner_train, inner_test))
            block_score = np.mean([
                e[self.blocks[train] == block].mean(0)
                for block in np.unique(self.blocks[train])
            ], axis=0)
            errors.append(block_score)
        a = np.array(errors)
        pick = np.argmax(a <= a.min(0)[None, :] + 1e-12, axis=0)
        return [family[k] for k in pick]

    def blocked_cv(self):
        pred = {name: np.full(self.y.shape, np.nan) for name in self.x}
        pred["Single4_G"] = np.full(self.y.shape, np.nan)
        for block in np.unique(self.blocks):
            test = np.flatnonzero(self.blocks == block)
            train = np.flatnonzero(self.blocks != block)
            for name in self.x:
                pred[name][test] = self.fit_predict(name, train, test)
            chosen = self.select_single(train)
            pred["Single4_G"][test] = np.column_stack([
                pred[name][test, j] for j, name in enumerate(chosen)
            ])
        return pred

    def metrics(self, pred):
        rows = []
        for model, p in pred.items():
            for j, metal in enumerate(METALS):
                y = self.y[:, j]
                ph = p[:, j]
                err = np.abs(y - ph)
                ss = np.sum((y - ph) ** 2)
                st = np.sum((y - y.mean()) ** 2)
                rows.append({
                    "Metal": metal,
                    "Model": model,
                    "N": self.n,
                    "Blocks": len(np.unique(self.blocks)),
                    "R2": 1 - ss / st,
                    "Spearman": float(spearmanr(y, ph).statistic),
                    "MAE_sample": float(err.mean()),
                    "MAE_block": float(np.mean([
                        err[self.blocks == b].mean() for b in np.unique(self.blocks)
                    ])),
                })
        return rows

    def gain_summary(self, pred, candidate="FC", reference="Single4_G"):
        rng = np.random.default_rng(SEED)
        blocks = np.unique(self.blocks)
        d = np.array([
            np.abs(self.y[self.blocks == b] - pred[reference][self.blocks == b]).mean(0)
            - np.abs(self.y[self.blocks == b] - pred[candidate][self.blocks == b]).mean(0)
            for b in blocks
        ])
        draw = rng.integers(0, len(blocks), size=(30000, len(blocks)))
        boot = d[draw].mean(1)
        lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)
        return [{
            "Metal": m,
            "Candidate": candidate,
            "Reference": reference,
            "Gain": float(d[:, j].mean()),
            "Conditional_low": float(lo[j]),
            "Conditional_high": float(hi[j]),
            "Positive_blocks": int(np.sum(d[:, j] > 0)),
        } for j, m in enumerate(METALS)]

    def triage(self, pred, high_n=11):
        rows = []
        for model, score in pred.items():
            for j, metal in enumerate(METALS):
                high = set(stable_order(self.y[:, j], self.ids)[:high_n])
                order = stable_order(score[:, j], self.ids)
                for k in range(1, self.n + 1):
                    selected = set(order[:k])
                    hit = len(high & selected)
                    rows.append({
                        "Metal": metal,
                        "Model": model,
                        "High_n": high_n,
                        "k": k,
                        "Hits": hit,
                        "Recall": hit / high_n,
                        "Precision": hit / k,
                        "Lift": (hit / high_n) / (k / self.n),
                        "Random_hits": k * high_n / self.n,
                        "Random_upper_tail": float(hypergeom.sf(hit - 1, self.n, high_n, k)),
                    })
        return rows

    def heldout_pair_batches(self):
        """Same-model audit: each pair of blocks is scored by one model fit without either block."""
        rows = []
        for g, h in itertools.combinations(np.unique(self.blocks), 2):
            test = np.flatnonzero((self.blocks == g) | (self.blocks == h))
            train = np.flatnonzero((self.blocks != g) & (self.blocks != h))
            k = math.ceil(len(test) / 4)
            for model in ("Ffreq", "Cfreq", "FC"):
                p = self.fit_predict(model, train, test)
                for j, metal in enumerate(METALS):
                    high = set(stable_order(self.y[test, j], self.ids[test])[:k])
                    order = stable_order(p[:, j], self.ids[test])
                    hit = len(high & set(order[:k]))
                    rows.append({
                        "Metal": metal,
                        "Model": model,
                        "Test_n": len(test),
                        "k": k,
                        "Recall": hit / k,
                        "MAE": float(np.abs(self.y[test, j] - p[:, j]).mean()),
                    })
        return rows


def summarize_batches(rows):
    out = []
    for metal in METALS:
        for model in ("Ffreq", "Cfreq", "FC"):
            x = [r for r in rows if r["Metal"] == metal and r["Model"] == model]
            recall = np.array([r["Recall"] for r in x])
            mae = np.array([r["MAE"] for r in x])
            out.append({
                "Metal": metal,
                "Model": model,
                "Batches": len(x),
                "Mean_recall": float(recall.mean()),
                "Median_recall": float(np.median(recall)),
                "Recall_q25": float(np.quantile(recall, 0.25)),
                "Recall_q75": float(np.quantile(recall, 0.75)),
                "Mean_MAE": float(mae.mean()),
            })
    return out


def resource_frontier(curves):
    out = []
    for metal in METALS:
        for target in (0.5, 0.8, 1.0):
            k = {}
            for model in ("Ffreq", "Cfreq", "FC", "Single4_G"):
                eligible = [r for r in curves if r["Metal"] == metal and r["Model"] == model and r["Recall"] >= target]
                k[model] = min(int(r["k"]) for r in eligible)
            for reference in ("Ffreq", "Cfreq", "Single4_G"):
                delta = k[reference] - k["FC"]
                out.append({
                    "Metal": metal,
                    "Recovery_target": target,
                    "Reference": reference,
                    "k_reference": k[reference],
                    "k_FC": k["FC"],
                    "Assays_avoided": delta,
                    "Max_extra_cost_per_sample_in_assay_units": delta / 43,
                })
    return out


def main():
    if not DATA.exists():
        raise SystemExit("Missing data/analysis_input.csv. See data/README.md; source data are not public.")
    source = read_rows(DATA)
    paired = [r for r in source if r.get("Coarse_LF", "") not in ("", None)]
    exp = Experiment(paired)
    pred = exp.blocked_cv()
    performance = exp.metrics(pred)
    gains = exp.gain_summary(pred)
    curves = exp.triage(pred)
    batches = exp.heldout_pair_batches()

    write_rows(OUT / "Performance.csv", performance)
    write_rows(OUT / "Gains.csv", gains)
    write_rows(OUT / "Triage_curves.csv", curves)
    write_rows(OUT / "Batch_summary.csv", summarize_batches(batches))
    write_rows(OUT / "Resource_frontier.csv", resource_frontier(curves))
    print(f"PASS: {exp.n} paired rows; {len(np.unique(exp.blocks))} blocked groups; aggregate outputs written.")


if __name__ == "__main__":
    main()
