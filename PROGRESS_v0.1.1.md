# EngiProof v0.1.1 progress

Checkpoint: 25 September 2026

## Completed in P38 integration batch

- Added versioned generic Study, Source, Evidence, Comparison, Discrepancy and Verification contracts.
- Added P38 as the first complete evidence-chain study.
- Preserved inherited P38 numerical evidence byte-for-byte for:
  - `reference_comparisons.csv`
  - `calculated_curves.csv`
  - `table2_check.csv`
  - `independent_work_checks.csv`
  - `summary.json`
- Added public-safe P38 reproduction: source PDF/raster assets remain external; SHA-256/source contract retained.
- Added evidence graph, comparison records, discrepancy records and provenance query.
- Added CLI: `schema`, `evidence`, `compare`, `discrepancy`, `provenance`.
- P08/P12 schema/tool behavior retained.
- Full local suite: 19 tests passed.
- `verify-all`: PASS; P08/P12/P38 return `PASS_SOURCE_EXTERNAL` when copyrighted PDFs are absent.

## P38 evidence disposition

- Figure 10(a): `COMPARED`
- Figure 10(b): `COMPARED`
- Figure 11(a): `CONDITIONAL`
- Figure 11(b): `CONDITIONAL`
- Table 2 arithmetic: `COMPARED`
- Direct work balance: independent mathematical `VERIFIED` check
- Engineering qualification: `NOT_GRANTED`

## Next authorized work

1. Run this batch on the user's Windows develop branch and confirm CI.
2. Integrate the next source-ready study, preferably P16/P29/P36, without weakening evidence boundaries.
3. Only after several heterogeneous studies use the contracts, stabilize schema naming for v0.2.0.


## Source-ready heterogeneous study batch

Integrated from `PiP_Library_PublicationRepair_2026-09-25.zip`
(SHA-256 `36550d395a323af6788ae4bc59c6e1725cdd5711e862048ab312bf424dac8a15`) without redistributing source PDFs/raster figures.

- **P16** `COMPARED`: Figure 5 vector curve vs cumulative Table 2 walking increments.
  - 261 source-curve vertices retained.
  - six printed cycle increments retained.
  - maximum graph-minus-table endpoint difference: 0.917245 mm.
  - no independent walking solver claimed.
- **P29** `CONDITIONAL`: independent Eq. (1)/(16)-(18) response evaluation.
  - 7,442 surface points retained.
  - state-space covariance and direct transfer quadrature cross-check at six cases.
  - inherited maximum cross-check relative difference: 1.070e-13.
  - factor-of-two positive-frequency/two-sided source convention remains `OPEN`.
- **P36** `COMPARED`: Eq. (8) against 27 extracted Figure 14 FE symbol centres.
  - mean absolute graphical residual: 1.748597%.
  - maximum absolute graphical residual: 3.585742%.
  - in-sample source fit audit only; no new FE prediction.

Local regression after this batch: **28 tests PASS** and `verify-all = PASS`.

## Next

1. Clean accidental shell-output files (`Current`, `Detected`, `Downloading`, `Future`, `Resolved`, `Updating`) from `develop` if still tracked.
2. Push the P16/P29/P36 batch and confirm GitHub CI.
3. Select the next source-ready heterogeneous study only after checking source availability and evidence boundary.
