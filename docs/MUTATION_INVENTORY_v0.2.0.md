# Verification mutation inventory (v0.2.0, pre-fix baseline)

Baseline: clean `develop` at `cec7e60` (after PR #2). Recompute environment: Linux, Python 3.11.15, NumPy 2.4.4 (P43 additionally under 3.10/NumPy 2.2.6, 3.12 and 3.13/NumPy 2.5.3). Each command was run from a clean checkout; SHA-256 of every tracked file was taken before and after. Frozen evidence was not modified.

## Result

| Classification | Files | Meaning |
|---|---|---|
| BYTE_ONLY | 7 | Bytes differ, content identical after newline normalisation. |
| ENVIRONMENT_METADATA | 3 | Only environment records (Python/NumPy versions) or provenance hashes whose value depends on the checkout's line endings. |
| NUMERICAL_NONMATERIAL | 10 | Recomputed numbers differ; no text/status/structure change and no change at the published precision. |
| NUMERICAL_MATERIAL | 0 | A number changes at the published precision, or any status/classification/structure changes. |
| VERIFICATION_CONTRACT_DRIFT | 1 study (P41) | Verification fails because the study contract no longer matches the code/tests; not a mutation. |

**20 tracked files mutated, all under `papers/*/results/`. Engineering values changed materially: 0. Status, classification, discrepancy or qualification fields changed: 0.**

## Mutations by command

| Command | Files |
|---|---|
| `engiproof verify P08` | 0 |
| `engiproof verify P12` | 0 |
| `engiproof verify P16` | 1 |
| `engiproof verify P29` | 1 |
| `engiproof verify P36` | 1 |
| `engiproof verify P38` | 5 |
| `engiproof verify P40` | 1 |
| `engiproof verify P41` (exit 1: P41 contract drift) | 1 |
| `engiproof verify P42` | 3 |
| `engiproof verify P43` | 7 |
| `engiproof verify P44` | 0 |
| `engiproof verify-all` | 8 |
| `python -m unittest discover -s tests` | 20 |

## Files

| Path | Classification | Modified by | Mechanism |
|---|---|---|---|
| `papers/P16/results/engiproof_verification.json` | NUMERICAL_NONMATERIAL | verify P16 | verify-all | unittest | 3 floats differ at <=1.4e-16 rel (e.g. 406.4 -> 406.40000000000003); also inherited_result_sha256 taken over CRLF checkout bytes (ENVIRONMENT_METADATA) |
| `papers/P29/results/engiproof_verification.json` | ENVIRONMENT_METADATA | verify P29 | verify-all | unittest | inherited_surface_sha256 and inherited_independent_checks_sha256 were taken over CRLF checkout bytes; same content, LF checkout gives a different hash |
| `papers/P36/results/engiproof_verification.json` | ENVIRONMENT_METADATA | verify P36 | verify-all | unittest | inherited_result_sha256 taken over CRLF checkout bytes |
| `papers/P38/results/calculated_curves.csv` | BYTE_ONLY | verify P38 | verify-all | unittest | runner writes CRLF (csv.writer default); git stores LF; values identical after newline normalisation |
| `papers/P38/results/engiproof_reproduction_manifest.json` | ENVIRONMENT_METADATA | verify P38 | verify-all | unittest | python 3.13.5 -> 3.11.15, numpy 2.3.5 -> 2.4.4, input hash of reference/pixel_points.csv (frozen hash = CRLF rendering). result_sha256 entries unchanged |
| `papers/P38/results/independent_work_checks.csv` | BYTE_ONLY | verify P38 | verify-all | unittest | runner writes CRLF (csv.writer default); git stores LF; values identical after newline normalisation |
| `papers/P38/results/reference_comparisons.csv` | BYTE_ONLY | verify P38 | verify-all | unittest | runner writes CRLF (csv.writer default); git stores LF; values identical after newline normalisation |
| `papers/P38/results/table2_check.csv` | BYTE_ONLY | verify P38 | verify-all | unittest | runner writes CRLF (csv.writer default); git stores LF; values identical after newline normalisation |
| `papers/P40/results/table2_reproduction.csv` | BYTE_ONLY | verify P40 | unittest | runner writes CRLF (csv.writer default); git stores LF; values identical after newline normalisation |
| `papers/P41/results/table2_reproduction.csv` | BYTE_ONLY | verify P41 | unittest | runner writes CRLF (csv.writer default); git stores LF; values identical after newline normalisation |
| `papers/P42/results/equation42_continuum_curve.csv` | BYTE_ONLY | verify P42 | unittest | runner writes CRLF (csv.writer default); git stores LF; values identical after newline normalisation |
| `papers/P42/results/phase2_analytical_stress_curves.csv` | NUMERICAL_NONMATERIAL | verify P42 | unittest | floats differ at <=5.4e-16 rel |
| `papers/P42/results/phase3_figure16_literal_probe.csv` | NUMERICAL_NONMATERIAL | verify P42 | unittest | floats differ at <=2.7e-16 rel |
| `papers/P43/results/figure6_first_three_modes_independent.csv` | NUMERICAL_NONMATERIAL | verify P43 | unittest | eigen-solver recompute (numpy.linalg cholesky/eigh); see P43 section |
| `papers/P43/results/figure6_mode1_independent.csv` | NUMERICAL_NONMATERIAL | verify P43 | unittest | eigen-solver recompute (numpy.linalg cholesky/eigh); see P43 section |
| `papers/P43/results/figures4_5_parameter_families.csv` | NUMERICAL_NONMATERIAL | verify P43 | unittest | eigen-solver recompute (numpy.linalg cholesky/eigh); see P43 section |
| `papers/P43/results/phase1_eigen_benchmark_summary.json` | NUMERICAL_NONMATERIAL | verify P43 | unittest | eigen-solver recompute (numpy.linalg cholesky/eigh); see P43 section |
| `papers/P43/results/phase2_full_matrix_summary.json` | NUMERICAL_NONMATERIAL | verify P43 | unittest | eigen-solver recompute (numpy.linalg cholesky/eigh); see P43 section |
| `papers/P43/results/table1_alpha50_beta100_comparison.csv` | NUMERICAL_NONMATERIAL | verify P43 | unittest | eigen-solver recompute (numpy.linalg cholesky/eigh); see P43 section |
| `papers/P43/results/table1_full_matrix_comparison.csv` | NUMERICAL_NONMATERIAL | verify P43 | unittest | eigen-solver recompute (numpy.linalg cholesky/eigh); see P43 section |

Before/after SHA-256 per file: `docs/MUTATION_INVENTORY_v0.2.0.csv`.

## Mechanisms

1. **CRLF output (BYTE_ONLY).** Runners write CSV with `csv.writer`'s default `\r\n` terminator. Git stores LF (`.gitattributes: * text=auto`). On a Windows checkout the bytes match; on Linux every run rewrites the file. `git diff` is empty but `git status` reports it modified.
2. **Checkout-dependent provenance hashes (ENVIRONMENT_METADATA).** P16, P29 (x2), P36 and P38 hash committed text files with `read_bytes()`. Every frozen hash equals the SHA-256 of the **CRLF** rendering, i.e. it was taken on a Windows checkout. A LF checkout of identical content yields a different hash, and the runner writes the new value back.
3. **Environment fields (ENVIRONMENT_METADATA).** P38's reproduction manifest records `python` and `numpy`; any other environment rewrites them.
4. **Floating-point recomputation (NUMERICAL_NONMATERIAL).** P16 and P42 differ at <=5.4e-16 relative. P43's independent FE eigen-solution (`numpy.linalg.cholesky`/`eigh`) differs at ~1e-8 across BLAS/LAPACK builds.

## P43 numerical changes

No text, status, structure, discrepancy or qualification field changes in any environment. Eigenvalues: 1,044 changed entries per environment, max absolute change 3.8e-8 (7.7e-5 of the published 3-decimal half-band 0.0005), **no eigenvalue rounds differently at 3 decimals**. Largest change in any percentage column: 1.2e-6 percentage points. Large *relative* changes (up to 1.9) occur only in columns that are differences of near-equal numbers (e.g. `eq10_error_from_independent_FE_percent`, values ~1e-8, which can change sign). Python 3.12 and 3.13 (both NumPy 2.5.3) agree exactly; every NumPy build differs slightly from every other.

The frozen P43 artifacts do **not record** the Python/NumPy versions that produced them, so the 'before' environment cannot be attributed.

Max absolute / max relative change per column, per recompute environment:

| File | Column / key | 3.10/numpy2.2.6 | 3.11/numpy2.4.4 | 3.12/numpy2.5.3 | 3.13/numpy2.5.3 |
|---|---|---|---|---|---|
| figure6_first_three_modes_independent.csv | `[Y_normalized]` | 3.6e-09 / 2.3e-06 | 5.5e-09 / 1.3e-06 | 5.5e-09 / 1.3e-06 | 5.5e-09 / 1.3e-06 |
| figure6_first_three_modes_independent.csv | `[curvature]` | 4.1e-07 / 3.9e-06 | 5.1e-07 / 1.0e-05 | 5.1e-07 / 9.9e-06 | 5.1e-07 / 9.9e-06 |
| figure6_first_three_modes_independent.csv | `[slope]` | 4.2e-08 / 8.4e-06 | 3.1e-08 / 9.7e-06 | 3.1e-08 / 9.7e-06 | 3.1e-08 / 9.7e-06 |
| figure6_mode1_independent.csv | `[Y_normalized]` | 2.6e-09 / 6.9e-09 | 5.5e-09 / 1.1e-08 | 5.5e-09 / 1.1e-08 | 5.5e-09 / 1.1e-08 |
| figure6_mode1_independent.csv | `[curvature]` | 3.5e-07 / 3.9e-06 | 2.3e-07 / 1.0e-05 | 2.3e-07 / 9.9e-06 | 2.3e-07 / 9.9e-06 |
| figure6_mode1_independent.csv | `[slope]` | 3.0e-08 / 1.2e-06 | 3.1e-08 / 3.1e-06 | 3.1e-08 / 3.1e-06 | 3.1e-08 / 3.1e-06 |
| figures4_5_parameter_families.csv | `[independent_lambda1]` | 1.5e-08 / 3.2e-09 | 2.9e-08 / 9.1e-09 | 3.8e-08 / 1.2e-08 | 3.8e-08 / 1.2e-08 |
| figures4_5_parameter_families.csv | `[independent_lambda2]` | 8.4e-09 / 1.3e-09 | 5.2e-09 / 6.8e-10 | 3.3e-09 / 4.1e-10 | 3.3e-09 / 4.1e-10 |
| phase1_eigen_benchmark_summary.json | `.figure6_independent_mode_shape_check.distance_below_top` | 2.0e-09 / 2.2e-08 | 5.1e-09 / 5.6e-08 | 5.1e-09 / 5.6e-08 | 5.1e-09 / 5.6e-08 |
| phase1_eigen_benchmark_summary.json | `.figure6_independent_mode_shape_check.first_mode_inflection_zeta` | 2.0e-09 / 2.2e-09 | 5.1e-09 / 5.6e-09 | 5.1e-09 / 5.6e-09 | 5.1e-09 / 5.6e-09 |
| phase1_eigen_benchmark_summary.json | `.figure6_independent_mode_shape_check.independent_lambda1` | 2.8e-08 / 4.1e-09 | 3.4e-08 / 5.0e-09 | 3.4e-08 / 5.0e-09 | 3.4e-08 / 5.0e-09 |
| phase1_eigen_benchmark_summary.json | `.table1_independent_FE_comparison.comparisons[].difference` | 4.5e-09 / 2.2e-05 | 8.5e-09 / 4.1e-05 | 9.5e-09 / 4.6e-05 | 9.5e-09 / 4.6e-05 |
| phase1_eigen_benchmark_summary.json | `.table1_independent_FE_comparison.comparisons[].independent_FE_lambda` | 4.5e-09 / 7.5e-10 | 8.5e-09 / 1.4e-09 | 9.5e-09 / 1.6e-09 | 9.5e-09 / 1.6e-09 |
| phase1_eigen_benchmark_summary.json | `.table1_independent_FE_comparison.comparisons[].relative_difference_percent` | 7.5e-08 / 2.2e-05 | 1.4e-07 / 4.1e-05 | 1.6e-07 / 4.6e-05 | 1.6e-07 / 4.6e-05 |
| phase2_full_matrix_summary.json | `.P43_D001_probe.independent_FE_lambda` | 1.8e-10 / 9.8e-12 | 4.0e-10 / 2.2e-11 | 6.3e-11 / 3.5e-12 | 6.3e-11 / 3.5e-12 |
| phase2_full_matrix_summary.json | `.P43_D002_probe.independent_FE_lambda` | 7.8e-10 / 1.2e-10 | 2.3e-09 / 3.5e-10 | 3.7e-09 / 5.6e-10 | 3.7e-09 / 5.6e-10 |
| phase2_full_matrix_summary.json | `.figure6_first_three_modes.summary[].distance_below_top[]` | 2.0e-09 / 2.2e-08 | 5.1e-09 / 5.6e-08 | 5.1e-09 / 5.6e-08 | 5.1e-09 / 5.6e-08 |
| phase2_full_matrix_summary.json | `.figure6_first_three_modes.summary[].independent_lambda` | 2.8e-08 / 4.1e-09 | 3.4e-08 / 5.0e-09 | 3.4e-08 / 5.0e-09 | 3.4e-08 / 5.0e-09 |
| phase2_full_matrix_summary.json | `.figure6_first_three_modes.summary[].inflection_zeta[]` | 2.0e-09 / 2.2e-09 | 5.1e-09 / 5.6e-09 | 5.1e-09 / 5.6e-09 | 5.1e-09 / 5.6e-09 |
| phase2_full_matrix_summary.json | `.table1_full_matrix.max_abs_FE_difference_excluding_source_mismatches` | 4.9e-10 / 9.8e-07 | 3.5e-10 / 7.1e-07 | 2.9e-10 / 5.9e-07 | 2.9e-10 / 5.9e-07 |
| phase2_full_matrix_summary.json | `.table1_full_matrix.max_abs_FE_relative_difference_percent_excluding_source_mismatches` | 3.2e-07 / 2.5e-05 | 9.1e-07 / 7.1e-05 | 1.2e-06 / 9.4e-05 | 1.2e-06 / 9.4e-05 |
| phase2_full_matrix_summary.json | `.table1_full_matrix.max_abs_Table2_error_difference_percentage_points_using_independent_FE` | 2.4e-07 / 2.3e-05 | 2.2e-07 / 2.1e-05 | 7.6e-08 / 7.3e-06 | 7.6e-08 / 7.3e-06 |
| table1_alpha50_beta100_comparison.csv | `[difference]` | 4.5e-09 / 2.2e-05 | 8.5e-09 / 4.1e-05 | 9.5e-09 / 4.6e-05 | 9.5e-09 / 4.6e-05 |
| table1_alpha50_beta100_comparison.csv | `[independent_FE_lambda]` | 4.5e-09 / 7.5e-10 | 8.5e-09 / 1.4e-09 | 9.5e-09 / 1.6e-09 | 9.5e-09 / 1.6e-09 |
| table1_alpha50_beta100_comparison.csv | `[relative_difference_percent]` | 7.5e-08 / 2.2e-05 | 1.4e-07 / 4.1e-05 | 1.6e-07 / 4.6e-05 | 1.6e-07 / 4.6e-05 |
| table1_full_matrix_comparison.csv | `[FE_difference]` | 1.5e-08 / 3.4e-04 | 2.9e-08 / 1.5e-04 | 3.8e-08 / 2.3e-04 | 3.8e-08 / 2.3e-04 |
| table1_full_matrix_comparison.csv | `[FE_relative_difference_percent]` | 3.2e-07 / 3.4e-04 | 9.1e-07 / 1.5e-04 | 1.2e-06 / 2.3e-04 | 1.2e-06 / 2.3e-04 |
| table1_full_matrix_comparison.csv | `[eq10_error_from_independent_FE_percent]` | 3.2e-07 / 1.9e+00 | 9.1e-07 / 1.8e+00 | 1.2e-06 / 1.3e+00 | 1.2e-06 / 1.3e+00 |
| table1_full_matrix_comparison.csv | `[independent_FE_lambda]` | 1.5e-08 / 3.2e-09 | 2.9e-08 / 9.1e-09 | 3.8e-08 / 1.2e-08 | 3.8e-08 / 1.2e-08 |

Every changed value (27,292 rows: environment, file, location, before, after, abs/rel difference) is in `P43_numerical_changes.csv`, delivered separately (not committed).

## P41: VERIFICATION_CONTRACT_DRIFT

`engiproof verify P41` exits 1 because `engiproof/studies/P41/study.json` lists two verification tests that do not exist in `tests/test_p41_engiproof.py`:

| Listed in study.json (missing) | Present in test file (unlisted) |
|---|---|
| `test_inner_force_is_source_review_not_confirmed_paper_discrepancy` | `test_inner_force_is_visually_confirmed_published_mismatch` |
| `test_source_transcription_uncertainty_blocks_promotion` | `test_published_reference_mismatch_blocks_promotion` |

Confirmed as the sole cause: in a scratch copy with only these two names replaced, `verify P41` returns `PASS_SOURCE_EXTERNAL` (10/10 tests; 8/10 before). The frozen repository was not changed. The renamed tests describe a different discrepancy state (source review not confirmed -> visually confirmed published mismatch), so the correction is a source-interpretation decision for the study owner. P41 is outside the live registry, so `verify-all` does not report it.

## Materiality criterion used

NUMERICAL_MATERIAL would require either (a) any non-numeric field to change (status, classification, discrepancy state, qualification, structure), or (b) any value to change when rounded to the precision of its published comparison reference. Neither occurs.
