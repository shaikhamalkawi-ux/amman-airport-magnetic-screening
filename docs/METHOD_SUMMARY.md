# Method summary

The public code implements the central comparison reported in the V4 study without redistributing the controlled source workbook.

## Measurement alternatives

- **F**: fine-fraction low-frequency susceptibility.
- **C**: coarse-fraction low-frequency susceptibility.
- **Ffreq**: fine-fraction low-frequency susceptibility plus frequency dependence.
- **Cfreq**: coarse-fraction low-frequency susceptibility plus frequency dependence.
- **FC**: low-frequency susceptibility from both particle-size fractions.
- **Single4_G**: one of F, C, Ffreq, or Cfreq chosen inside each outer training split using grouped inner validation.

Each model is linear on log10-transformed concentration outcomes. Predictors are standardized using only the training data for the corresponding split.

## Validation logic

The primary public implementation uses grouped outer validation. The selected-single strategy is chosen inside the outer training data; the held-out block is not used for that choice. A second audit with pairs of held-out blocks uses one fitted model for the whole held-out batch.

## Decision endpoints

The analysis separates:

1. concentration prediction error and R²;
2. rank-based chemical-analysis triage at fixed sample budgets;
3. conditional resource accounting: how many chemical assays are avoided at a specified retrospective recovery target.

The key methodological lesson is that the configuration with the best predictive R² need not provide the best low-budget recovery ranking.

## Claim boundary

The analysis is a secondary, retrospective screening study. It is not prospective or external validation, and no public cost-saving claim is made without an observed local cost ledger.
