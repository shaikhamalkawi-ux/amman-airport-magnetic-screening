# V11R3 endpoint-extension reproduction report

**PASS.** The original endpoint-extension code was executed using the exact source-locked workbook and reconstructed master CSV. The regenerated results agree with the saved author outputs and the reported Main Table 4 and Supplementary Tables S14–S18. No result-changing discrepancy was found.

## Inputs and method

The verified input identities are:

| Input | SHA-256 |
|---|---|
| `04_M-Ghraam2026_ORIGINAL_UNCHANGED.xlsx` | `4ff48393b15d83306e9099efa30e12ee2d797cd57a0b75c44b8f99726380becb` |
| `Source_Reconstructed_Master_44.csv` | `e1804049d7e2819e8b1228eb55db81524caaa18cb6d4745000c20d3ce609d105` |

All three original executable files—`run_all.py`, `source_trace_audit.py` and `run_extension.py`—were reviewed before execution. They read local inputs, calculate results, and write local outputs. The orchestrator invokes the other two local Python scripts. No network operation, upload or deletion was found.

The original scripts and both inputs were copied without modification to a fresh isolated directory. No saved result CSVs were copied into that directory. Running `python run_all.py` therefore regenerated the outputs rather than reusing the reference snapshots. The supplied source files and snapshots remained unchanged.

The verified environment was Python 3.12.14, NumPy 2.3.5 and openpyxl 3.1.5 on Windows. These versions satisfy the original dependency ranges. The portable verifier records the actual environment, process exit code, script/input hashes, full author log, and every CSV comparison in its JSON report.

## Results

| Verification | Outcome |
|---|---|
| Source-to-extension audit | 878/878 checks pass; maximum absolute numeric difference 2.842170943040401e-14 |
| Paired cohort | 43 distinct sample IDs; only sample 24 excluded from the 44-row master |
| Central endpoint experiment | Both frequency representations, 45 overlapping outer pairs, nine metals: 810 metal-batch records |
| Complete deletion experiment | 10 original-block deletions, 36 outer pairs, nine metals, two representations: 6,480 evaluated records, summarized in 180 per-deletion means |
| Saved-output reconciliation | All 12 regenerated CSVs agree with the original snapshots across 21,139 numeric cells; categorical cells match exactly |
| Main Table 4 | All 72 printed numerical entries agree at displayed precision |
| Supplement S14–S18 | All 390 printed numerical entries agree at displayed precision |
| Independent frequency-dependence check | All 87 available fine/coarse percentages agree with `100 × (KLF − KHF) / KLF` calculated from the raw readings |
| Saved public fixed-model aggregates | 117 comparisons pass: R² and block-MAE for all 45 fixed metal/configuration combinations, plus 27 available recovery-hit counts |

The numeric comparison uses absolute and relative tolerances of 1e-12 and compares every row and column. The maximum difference between regenerated and saved CSV numbers was 2.842170943040401e-14, in conditioning diagnostics. Six output CSVs were byte-identical; the other six differed only at floating-point precision. Verification counts are not independent scientific replications.

Under the primary FD representation, the reproduced mean recall difference is +0.12962962962962965 for Mn and −0.10333333333333335 for Cu. Mn remains positive across all ten deletion reruns; Cu remains negative across all ten. These reproduce the manuscript's rounded +0.130 and −0.103 effects and reported deletion ranges. The alternative logHF representation gives +0.11925925925925927 for Mn and the same Cu difference.

The eight fixed-model reference anchors differ by at most 6.661338147750939e-16 in the verified environment. The previously recorded maximum was approximately 5.55e-16; this negligible environment-dependent difference changes no displayed result.

## Executed selection rules

The original implementation resolves selector ties using a numerical tolerance of **1e-12**:

1. S_MAE admits configurations with inner MAE no greater than the minimum plus the tolerance, then chooses fewer magnetic measurements and finally fixed order F, C, Fν, Cν, FC.
2. S_REC admits configurations with inner mean recall no less than the maximum minus the tolerance. Within that set, it admits inner MAE no greater than the set's minimum plus the tolerance, then chooses fewer measurements and the same fixed order.
3. Measurement counts are F=1, C=1, Fν=2, Cν=2 and FC=2.
4. Sample-ranking ties are resolved by ascending numerical sample ID after descending score. The selector tolerance is not applied to sample ranking.

Descriptions of “exact” selector ties should therefore state the implemented numerical tolerance. This is a methods-reporting clarification; the reproduced calculation was not changed.

## Reproduction scope

This verifies the original V11R3 endpoint extension and its source-linked fixed models. It does not claim that the recovered extension program regenerates every historical auxiliary analysis in the manuscript.

The original pipeline treats the reconstructed master CSV as an explicit input, checks its checksum, and audits its links to the unchanged workbook. It does not contain a script that writes the entire master CSV from scratch. The independent FD calculation supplements the original field audit for predictors used by this extension.

A separate **new release utility**, `reconstruct_master_from_workbook.py`, now reconstructs all 44 rows and 31 columns directly from the original workbook's cached values using the verified cell map and mass rules. All 1,364 fields agree with the author master: raw strings/categorical fields exactly and numeric fields within 1e-12 absolute/relative tolerance. The largest absolute numeric difference is 3.907985046680551e-14. This utility does not use the reference CSV to construct any value and is not represented as recovered historical code. Its output is numerically equivalent but has a different file hash; the unchanged author pipeline retains the original hash-locked CSV as its input.

The recovered code does not generate the earlier Context baselines, source-handling/grouping sensitivities, shared-list/threshold diagnostics or external-data analyses. It also does not regenerate the supplied author audit XLSX or figure PDF/PNG. Their inclusion as preserved artifacts must be distinguished from regeneration by this extension code.

The dated protocol supplies the authors' record of advance specification. Numerical replay does not independently establish historical preregistration, instrument accuracy, independent field sampling, external geographic transfer or prospective cost-effectiveness. The overlapping outer batches remain dependent descriptive evaluations.

## Portable verification

Install the supplied dependencies and run the release's `verify_reproduction.py` with the directory containing the unchanged author scripts and inputs. Its README gives the command and optional location for separately stored reference CSVs. It executes the original pipeline in a fresh temporary directory, compares all 12 outputs, records the verification report, and returns a nonzero exit status if execution or comparison fails.
