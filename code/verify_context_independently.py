"""New verification code written 2026-09-26; not the recovered historical generator.

Reconstruct the already-reported context baselines from the verified master.
Do not modify author source, tables or publication results.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
parser.add_argument("--source", type=Path, help="Override the source master CSV")
parser.add_argument("--reference", type=Path, help="Override the public Mn context reference CSV")
parser.add_argument("--primary-reference", type=Path, help="Override the printed primary-metric fixture CSV")
parser.add_argument("--output", type=Path, help="Output directory; defaults to results/context_reproduction")
args = parser.parse_args()
ROOT = args.repo_root.resolve()
SOURCE = (args.source or ROOT / "endpoint_extension/Source_Reconstructed_Master_44.csv").resolve()
REFERENCE = (args.reference or ROOT / "results/v6_mn_context_safeguard.csv").resolve()
PRIMARY_REFERENCE = (args.primary_reference or ROOT / "tests/fixtures/context_primary_expected.csv").resolve()
OUTPUT = (args.output or ROOT / "results/context_reproduction").resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)

def display_path(path):
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.name

METALS = ["Fe", "Zn", "Cu", "Cr", "Co", "Ni", "Mn", "Pb", "Cd"]
rows = list(csv.DictReader(SOURCE.open(encoding="utf-8-sig", newline="")))
paired = sorted((r for r in rows if r["Coarse_LF_reconstructed"].strip()), key=lambda r: int(r["Sample"]))
ids = np.array([int(r["Sample"]) for r in paired])
assert len(rows) == 44 and len(ids) == 43 and 24 not in ids
numeric = np.array([int(re.search(r"(\d+)$", r["SiteCode"]).group(1)) for r in paired])
sites = np.array([r["SiteCode"] for r in paired])
distance_m = np.array([float(r["Distance_numeric_m"]) for r in paired])
right = np.array([float(r["Side"] == "R") for r in paired])
f = np.log10([float(r["Fine_LF_reconstructed"]) for r in paired])
c = np.log10([float(r["Coarse_LF_reconstructed"]) for r in paired])
Y = np.log10([[float(r[f"{m}_mgkg"]) for m in METALS] for r in paired])
groups = {
    "Ten_code_blocks": numeric,
    "Nineteen_side_codes": sites,
    # Explicit new verification interpretation; no historical mapping code was recovered.
    "Five_merged_blocks": (numeric - 1) // 2 + 1,
}
assert [len(np.unique(g)) for g in groups.values()] == [10, 19, 5]


def run(transform_name, intercept=True):
    distance_feature = {
        "log10_1plus_metres": np.log10(1 + distance_m),
        "ln_1plus_metres": np.log1p(distance_m),
        "log10_1plus_kilometres": np.log10(1 + distance_m / 1000),
        "log10_metres": np.log10(distance_m),
        "untransformed_metres": distance_m,
    }[transform_name]
    X = {
        "Context": np.column_stack((distance_feature, right)),
        "ContextF": np.column_stack((distance_feature, right, f)),
        "ContextFC": np.column_stack((distance_feature, right, f, c)),
    }
    result = []
    predictions = []
    for grouping, block in groups.items():
        for model, features in X.items():
            predicted = np.full_like(Y, np.nan)
            train_mean = np.full_like(Y, np.nan)
            for fold in np.unique(block):
                test = block == fold
                train = ~test
                if intercept:
                    # Solve the unscaled design directly. This does not reuse any author helper.
                    a = np.column_stack((np.ones(train.sum()), features[train]))
                    b = np.column_stack((np.ones(test.sum()), features[test]))
                else:
                    a, b = features[train], features[test]
                coefficients = np.linalg.lstsq(a, Y[train], rcond=None)[0]
                predicted[test] = b @ coefficients
                train_mean[test] = Y[train].mean(axis=0)
            assert np.isfinite(predicted).all()
            for j, metal in enumerate(METALS):
                y, p = Y[:, j], predicted[:, j]
                errors = np.abs(y - p)
                high = set(ids[np.lexsort((ids, -y))[:11]])
                chosen = set(ids[np.lexsort((ids, -p))[:11]])
                result.append({
                    "Transform": transform_name, "Intercept": intercept,
                    "Grouping": grouping, "Model": model, "Metal": metal,
                    "R2": 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum(),
                    "Q2": 1 - ((y - p) ** 2).sum() / ((y - train_mean[:, j]) ** 2).sum(),
                    "MAE_sample": errors.mean(),
                    "MAE_block": np.mean([errors[block == b].mean() for b in np.unique(block)]),
                    "Hits_h11_k11": len(high & chosen),
                })
                if transform_name == "log10_1plus_metres" and intercept:
                    predictions.extend({"Grouping": grouping, "Model": model, "Metal": metal,
                                        "Sample": int(ids[i]), "Block": str(block[i]),
                                        "Observed_log10": float(y[i]), "Predicted_log10": float(p[i])}
                                       for i in range(len(ids)))
    return result, predictions


def save_csv(name, values):
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(values[0]))
        writer.writeheader()
        writer.writerows(values)


primary, predictions = run("log10_1plus_metres")
save_csv("CONTEXT_INDEPENDENT_METRICS.csv", primary)
save_csv("CONTEXT_INDEPENDENT_PREDICTIONS.csv", predictions)
expected = list(csv.DictReader(REFERENCE.open(encoding="utf-8-sig", newline="")))
comparisons = []
diagnostics = []
for transform, intercept in [("log10_1plus_metres", True), ("ln_1plus_metres", True),
                             ("log10_1plus_kilometres", True), ("log10_metres", True),
                             ("untransformed_metres", True), ("log10_1plus_metres", False)]:
    values = primary if transform == "log10_1plus_metres" and intercept else run(transform, intercept)[0]
    lookup = {(r["Grouping"], r["Model"]): r for r in values if r["Metal"] == "Mn"}
    diffs = []
    hit_diffs = []
    for e in expected:
        a = lookup[(e["Grouping"], e["Model"])]
        for metric in ["R2", "MAE_sample", "MAE_block"]:
            diff = float(a[metric]) - float(e[metric])
            diffs.append(abs(diff))
            if transform == "log10_1plus_metres" and intercept:
                comparisons.append({"Grouping": e["Grouping"], "Model": e["Model"], "Metric": metric,
                                    "Published": float(e[metric]), "Independent": float(a[metric]),
                                    "Difference": diff, "Matches_1e-12": abs(diff) <= 1e-12})
        hit_diff = int(a["Hits_h11_k11"]) - int(e["Hits_h11_k11"])
        hit_diffs.append(hit_diff)
        if transform == "log10_1plus_metres" and intercept:
            comparisons.append({"Grouping": e["Grouping"], "Model": e["Model"], "Metric": "Hits_h11_k11",
                                "Published": int(e["Hits_h11_k11"]), "Independent": int(a["Hits_h11_k11"]),
                                "Difference": hit_diff, "Matches_1e-12": hit_diff == 0})
    diagnostics.append({"Transform": transform, "Intercept": intercept,
                        "Max_absolute_float_difference": max(diffs),
                        "All_float_values_match_1e-12": max(diffs) <= 1e-12,
                        "Hit_count_disagreements": sum(d != 0 for d in hit_diffs)})
save_csv("CONTEXT_PUBLIC_AGGREGATE_COMPARISON.csv", comparisons)
save_csv("CONTEXT_TRANSFORM_DIAGNOSTICS.csv", diagnostics)

table_comparisons = []
for row in csv.DictReader(PRIMARY_REFERENCE.open(encoding="utf-8", newline="")):
    metal, model = row["Metal"], row["Model"]
    actual = next(r for r in primary if r["Grouping"] == "Ten_code_blocks" and r["Metal"] == metal and r["Model"] == model.replace("+", ""))
    for metric in ["R2", "Q2", "MAE_sample", "MAE_block"]:
        value = float(row[metric])
        matches = f"{actual[metric]:.3f}" == f"{value:.3f}"
        table_comparisons.append({"Metal": metal, "Model": model, "Metric": metric,
                                  "Printed": value, "Independent": float(actual[metric]),
                                  "Independent_3dp": f"{actual[metric]:.3f}", "Matches_printed": matches})
save_csv("CONTEXT_MANUSCRIPT_TABLE_COMPARISON.csv", table_comparisons)

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
summary = {
    "verification_kind": "New independent reconstruction of previously reported context models; historical generator not recovered",
    "source_master": display_path(SOURCE), "source_sha256": sha(SOURCE),
    "reference_aggregate": display_path(REFERENCE), "reference_sha256": sha(REFERENCE),
    "reference_primary_fixture": display_path(PRIMARY_REFERENCE), "reference_fixture_sha256": sha(PRIMARY_REFERENCE),
    "script_sha256": sha(Path(__file__)),
    "paired_samples": len(ids), "excluded_missing_coarse": [24],
    "model": "OLS with intercept; target log10 concentration; distance feature log10(1 + distance in metres); binary recorded side; magnetic additions log10 LF",
    "fit": "Direct unscaled design solved with numpy.linalg.lstsq(rcond=None), separately in every training fold; no author fit helper imported",
    "group_counts": {k: int(len(np.unique(v))) for k, v in groups.items()},
    "five_group_map": {str(i): int((i - 1) // 2 + 1) for i in range(1, 11)},
    "five_group_map_provenance": "Explicit newly reconstructed adjacent-pair interpretation; reproduces public aggregate if checks pass; not read from recovered historical code",
    "public_numeric_comparisons": len(comparisons),
    "public_max_absolute_difference": max(abs(r["Difference"]) for r in comparisons),
    "public_all_match_1e-12": all(r["Matches_1e-12"] for r in comparisons),
    "printed_primary_context_metrics_checked": len(table_comparisons),
    "printed_all_match_3dp": all(r["Matches_printed"] for r in table_comparisons),
    "transform_diagnostics": diagnostics,
    "not_identifiable_from_aggregate_alone": ["logarithm base (natural log is a constant rescaling)", "which side is coded 0 versus 1 when an intercept is fitted", "unique historical implementation or all per-sample predictions"],
    "numpy_version": np.__version__,
    "canonical_master_sha256_matches": sha(SOURCE) == "e1804049d7e2819e8b1228eb55db81524caaa18cb6d4745000c20d3ce609d105",
    "author_sources_modified": False,
}
(OUTPUT / "CONTEXT_INDEPENDENT_QA.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))

raise SystemExit(0 if summary["public_all_match_1e-12"] and summary["printed_all_match_3dp"] and summary["canonical_master_sha256_matches"] else 1)
