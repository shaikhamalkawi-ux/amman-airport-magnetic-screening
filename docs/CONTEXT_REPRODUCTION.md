# Independent reproduction of the context baselines

This verification program was written on 26 September 2026 to reproduce the context-model results already reported for the Amman-Airport magnetic-screening study. It is new verification code, not the recovered historical generator. The author-supplied scripts and reference outputs are preserved separately.

## Run

From the repository root, with the release's NumPy dependency installed:

```sh
python code/verify_context_independently.py
```

The program finds the repository relative to its own location, so it can also be invoked from another working directory. `--repo-root`, `--source`, `--reference`, `--primary-reference`, and `--output` provide explicit path overrides. Output defaults to `results/context_reproduction/`. A successful exit requires agreement with both sets of expected values and the canonical source-master hash.

Required released inputs:

- `endpoint_extension/Source_Reconstructed_Master_44.csv`
- `results/v6_mn_context_safeguard.csv`
- `tests/fixtures/context_primary_expected.csv`

The fixture contains 27 context-model rows, with four printed metrics each, transcribed programmatically from the authors' original V11R3 supplementary LaTeX table. Expected values are not regenerated from this checker. Their source hashes are recorded in `tests/fixtures/context_reference_provenance.json`. No LaTeX engine or manuscript source is needed to run the check.

## Model and distance units

The unchanged source workbook, `04_M-Ghraam2026_ORIGINAL_UNCHANGED.xlsx`, has SHA-256 `4ff48393b15d83306e9099efa30e12ee2d797cd57a0b75c44b8f99726380becb`. Its `dist!C2` field identifies distance in metres, and the reconstructed master carries `Distance_numeric_m`.

For each held-out block, the checker fits an ordinary least-squares model with an intercept to log10 metal concentration. Context uses `log10(1 + d_m)` and a binary recorded-side indicator, where `d_m = distance / (1 metre)`. Context+F adds log10 fine-fraction LF susceptibility; Context+FC adds log10 fine- and coarse-fraction LF susceptibility. The master contains 44 samples; the common paired cohort has 43 after excluding sample 24, which lacks the coarse record.

The independent implementation solves the unscaled design directly with `numpy.linalg.lstsq`. With an intercept and these designs, this is the same fitted linear model as training-fold centering/scaling. It does not import or execute an author fitting helper. High-sample recovery ranks predicted and observed log concentrations descending, breaking exact ties by ascending sample number, with both high-set and assay budget equal to 11.

Block conventions checked are:

- Ten blocks from the numeric suffix of the recorded R/L code.
- Nineteen blocks from the full recorded R/L code.
- Five merged blocks: {1,2}, {3,4}, {5,6}, {7,8}, {9,10}.

The five-block map is an explicit reconstruction that reproduces the published aggregate results. No historical code defining this map was recovered. These remain recorded-code analysis conventions, not newly established geographic independence.

## Reproduction result

Using NumPy 2.3.5, the portable check reproduced all nine rows of the existing Mn context-safeguard CSV: 27 floating-point values and nine recovery counts. Maximum absolute floating-point difference was `8.43769498715119e-15`; all counts were exact. It also reproduced all 108 printed R2, Q2, sample-weighted MAE and block-weighted MAE values for the three context configurations across all nine metals to their three displayed decimal places.

The test reports each comparison and does not change the reference results. Outputs include computed metrics, per-sample predictions, comparison CSVs, diagnostic transforms and a machine-readable summary with input/script hashes.

The supplied diagnostic checks show that using kilometres inside `log10(1 + distance)`, raw distance, or `log10(distance)` does not reproduce all the reference metrics. Natural-log `ln(1 + d_m)` produces the same fitted predictions because changing log base only rescales a predictor in an unpenalized linear model. The manuscript specifies log10; numerical agreement alone cannot distinguish equivalent log bases or reversed binary-side coding with an intercept.

## Scope

This verifies the reported primary context metrics and the Mn context grouping safeguard. Agreement corroborates the stated metre-based transform against the actual source and published values. It does not prove the identity of historical code or establish that every prior per-sample prediction was identical, because the historical prediction files were not supplied. It does not by itself reproduce every other analysis in the study or validate the archived measurements externally. No scientific result was replaced or silently altered.
