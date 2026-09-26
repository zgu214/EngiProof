# P40 — Propagation Buckling in Subsea Pipe-in-Pipe Systems

EngiProof v0.2.0 ingestion-generated engineering study.

## Current evidence state

`CONDITIONAL`

Selected source targets:

- Table 1 — source input properties;
- Equation (9) — modified PIP analytical propagation-pressure expression;
- Table 2 — normalized analytical / experimental / RST / FE comparison.

## Reproduction result

Eqs. (2), (3), and (6) reproduce their Table 2 normalized ratios within the two-decimal source precision. Eq. (9) reproduces PIP-1 and PIP-2 to source rounding.

For PIP-3:

- direct Eq. (9): approximately `0.705666` normalized by `Pp2`;
- source Table 2: `0.66`;
- independent Eq. (8a-d) work-balance reconstruction: approximately the same as direct Eq. (9), with less than 0.1% difference caused by the source rounding reduction (`0.626` / `2.515`).

The PIP-3 discrepancy remains `OPEN`. No parameter is tuned to force agreement.

## Commands

```bat
engiproof verify P40
engiproof run P40
engiproof tool P40 table2_reproduction_summary --params "{}"
engiproof tool P40 equation9_pressure_kPa --params "{\"Do\":80,\"to\":3,\"Di\":40,\"ti\":1.6,\"sigma_Yo_MPa\":209,\"sigma_Yi_over_sigma_Yo\":0.75}"
```

The source PDF remains external. Engineering qualification is `NOT_GRANTED`.
