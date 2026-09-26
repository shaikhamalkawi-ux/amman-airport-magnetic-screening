# Release scope and reproduction

This release provides the original study workbook, the author-supplied reconstructed 44-row table, and the unchanged author code for the endpoint-directed selection and frequency-representation extension. The code has been rerun from copies of those inputs, and its numerical outputs have been reconciled with the archived outputs and the corresponding manuscript tables.

The release supports an executable replay of the stated extension. It also supplies new independent utilities for reconstructing the master table from the workbook and verifying the context models. These utilities are distinguished from the unchanged author scripts. The release does not supply a single original generator for every historical analysis in the manuscript.

## What the original runner does

`run_all.py` performs the following sequence:

1. Checks the SHA-256 identities of `04_M-Ghraam2026_ORIGINAL_UNCHANGED.xlsx` and `Source_Reconstructed_Master_44.csv`.
2. Runs `source_trace_audit.py` to compare 878 specified source-to-table fields, including sample codes, magnetic readings, adopted masses, reconstructed LF/HF values and the nine final chemistry targets.
3. Runs `run_extension.py` for both FD and logHF representations: five fixed candidate models, the two endpoint-directed selectors, all 45 outer block pairs, and ten complete deleted-block reruns with 36 outer pairs each.
4. Produces configuration counts, representation-stability summaries, fixed-model representation comparisons, standardized-design condition numbers and selected fixed-model numerical checks.
5. Checks the source identities and stated numerical invariants before reporting successful completion.

The output comprises 810 central metal-by-batch records and 6,480 deleted-block metal-by-batch records calculated during execution. The runner saves central records and deletion summaries; it does not save every internal prediction or every inner candidate score.

## Reproduction command

Use a writable copy of the directory containing the original scripts and both input files. Keep the filenames unchanged and the files together because the scripts resolve paths relative to their own directory.

The verified execution used Python **3.12.14**, NumPy **2.3.5** and openpyxl **3.1.5**. The author's `requirements.txt` allows broader compatible version ranges. To use the versions checked for this release, run:

```bash
python -m pip install numpy==2.3.5 openpyxl==3.1.5
python run_all.py
```

The command writes result CSVs beside the scripts. Keep the published reference outputs separately when comparing a new run, because running in their directory replaces files with the same names.

| Output | Contents |
|---|---|
| `Source_to_Extension_Audit.csv` | Source-to-table comparisons for the 878 checked fields. |
| `Selector_OuterPairs.csv` | Selected configurations, inner selected-candidate scores, recovery tie-set summaries, held-out integer hits/recall and losses for 810 central metal-by-batch records. |
| `Selector_Summary.csv` | Mean/median selector contrast, win/tie/loss counts and configuration differences by metal and representation. |
| `DeleteBlock_ByDeletion.csv` | Mean recall contrast for each metal, representation and deleted original block. |
| `DeleteBlock_Robustness.csv` | Ranges, medians and sign counts across the deleted-block reruns. |
| `Fixed_FD.csv`, `Fixed_logHF.csv` | Fixed-candidate primary blocked results under each frequency representation. |
| `Selection_Counts.csv` | Configuration-selection counts for each selector, metal and representation. |
| `Representation_Selection_Stability.csv` | Selector and recall changes between representations on matched outer batches. |
| `Fixed_Representation_Sensitivity.csv` | Changes in fixed frequency-aware models between FD and logHF. |
| `Representation_Conditioning.csv` | Condition-number summaries for standardized training designs. |
| `Reproduction_Anchor_Differences.csv` | Differences from the selected fixed-model numerical reference values. |

## Verified scope

The unchanged author execution completed successfully. All 878 source-to-table checks passed, with a maximum absolute difference of **2.842 × 10^-14**. All 12 generated CSVs reconciled with their author-supplied counterparts: **21,139 numerical cells** agreed within absolute/relative tolerances of 10^-12, with maximum absolute difference **2.842 × 10^-14**; compared text categories agreed exactly.

A separate reconciliation checked **462 printed numerical cells** in Main Table 4 and Supplementary Tables S14–S18. They agree with the rerun at the stated printed precision. Additional checks confirmed all 87 available fine/coarse FD percentages against raw readings and 117 fixed-model comparisons against independently archived public aggregate results. The paired cohort is exactly 43 unique samples, excluding sample 24.

Floating-point differences across executions are reported rather than described as byte-identical reproduction. For example, the maximum discrepancy in the eight selected fixed-model reference checks was approximately 6.66 × 10^-16 in this run, compared with the historical approximately 5.55 × 10^-16 value. This is consistent with numerical precision and does not change the reported results.

## Selector tie conventions

The code uses an absolute numerical tolerance of **10^-12** for selector-score ties:

- S_MAE retains candidates whose mean inner block-balanced MAE is at most the minimum plus 10^-12, then chooses fewer magnetic measurements and finally the fixed order F, C, Fν, Cν, FC.
- S_REC retains candidates whose mean inner recall is at least the maximum minus 10^-12. Within that set it uses smaller mean inner MAE with the same 10^-12 tolerance, then measurement count and the same fixed order.
- F and C require one magnetic measurement; Fν, Cν and FC require two.

Sample rankings use descending actual observed concentration or prediction score and ascending numerical sample ID for exact ties. That ranking rule is distinct from the numerical tolerance applied to selector scores. The released scripts are the reference for these numerical conventions.

## Coverage limits

`Source_Reconstructed_Master_44.csv` remains the unchanged author input used by the original runner. The historical master-generation program was not recovered. A new independent utility, `reconstruct_master_from_workbook.py`, reconstructs all 44 rows and 31 fields directly from workbook cells without using reference values in construction. It agrees with all 1,364 reference fields: 1,094 numerical fields within 10^-12 absolute/relative tolerances (maximum absolute difference 3.908 × 10^-14), and 270 categorical fields exactly. CSV byte identity is not claimed; the unchanged author master is retained for the original runner's SHA-256 check. See the independent-verification README for the utility command and its `RECONSTRUCTION_RESULT.json` evidence.

The archived distance unit is directly documented as metres in workbook `dist!C2`. The new independent `verify_context_independently.py` implements Context, Context+F and Context+FC with recorded side and log10(1 + distance_m), including the stated block groupings. It reproduces all 36 archived Mn context-summary values (maximum absolute difference 8.44 × 10^-15) and all 108 printed primary context-model metrics at displayed precision. The original historical context-model generator was not recovered. This independent context implementation is supplied separately from `run_all.py`, `source_trace_audit.py` and `run_extension.py`, which do not execute these context analyses.

The runner also does not regenerate the older alternative-mass/grouping sensitivities, shared-list diagnostic, fixed external-threshold comparison, or external coastal-sediment reanalysis. Earlier public scripts and aggregate tables have their own stated coverage and are not evidence that this extension runner implements those analyses.

Figure files and an author verification workbook are supplied as archived artifacts where included in the release. The recovered scripts do not regenerate those presentation files. Their underlying extension values have been checked, but compiling manuscript sources or retaining figure PDFs is distinct from regenerating graphics from numerical outputs.

Computational reproduction does not establish instrument accuracy, independently verified geographic replication, causal sources, external validation or prospective laboratory savings. The 45 held-out batches overlap; their mean contrasts and deleted-block ranges retain the descriptive interpretation stated in the paper.
