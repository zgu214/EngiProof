# P41 Phase 2 — axial bonding criterion and Table 3

## Source-confirmed Table 2 mismatch

The original PDF visibly reports:
- fS = 471 N/m
- inner ΔS = 153 N/m
- outer ΔS = 312 N/m

The components sum to 465 N/m, whereas Eq. (8) requires 471 N/m.
Independent Eqs. (6)-(7) evaluation gives approximately 158.8 and 312.2 N/m.

Classification: `PUBLISHED_REFERENCE_MISMATCH`, OPEN.
The possible `153 -> 159` typo is plausible but unconfirmed.

## Eq. (9) / Table 3

With gamma_f=1.0 for the paper's illustrative Table 3 classification, the full-bonding threshold is approximately 158.78 N/m.

The Table 3 case types are independently reproduced:
- Case 1, 0 N/m -> NO_FRICTION
- Case 2, 87.5 N/m -> PARTIAL_BONDING
- Case 3, 175 N/m -> FULL_BONDING
- Case 4, 358 N/m -> FULL_BONDING

The source dry-friction estimate also checks:
`1195 N/m * 0.3 = 358.5 N/m`, consistent with the rounded source value 358 N/m.

## Eq. (10)

Eq. (10) is implemented as a callable published relationship.
Direct reproduction of the published 1.305 m full-bonding end expansion is not claimed because the source does not explicitly provide all numerical inputs needed to independently reconstruct S0_total from Eqs. (4)-(5) without assumptions.
