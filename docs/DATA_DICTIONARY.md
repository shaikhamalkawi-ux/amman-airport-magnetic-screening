# Data dictionary

## Study and files

The data describe 44 archived roadside-soil samples from the Amman–Airport Highway, Jordan. Magnetic measurements concern the fine (<125 µm) and coarse (125–250 µm) fractions. Chemistry was measured once per sample on the <125 µm analytical portion; these data do not provide separate metal concentrations for both magnetic fractions.

The two numerical source files are:

| File | Role | SHA-256 |
|---|---|---|
| `04_M-Ghraam2026_ORIGINAL_UNCHANGED.xlsx` | Original workbook, preserved without editing or recalculation. | `4ff48393b15d83306e9099efa30e12ee2d797cd57a0b75c44b8f99726380becb` |
| `Source_Reconstructed_Master_44.csv` | Author-supplied reconstructed table, one row per archived sample. | `e1804049d7e2819e8b1228eb55db81524caaa18cb6d4745000c20d3ce609d105` |

The CSV has 44 rows and 31 columns. Blank fields denote missing coarse magnetic information for sample 24; they are not zeros. Every paired magnetic analysis uses the same 43 samples, excluding sample 24 even for configurations that use only the fine fraction. All 43 retained LF/HF values are positive. Four negative coarse FD percentages are preserved, for samples 20, 25, 26 and 38.

The CSV is supplied as an input to the extension runner. The accompanying source-check script verifies specified fields against workbook cells; it does not create the CSV anew. See [Release scope](RELEASE_SCOPE.md).

## Sample and location fields

For sample identifier `s`, the main sample records occupy workbook row `s + 2` in `dist` and `Enrichment Factor` (rows 3–46).

| CSV field | Type / unit | Definition and source |
|---|---|---|
| `Sample` | Integer identifier, 1–44 | Stable archived sample identifier. It is used for deterministic numerical-ID ranking ties. |
| `SiteCode` | Text | Recorded R/L code with numerical suffix; `dist!B3:B46`. There are 19 distinct codes. |
| `Side` | Text, `R` or `L` | Letter component of `SiteCode`. It identifies the recorded side code, not an independently verified spatial direction. |
| `StationNumber` | Integer, 1–10 | Numerical suffix of `SiteCode`. It defines the primary analysis block. |
| `Distance_raw` | Text | Original content of `dist!C3:C46`, including numeric entries, `1m`, and short field annotations. |
| `Distance_numeric_m` | Number, metres | Numerical distance represented by the archived entry. The source header `dist!C2` explicitly states `distance (m)`. Entries include 1, 10, 20, 50, 70, 100, 150 and 200 m. |
| `LocationIndex` | Integer identifier | Index in `LOCATION!A2:A20`, matched by `SiteCode` to `LOCATION!B2:B20`. It is distinct from `Sample` and `StationNumber`. |
| `Latitude_raw` | Text | Original latitude entry from `LOCATION!C2:C20`, matched by site code. |
| `Longitude_raw` | Text | Original longitude entry from `LOCATION!D2:D20`, matched by site code. |

Coordinate strings retain their original inconsistent formatting and are not corrected decimal-degree coordinates. Numeric-code blocks are reproducible analysis groups; the archive does not independently establish ten geographically independent sites. The retained sample counts in blocks 1–10 are **4, 2, 9, 2, 2, 10, 2, 9, 2 and 1**, respectively.

The recorded distance unit is verified. The endpoint-extension code does not use distance or side. The separate, newly written context verification reproduces the reported aggregates and printed metrics using the manuscript's `log10(1 + distance in metres)` transformation; see CONTEXT_REPRODUCTION.md. The historical context-model generator itself has not been recovered.

## Magnetic fields

LF and HF denote low- and high-frequency measurements. Raw `K` values are the workbook's instrument-reading numbers, labelled in units of 10^-5 SI. Reconstructed susceptibility values are numerical multiples of **10^-8 m³ kg^-1**: for example, a stored value of 96.68 represents 96.68 × 10^-8 m³ kg^-1.

| CSV field | Type / unit | Definition and source |
|---|---|---|
| `Fine_Klf_raw` | Number, workbook reading scale | Fine LF reading from `dist!D3:D46`. |
| `Fine_Khf_raw` | Number, workbook reading scale | Fine HF reading from `dist!E3:E46`. |
| `Fine_net_mass_g` | Number, g | Adopted fine net mass under the rules below. |
| `Fine_mass_rule` | Text | Row-specific description of the adopted mass rule. |
| `Fine_LF_reconstructed` | Number, 10^-8 m³ kg^-1 | Reconstructed fine LF susceptibility. |
| `Fine_HF_reconstructed` | Number, 10^-8 m³ kg^-1 | Reconstructed fine HF susceptibility. |
| `Fine_FD_pct` | Number, percent | Fine frequency dependence, calculated from LF and HF. A value of 3 denotes 3%, not 0.03%. |
| `Coarse_Klf_raw` | Number, workbook reading scale; blank for sample 24 | Coarse LF reading from `dist!K3:K46`. |
| `Coarse_Khf_raw` | Number, workbook reading scale; blank for sample 24 | Coarse HF reading from `dist!L3:L46`. |
| `Coarse_mass_g` | Number, g; blank for sample 24 | Recorded coarse mass from `dist!M3:M46`, used directly by the reconstruction. |
| `Coarse_LF_reconstructed` | Number, 10^-8 m³ kg^-1; blank for sample 24 | Reconstructed coarse LF susceptibility. |
| `Coarse_HF_reconstructed` | Number, 10^-8 m³ kg^-1; blank for sample 24 | Reconstructed coarse HF susceptibility. |
| `Coarse_FD_pct` | Number, percent; blank for sample 24 | Coarse frequency dependence. Negative values are retained. |

