# Analysis code

This directory contains the **public-safe** implementation of the central V4 screening comparison.

## Files

- `analyse_public.py` — grouped prediction, selected-single benchmark, frequency-versus-fraction comparison, triage curves, held-out pair-batch audit, and conditional resource frontier.
- `verify_public.py` — aggregate structural and arithmetic checks.
- `run_public.sh` — sequential runner.

The scripts do not contain the controlled source workbook or source values. They require an authorized local `data/analysis_input.csv` described in `data/README.md`.

The public implementation deliberately emits aggregate outputs only. Source-cell traces, row-level prediction files, selected sample-ID lists, and private provenance records remain outside this repository.
