# Amman–Airport magnetic screening: V11R3 reproducibility

Research data and software accompanying **When predictive fit and screening utility diverge: choosing frequency or particle size in roadside-soil magnetometry**.

This release makes the original study workbook, the supplied reconstructed analysis table, the endpoint-directed extension code and reference outputs available with explicit execution checks. The scientific results are unchanged. The study contains 44 archived soil samples, 43 complete fine/coarse magnetic pairs and nine measured metals.

Release: `v11r3-reproducibility` (2026-09-26). Archive DOI: [10.5281/zenodo.22973207](https://doi.org/10.5281/zenodo.22973207).

## Contents and checked scope

| Directory | Contents |
|---|---|
| `endpoint_extension/` | Original workbook, hash-locked master CSV, unchanged author scripts, original protocol, reference CSVs and archived presentation artifacts. |
| `data/` | Input for the earlier central public implementation, mapped directly from the master CSV. |
| `code/` | Earlier central implementation, new input-schema adapter and independent context verifier. |
| `verification/` | New independent replay and source-reconstruction utilities, distinguished from historical author code. |
| `results/` | Earlier aggregate reference tables and central-script outputs. |
| `docs/` | Data dictionary, execution reports and exact coverage limits. |

The original workbook SHA-256 is `4ff48393b15d83306e9099efa30e12ee2d797cd57a0b75c44b8f99726380becb`. Its bytes are unchanged, including additional archived laboratory sheets outside the analysis cohort. See [DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md).

The unchanged author extension passed 878 source-to-table checks. All 12 regenerated CSVs matched 21,139 numerical cells within floating-point tolerance; all 462 checked numerical entries in Main Table 4 and Supplement S14–S18 matched at displayed precision. See [REPRODUCTION_REPORT.md](docs/REPRODUCTION_REPORT.md). Selector-score ties use an absolute tolerance of `1e-12`; exact sample-ranking ties use numerical sample ID. Source distances are in metres.

## Run

Python 3.12 was used for release checks. Create and activate a virtual environment, then run from the repository root:

```bash
python -m pip install -r requirements-reproduction.txt
python verification/verify_reproduction.py endpoint_extension --report reproduction_check.json
python code/prepare_analysis_input.py
python code/analyse_public.py
python code/verify_public.py
python code/verify_context_independently.py
```

The first verifier executes the author code in a temporary directory and compares new CSVs with reference files. Running `endpoint_extension/run_all.py` directly replaces outputs beside its inputs; use a working copy if doing so. The central script writes aggregate outputs under `results/`. See [verification/README.md](verification/README.md) for the new workbook reconstruction utility. Its numerically matching output does not replace the hash-locked author master.

## Interpretation and limits

The release verifies the available workflows. The original generators for several older auxiliary analyses and plot/workbook presentation files are not included. New reconstruction and context checks are identified as such. See [RELEASE_SCOPE.md](docs/RELEASE_SCOPE.md) and [CONTEXT_REPRODUCTION.md](docs/CONTEXT_REPRODUCTION.md).

Chemistry was measured once per sample on the analytical portion, not separately in both magnetic fractions. The study concerns retrospective screening/triage within one campaign. Number blocks are a code-derived convention; the 45 outer batches overlap. Reproduction does not establish instrument accuracy, independent geographic validation, causal sources or prospective monetary savings.

The campaign article and 2022 Yarmouk University master's thesis are ordinary scientific sources cited in the accompanying metadata. This data/software deposit does not represent journal publication or acceptance of the new manuscript.

## Licenses and citation

Original software: MIT. Author-owned research data and documentation: CC BY 4.0. Licenses apply to separate components, not as alternatives for all files. Third-party rights remain unchanged. See [LICENSING.md](LICENSING.md) and [CITATION.cff](CITATION.cff).
