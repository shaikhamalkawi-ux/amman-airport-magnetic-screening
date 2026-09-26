# Magnetic Screening V11R3 scientific-extension protocol

Date locked before executing the extension analysis: 2026-09-25.
Baseline manuscript: V11R2. This branch must not overwrite V11R2 unless the extension is scientifically informative and all-author approval follows.

## Source lock
- Canonical original workbook: `04_M-Ghraam2026_ORIGINAL_UNCHANGED.xlsx`.
- Required SHA-256: `4ff48393b15d83306e9099efa30e12ee2d797cd57a0b75c44b8f99726380becb`.
- Deterministic source reconstruction: `Source_Reconstructed_Master_44.csv` from SourceLock V3.
- Required SHA-256: `e1804049d7e2819e8b1228eb55db81524caaa18cb6d4745000c20d3ce609d105`.
- Paired analysis cohort: 43 samples; sample 24 is excluded from every paired configuration because coarse magnetic measurements are missing.
- Primary grouping: ten numeric suffix blocks obtained by pairing R/L site codes with the same station number. These are analysis blocks, not independently verified geographic sites.

## Reproduction gate
Before any new result is interpreted, reproduce the V11R2 fixed-model blocked results for F, C, Fnu, Cnu, and FC using the source-locked 43-sample cohort. The gate passes only if the recalculated values match the V11R2 displayed results to rounding and the unrounded aggregate outputs available from the public repository to numerical precision.

## Scientific question A: endpoint-directed measurement selection
Question: Does selecting the magnetic measurement configuration by held-out screening recovery, instead of prediction error, improve screening recovery on outer held-out batches?

Candidate configurations are identical under both selection rules:
- F: fine fraction, LF only.
- C: coarse fraction, LF only.
- Fnu: fine fraction, LF plus frequency information.
- Cnu: coarse fraction, LF plus frequency information.
- FC: fine and coarse fractions, LF on each.

### Outer evaluation
- Hold out every pair of the ten number blocks: 45 outer test batches.
- The remaining eight blocks are the outer training set.
- After selecting a configuration using outer-training data only, refit that configuration on all eight outer-training blocks and score every sample in the held-out pair with one model.
- For an outer test batch of size nB, define both the high set and the chemistry-selection budget as `ceil(nB/4)`.
- Ranking ties are broken by ascending numerical sample ID.

### Inner selection
Within each outer training set:
- Evaluate all 28 pairs of the eight training blocks as inner held-out batches.
- For each candidate configuration and each inner pair, fit on the other six blocks and score the held-out pair with one model.
- MAE score: for each inner pair, compute MAE separately in its two constituent blocks and average the two block means; then average across the 28 inner pairs.
- Recovery score: within each inner pair, set high-set size = selection budget = `ceil(n_inner_pair/4)` and compute recall; then average recall across the 28 inner pairs.

Selectors:
- `S_MAE`: configuration with the smallest mean inner block-balanced MAE.
- `S_REC`: configuration with the largest mean inner recovery. Exact recovery ties are broken by smaller mean inner MAE; remaining ties are broken by fewer magnetic measurements and then fixed order F, C, Fnu, Cnu, FC.
- `S_MAE` numerical ties within 1e-12 are broken by fewer magnetic measurements and then the same fixed order.
- Every recovery-primary tie is logged; tie frequency is part of the result rather than hidden.

Primary outer contrast for each metal and outer batch:
`DeltaR = Recall(S_REC) - Recall(S_MAE)`.
Positive values favor recovery-directed selection. Report all nine metals, including ties and negative results. The 45 overlapping batches are descriptive repeated evaluations, not 45 independent experiments; no confirmatory p-value will treat them as independent.

## Scientific question B: frequency-representation sensitivity
Run the complete experiment under two representations of frequency information, while keeping samples, folds, candidate counts, OLS estimator, standardization, tie handling, and budgets unchanged.

Current representation:
- Fnu = [log10(Fine_LF), Fine_FD_percent]
- Cnu = [log10(Coarse_LF), Coarse_FD_percent]

Alternative representation (only if both LF and HF are positive on the admitted cohort):
- Fnu = [log10(Fine_LF), log10(Fine_HF)]
- Cnu = [log10(Coarse_LF), log10(Coarse_HF)]

F, C and FC are unchanged. No zero replacement, clipping, or row deletion is allowed merely to make the alternative logarithm computable.

Also compare the two frequency representations under the original ten-block fixed-model evaluation for all nine metals, reporting pooled R2, block-balanced MAE, and primary k=11 recovery.

## Robustness
- Positivity audit for all four LF/HF variables.
- Full delete-one-original-block rerun of the endpoint-directed outer-pair experiment. After one block is deleted, evaluate all 36 pairs among the remaining nine blocks with the same nested rules. Report the range of the mean DeltaR across the ten deletion reruns for each metal and representation.
- Do not change the primary quarter-budget definition, candidate family, or reported metal set after seeing results.

## Interpretation rules
- Improvement is not assumed. A null, tied, or unstable result is reportable.
- Do not claim independent external validation, causal benefit, universal measurement ranking, safe exclusion of untested samples, or prospective cost-effectiveness.
- The frequency-representation comparison tests estimator/representation sensitivity; it does not add new physical measurements.
- If the extension does not add a stable scientific finding, retain V11R2 for submission and archive this branch as a negative/diagnostic analysis rather than rewriting the manuscript around it.
