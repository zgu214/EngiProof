# P43 Phase 2 — Full eigenvalue matrix and source mismatch

Coverage: 35 alpha-beta rows, 175 eigenvalues, full Table2 Eq10 errors, Figures4-5 parameter families, and independent Figure6 modes 1-3.

## P43-D001
The source Table 1 cell at alpha=0, beta=200, mode 5 visibly prints `13.221`. Independent Eq.8 Hermite-FE and Eq.10 give approximately `18.221`; Table 2 reports zero approximation error for alpha=0.

Classification: `PUBLISHED_REFERENCE_MISMATCH`.

The inferred intended value `18.221` is not substituted into the published record without authoritative confirmation.

Qualification: NOT_GRANTED.

P43-D002: Table 1 alpha=200, beta=100, lambda1 is visibly printed as 6.554. Independent Eq.8 FE gives ~6.654; Eq.10/Table2 internal consistency also supports 6.654. Preserve printed 6.554; inferred correction is not applied.