For either fraction and frequency, the stored susceptibility number is reconstructed as

```text
susceptibility_number = 10 × raw_reading_number / adopted_mass_g
physical susceptibility = susceptibility_number × 10^-8 m³ kg^-1
```

The adopted fine-mass rules are:

- Samples 1–15, except sample 8: use the cached net-mass value in `dist!G(s+2)` directly.
- Sample 8: use `Enrichment Factor!D10 − dist!G53`; the corresponding `dist!G10` mass formula is inconsistent with the adopted tare rule.
- Samples 16–44: use `dist!G(s+2) − dist!G53`.

The bottle mass in `dist!G53` is **2.999 g**. For sample 18, the primary rule uses the `dist` entry; the alternative gross mass remains in `Enrichment Factor!D20`. The original workbook preserves both entries. The endpoint-extension runner uses the supplied primary reconstruction and does not regenerate the separate alternative-mass sensitivity.

Frequency dependence is

```text
FD_pct = 100 × (LF − HF) / LF
```

Because LF and HF within a fraction share the adopted mass, the same percentage can be calculated from its raw LF/HF readings. The reconstructed fields use unrounded numerical values; rounded susceptibility cells elsewhere in the original workbook are not substitutes for these fields. The 87 available fine/coarse FD percentages agree with independent raw-reading calculations to floating-point precision.

The primary models use `log10(LF / χ0)` and FD, with `χ0 = 10^-8 m³ kg^-1`. Since the CSV stores numerical multiples of χ0, the original code applies `log10` directly to the stored LF numbers. The alternative frequency representation uses the corresponding logarithms of LF and HF; it adds no new measurement.

## Chemistry fields

Each chemistry column contains a positive sample-level concentration in **mg kg^-1**. The nine fields, in source order, are:

| CSV field | Element | Workbook final-concentration column |
|---|---|---|
| `Fe_mgkg` | Iron | `Enrichment Factor!T3:T46` |
| `Zn_mgkg` | Zinc | `Enrichment Factor!U3:U46` |
| `Cu_mgkg` | Copper | `Enrichment Factor!V3:V46` |
| `Cr_mgkg` | Chromium | `Enrichment Factor!W3:W46` |
| `Co_mgkg` | Cobalt | `Enrichment Factor!X3:X46` |
| `Ni_mgkg` | Nickel | `Enrichment Factor!Y3:Y46` |
| `Mn_mgkg` | Manganese | `Enrichment Factor!Z3:Z46` |
| `Pb_mgkg` | Lead | `Enrichment Factor!AA3:AA46` |
| `Cd_mgkg` | Cadmium | `Enrichment Factor!AB3:AB46` |

The source checks read the archived cached final-concentration values in these cells. The workbook's conversion is `50 × C / w`, where `C` is the corresponding concentration in mg L^-1 in columns H–P and `w` is the analytical mass in grams in column G. The factor corresponds algebraically to a 0.050 L volume divided by mass in kilograms. The original archive, rather than a new inferred laboratory protocol, is the source of these conversion values.

The analysis applies a base-10 logarithm to each numerical mg kg^-1 concentration. No concentration is imputed for a missing magnetic fraction, and the chemistry is not partitioned into separate fine/coarse targets.

## Original workbook structure

The archive contains five visible sheets: `Enrichment Factor`, `dist`, `colration x`, `LOCATION` and `Factor Analysis`. Nine per-metal laboratory sheets are hidden in the original: `Fe`, `zn`, `cu`, `cr`, `Co`, `ni`, `Cd`, `Mn` and `Pb`.

The hidden sheets contain laboratory/calibration records and additional labelled rows beyond the 44-sample analysis cohort. They remain as archival context and are not additional observations in the current analysis. The workbook also contains an attributed study-location map and earlier correlation/factor-analysis material. These objects are preserved; they do not independently validate field-site separation or the current model results.

One unused summary cell, `dist!J48`, has a stored `#DIV/0!` result for `AVERAGE(J3:J46)`. It is outside the sample-data rows and is not read by the source-check or endpoint-extension scripts. The original file is preserved without repairing that cached value or changing its hash.
