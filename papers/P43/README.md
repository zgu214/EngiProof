# P43 — Natural Frequencies of Marine Drilling Risers

Phase 1 converts a classic drilling-riser eigenvalue benchmark into callable EngiProof evidence.

## Source model

The source dimensionless eigenproblem is:

`Y'''' - d/dζ[(β + αζ)Y'] - λ^4 Y = 0`

with ball-joint/pinned end conditions. The source solves it by a power series (Eq. 9), but the detailed coefficient procedure is referred to earlier papers and is not repeated.

## Independent method

EngiProof uses cubic Hermite beam elements and the weak form

`∫v''Y'' dζ + ∫(β+αζ)v'Y' dζ = λ^4 ∫vY dζ`

to obtain an independent generalized eigenvalue solution.

This deliberately avoids reproducing hidden source implementation details.

## Phase-1 evidence

- selected Table 1 rows;
- Eq. (10) approximation and Table 2 error check;
- worked-example natural period;
- Figure 6 first-mode inflection-location check;
- no curve digitization;
- qualification `NOT_GRANTED`.
