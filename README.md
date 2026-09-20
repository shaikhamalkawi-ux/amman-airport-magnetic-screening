# Amman–Airport Magnetic Screening

**Public research repository**

This repository supports the secondary-analysis study:

> **Frequency or particle size? Choosing additional magnetic measurements for roadside-soil screening**

The study re-analyses an archived 44-sample roadside-soil campaign from the Amman–Airport Highway, Jordan. The central question is practical: **when laboratory resources are limited, is the more useful additional magnetic information obtained from a second measurement frequency within one particle-size fraction, or from preparing and measuring a second particle-size fraction?**

## Scientific scope

The analysis compares magnetic-screening strategies using archived Bartington MS2B measurements and sample-level chemistry for Fe, Zn, Cu, Cr, Co, Ni, Mn, Pb, and Cd. It evaluates prediction error, ranking/triage performance, grouped sensitivity, held-out batch performance, and conditional resource trade-offs.

The repository keeps the scientific claim boundaries explicit:

- chemistry was measured once per sample on the analytical portion, not separately in the two magnetic fractions;
- magnetic screening is treated as a **triage tool**, not as a replacement for confirmatory geochemistry;
- no causal source attribution, bioavailability claim, or external geographic/temporal validation is inferred from the archived campaign;
- the numeric R/L suffix blocks are an analysis blocking convention, not independently verified physical co-location;
- no monetary saving is claimed without an observed local cost ledger.

## Current scientific revision

Current internal scientific revision: **V4 (2026-09-20)**.

Key result: the preferred magnetic measurement depends on the metal and the downstream decision criterion. A configuration with the best predictive R² does not necessarily provide the best low-budget sample-recovery performance.

## Public-safe analysis code

The repository now contains a public-safe implementation of the central V4 comparison in `code/analyse_public.py`.

The code expects a local `data/analysis_input.csv` matching the schema documented in `data/README.md`. The controlled author/team source archive is **not included** in this public repository.

To run after supplying an authorized local input file:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash code/run_public.sh
```

The runner writes aggregate analysis outputs only. It does not emit source-cell traces, row-level prediction files, or selected sample-ID lists.

## Publication-safe results

The `results/` directory contains selected aggregate outputs supporting the current manuscript:

- primary blocked performance;
- incremental FC-versus-selected-single error comparison;
- fixed-budget triage summary;
- 80% retrospective recovery frontier;
- held-out pair-batch summary.

These aggregate files are included for transparency and inspection; they are not a substitute for the controlled source archive.

## Public-repository policy

This repository is intentionally **public**. Original study-team spreadsheets, source documents, raw/source-level data, private transfer packages, and row-level source reconstructions are not uploaded unless the original team explicitly approves release.

See `PUBLIC_RELEASE_POLICY.md`.

## Reproducibility

The controlled V4 package passed:

- 268 numerical/property checks;
- an independent QR-based numerical cross-check;
- clean replay with 21/21 generated CSV tables reproduced byte-for-byte;
- LaTeX cross-reference, font, and render QA.

The public-safe implementation was also run locally against an authorized adapted input and reproduced the headline V4 values, including Mn FC R² ≈ 0.4055, Cu FC R² ≈ 0.4875, and Cr C-frequency block-MAE ≈ 0.09466.

These checks establish computational reproducibility of the implemented analysis. They do **not** establish instrument accuracy, external validation, or geographic independence.

## Repository status

Public-safe code, documentation, and aggregate results are available. Source-data release, manuscript posting, licence, and permanent DOI remain author-stage decisions.
