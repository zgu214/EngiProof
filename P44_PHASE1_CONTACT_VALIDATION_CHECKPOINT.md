# P44 Phase 1 — Contact validation checkpoint

## Reproduced source-bounded mechanics

- Drillpipe OD/ID independently reconstruct Table 1 cross-sectional area and second moment.
- Equation (1) printed arithmetic:
  `30 * 19.5 * 0.847 * 0.866 = 429.09867 lb`, matching the published 429.098 lb.
- Exact `sin(60°)` gives `429.11126 lb`, essentially identical to the published FEM value `429.11 lb`.
- `5.8 s / 10 = 0.58 s`, reproducing the published time-slice spacing.
- With published `K1 = 1e6 lbf/ft`, 429.11 lb corresponds to only ~0.00515 in elastic penetration.

## P44-D001

The paragraph introducing Figures 7 and 8 states 4.06 s and 2.32 s.  
The Figure 7 and 8 captions state 0.58 s and 1.74 s.  
Figure 2 also uses 0.58 s and 1.74 s.

Classification: `SOURCE_FIGURE_TEXT_MISMATCH`.

No silent correction is applied.

## Boundary

The complete nonlinear FE contact profiles are not reproduced because the source does not provide the full time-dependent wall geometry, well trajectory, RAO/environmental coefficient data, and exact contact implementation needed for a faithful reconstruction.

Qualification: NOT_GRANTED.
