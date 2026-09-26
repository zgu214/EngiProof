# P40 reproduction checkpoint — EngiProof v0.2.0-dev2

Date: 2026-09-26

## Outcome

P40 has crossed from structural readiness into deterministic source-bounded reproduction.

Implemented:

- source-reviewed Table 1 machine-readable inputs;
- source-reviewed Table 2 comparison values;
- published Eqs. (2), (3), (6), and (9);
- independent work-balance reconstruction from Eqs. (8a-d);
- deterministic Table 2 reproduction CSV;
- explicit open-discrepancy record;
- evidence graph;
- callable tools;
- automated tests.

## Numerical evidence

Supporting Eqs. (2), (3), and (6) reproduce source Table 2 ratios within 0.01 absolute ratio (two-decimal source precision).

Eq. (9):

- PIP-1: calculated `0.863474`; source `0.86`;
- PIP-2: calculated `0.690022`; source `0.69`;
- PIP-3: calculated `0.705666`; source `0.66`.

The PIP-3 absolute ratio difference is `0.045666` (about `6.92%` relative to the published 0.66 value).

The independent work-balance reconstruction from Eqs. (8a-d) agrees with direct Eq. (9) within `0.1%` for all three cases. This supports the implemented mechanics but does not resolve the PIP-3 source-table mismatch.

## Status

- evidence status: `CONDITIONAL`;
- discrepancy `P40-D001`: `OPEN`;
- FE reproduction: not performed;
- engineering qualification: `NOT_GRANTED`;
- live registry promotion: intentionally deferred until local user review.
