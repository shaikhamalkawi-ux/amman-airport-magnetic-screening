# Amman–Airport Magnetic Screening

**Working research repository**

This repository supports the secondary-analysis study:

> **Frequency or particle size? Choosing additional magnetic measurements for roadside-soil screening**

The study re-analyses an archived 44-sample roadside-soil campaign from the Amman–Airport Highway, Jordan. The central question is practical: **when laboratory resources are limited, is the more useful additional magnetic information obtained from a second measurement frequency within one particle-size fraction, or from preparing and measuring a second particle-size fraction?**

## Scientific scope

The analysis compares magnetic-screening strategies using archived Bartington MS2B measurements and sample-level chemistry for Fe, Zn, Cu, Cr, Co, Ni, Mn, Pb, and Cd. It evaluates prediction error, ranking/triage performance, grouped sensitivity, and conditional resource trade-offs.

The repository is designed to keep the scientific claim boundaries explicit:

- chemistry was measured once per sample on the analytical portion, not separately in the two magnetic fractions;
- magnetic screening is treated as a **triage tool**, not as a replacement for confirmatory geochemistry;
- no causal source attribution, bioavailability claim, or external geographic/temporal validation is inferred from the archived campaign;
- the 10 numeric R/L suffix blocks are an analysis blocking convention, not independently verified physical co-location;
- no monetary saving is claimed without an observed local cost ledger.

## Current scientific revision

Current internal revision: **V4 (2026-09-20)**.

Key result: the preferred magnetic measurement depends on the metal and the downstream decision criterion. A configuration with the best predictive R² does not necessarily provide the best low-budget sample-recovery performance.

## Public-repository policy

This repository is currently **public**. For that reason, the following controlled author materials are intentionally **not uploaded** here unless the authors explicitly approve public release:

- the original workbook `M-Ghraam2026.xlsx`;
- raw or source-level data that would reproduce the controlled workbook;
- private author/audit packages;
- unpublished author metadata or correspondence.

Public-safe code, documentation, and verification material can be added here. A complete reproducibility release will be prepared only after the author team decides the data-release and licence terms.

## Reproducibility

The internal V4 package has already passed:
- 268 numerical/property checks;
- an independent QR-based numerical cross-check;
- clean replay with 21/21 generated CSV tables reproduced byte-for-byte;
- LaTeX cross-reference, font, and render QA.

These checks establish computational reproducibility of the archived analysis pipeline. They do **not** establish instrument accuracy, external validation, or geographic independence.

## Repository status

This repository is being initialized for controlled reproducibility and Codex-assisted code audit. Source-data release remains an author decision.

