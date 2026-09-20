# Analysis input (not included)

This public repository intentionally does **not** contain the original author/team spreadsheets or the controlled source workbook.

The public analysis code expects a CSV named `data/analysis_input.csv` with one row per archived sample and these columns:

- `Sample` — stable sample identifier used only for deterministic tie breaking.
- `Block` — the predeclared grouped-validation block identifier.
- `SiteCode` — optional side/site code used for sensitivity checks.
- `Side` — optional `L`/`R` field.
- `Distance_m` — optional non-negative road-distance field.
- `Fine_LF`, `Coarse_LF` — mass-specific low-frequency susceptibility for the fine and coarse fractions.
- `Fine_FD_pct`, `Coarse_FD_pct` — frequency-dependence percentage for the fine and coarse fractions.
- `Fe_mgkg`, `Zn_mgkg`, `Cu_mgkg`, `Cr_mgkg`, `Co_mgkg`, `Ni_mgkg`, `Mn_mgkg`, `Pb_mgkg`, `Cd_mgkg` — sample-level chemistry.

Rows without a paired coarse measurement are excluded only from analyses that require the paired fine/coarse cohort.

The repository intentionally provides the schema and analysis logic without redistributing the controlled source data.
