# EngiProof discrepancy automation — v0.2.0-dev3

The discrepancy engine converts recorded differences into conservative review/escalation metadata. It does **not** decide whether a difference is physically acceptable and it never grants engineering qualification.

## CLI

```bat
engiproof discrepancy-audit P40
engiproof assess-discrepancies P40
engiproof discrepancy-gate P40
engiproof discrepancy-audit-all
```

`promotion_effect` is `NONE`, `REVIEW_REQUIRED`, or `BLOCK_PROMOTION`. An unresolved blocking discrepancy prevents a new study from entering the live registry. Existing live `CONDITIONAL` studies are not retroactively demoted.

P40-D001 is the first real blocking case: direct Eq. (9) reproduction gives 0.705666 versus published 0.66, beyond the two-decimal rounding band, while an independent Eq. (8a-d) reconstruction corroborates the reproduced value. The engine records this as `PUBLISHED_REFERENCE_MISMATCH`, HIGH, `BLOCK_PROMOTION`; it does not declare the paper wrong and does not tune inputs.
