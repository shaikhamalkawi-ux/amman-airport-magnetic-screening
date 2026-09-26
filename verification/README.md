# Independent endpoint-extension verification

`verify_reproduction.py` runs the original author code in a fresh temporary directory. It does not modify the supplied workbook, master CSV, scripts or reference outputs. It compares all 12 generated CSV files with the saved author snapshots: numerical cells use absolute/relative tolerance 1e-12, categorical cells must match exactly, and row/column counts must agree.

Use Python 3.10 or newer with the original requirements:

```text
python -m pip install -r endpoint_extension/requirements.txt
python verification/verify_reproduction.py endpoint_extension --report verification/VERIFICATION_RESULT.json
```

Replace the example directories with the corresponding locations in your checkout. If the saved author CSV outputs are in a separate folder:

```text
python verification/verify_reproduction.py endpoint_extension --expected-dir results/endpoint_reference --report verification/VERIFICATION_RESULT.json
```

The author directory must contain `run_all.py`, `source_trace_audit.py`, `run_extension.py`, the original workbook, and `Source_Reconstructed_Master_44.csv`. The reference folder must contain the 12 CSVs listed in `OUTPUTS` in the verifier. Write the verification report outside those input/reference directories.

The verifier checks the two fixed source SHA-256 values before execution, captures the actual process exit code and log, compares every output cell, and verifies that supplied files remain unchanged. The temporary directory contains no preexisting result snapshots and is removed after comparison. The JSON report records source and script hashes, dependency versions, elapsed time and per-file differences.

A successful run exits with code 0 and prints `PASS`. Any failed scientific assertion, source-hash mismatch, missing output, categorical difference or numeric discrepancy causes failure. This verifies the endpoint-extension calculation; it is not a claim that the original extension scripts regenerate every historical auxiliary analysis or manuscript-production artifact. See `REPRODUCTION_REPORT.md` and the release scope document.

## Independent workbook-to-master reconstruction

`reconstruct_master_from_workbook.py` is a **new release utility**, not the historical author SourceLock V3 generator. It reconstructs all 44 rows and 31 columns using only the unchanged workbook's cached values and documented cell/mass rules. The reference CSV is used only for the optional comparison, never to construct a value. Raw coordinate and distance strings are preserved, not repaired.

```text
python verification/reconstruct_master_from_workbook.py endpoint_extension/04_M-Ghraam2026_ORIGINAL_UNCHANGED.xlsx outputs/reconstructed_master_independent.csv --reference endpoint_extension/Source_Reconstructed_Master_44.csv --report verification/RECONSTRUCTION_RESULT.json
```

The utility refuses an existing output filename and validates the original workbook checksum. It compares every output field: raw text and categorical values exactly, numeric values within absolute/relative tolerance 1e-12. The verified reconstruction agrees in all 1,364 cells. Its CSV is numerically equivalent but not byte-identical to the author master, due to serialization/floating-point details. Preserve the original author master for unchanged `run_all.py`, which intentionally checks that file's exact historical SHA-256. Do not silently substitute the new CSV or change the author's expected hash.
