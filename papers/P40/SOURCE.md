# P40 source contract

**Paper:** Propagation Buckling in Subsea Pipe-in-Pipe Systems  
**Year:** 2017  
**DOI:** `10.1061/(ASCE)EM.1943-7889.0001337`  
**Canonical local PDF:** `p40-karampour2017.pdf`  
**Expected local SHA-256:** `e83902ba46b8e713ddf2f11f5953bdf318ac539f6701ff303651e28d3d5e28bb`

## Selected targets

- Table 1 — Properties of PIP Systems.
- Table 2 — Hyperbaric chamber / analytical / RST / FE comparison.
- Equation (9) — modified analytical PIP propagation-pressure expression.

Supporting source equations used for verification: Eqs. (2), (3), (6), and (8a-d).

## Source-reviewed Eq. (9)

Using source notation,

`Ptilde_p2 = [3*pi*sigma_Yo/2.515 * (to/Do)^2] * [1 + (sigma_Yi/sigma_Yo)*(ti/to)^2] * [1/(1 - (Di/(2*Do))^2)]`

The source explicitly states that setting `Di = ti = 0` reduces Eq. (9) to Eq. (6).

## Evidence boundary

The source PDF is external and is not redistributed. Table 1 and Table 2 numerical reference values are retained as source-bounded machine-readable data. The direct Eq. (9) implementation is `PUBLISHED` evidence. The separate work-balance reconstruction from Eqs. (8a-d) is `INDEPENDENT` evidence.

## Open discrepancy

For PIP-3, direct Eq. (9) evaluation using the Table 1 inputs yields a normalized `Ptilde_p2/Pp2` ratio of approximately `0.7057`, while Table 2 reports `0.66`. PIP-1 and PIP-2 reproduce the published ratios to rounding. The mismatch is retained as an open source/comparison discrepancy; parameters must not be tuned to remove it.

Engineering qualification is **NOT_GRANTED**.
