# Codex computational audit task

Act as a second computational auditor of the V4 analysis. Do not assume existing PASS records are correct.

## Audit goals

1. Reproduce the supplied pipeline in a clean environment.
2. Recompute the principal regressions and ranking/triage calculations using a separately written implementation rather than importing the original analysis functions.
3. Check group blocking, nested model selection, held-out predictions, ties, missing values, and sample counts.
4. Verify frequency-versus-particle-size comparisons and the distinction between predictive R² and low-budget sample recovery.
5. Verify conditional resource/cost arithmetic without introducing unobserved prices.
6. Record every discrepancy and whether it changes any manuscript result or claim.

## Non-negotiable boundaries

- Do not change the archived data to improve results.
- Do not tune models to produce a preferred outcome.
- Do not convert computational reproducibility into external validation.
- Do not infer geographic independence from numeric sample codes.
- Do not fabricate unavailable cost, calibration, or measurement-uncertainty records.

## Expected return

Return an audit folder or ZIP containing:

- execution log;
- environment/version record;
- separately written audit scripts;
- numerical comparison table;
- discrepancy register;
- final PASS / PASS-WITH-QUALIFICATIONS / FAIL judgment;
- SHA-256 manifest.
