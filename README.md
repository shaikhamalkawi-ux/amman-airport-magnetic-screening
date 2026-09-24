# Amman–Airport Magnetic Screening

**Public research repository**

This repository supports the secondary-analysis study:

> **When predictive fit and screening utility diverge: choosing frequency or particle size in roadside-soil magnetometry**

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

Current scientific revision: **V10 Environmental Advances submission preparation (2026-09-25)**.

The central result is that measurement value depends on the declared endpoint. A configuration with the best predictive fit does not necessarily provide the best low-budget sample-recovery performance.

V6 introduced the main strengthening safeguards; later revisions retained those results while closing notation, authorship, and submission-production details. V10 changes only target-journal preparation for Environmental Advances:

- the exact Mn C-frequency-versus-two-fraction low-budget ordering is tested against alternative blocking and high-set definitions and is shown not to be invariant;
- recorded distance/side information is made explicit as a simple context baseline;
- an open dual-frequency coastal-sediment dataset is used only as a frequency-only portability stress test, not as external validation of the Jordan fine/coarse comparison.

## Public-safe analysis code

The repository contains a public-safe implementation of the central comparison in `code/analyse_public.py`.

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

The `results/` directory contains aggregate outputs supporting the manuscript, including the primary blocked performance, resource frontier, low-budget triage, V6 endpoint sensitivity, context safeguard, and the external frequency-only stress test.

These aggregate files are included for transparency and inspection; they are not a substitute for the controlled source archive.

## Public-repository policy

This repository is intentionally **public**. Original study-team spreadsheets, source documents, raw/source-level data, private transfer packages, and row-level source reconstructions are not uploaded unless the original team explicitly approves release.

See `PUBLIC_RELEASE_POLICY.md`.

## Reproducibility

The controlled analysis pipeline passed its numerical/property and clean-replay checks. A separately written blocked-OLS implementation reproduced 54 matched primary model/metal metric combinations with maximum absolute difference (3.22\times 10^{-15}) across R², block-MAE, and Spearman metrics.

These checks establish computational reproducibility of the implemented analysis. They do **not** establish instrument accuracy, external validation, or geographic independence.

## Repository status

Public-safe code, documentation, and aggregate results are available. Source-data release, manuscript posting, licence, and permanent DOI remain author-stage decisions.
