# Discrepancy taxonomy (controlled vocabulary)

Status: **proposed mapping awaiting human review** (Paper A gap G2). Source of truth: `engiproof/contracts/contracts.json` → `contracts.discrepancy_taxonomy` and `engiproof/contracts/discrepancy_taxonomy_mapping.json`. This page is a readable copy of both.

**Rule.** A taxonomy label describes the kind of discrepancy and where it was established. It never changes an observation, value, status, decision or qualification, and it does not state a cause.

## Categories (apply in this order; the first rule that holds wins)

| # | Category | Definition | Use when | Not when |
|---|---|---|---|---|
| 1 | `MODEL_VS_EXPERIMENT_GAP` | A model prediction (published or reproduced) differs from measured experimental data reported in the source. | Use when one side of the comparison is a physical measurement. Takes precedence over all other categories. | Both sides are calculations or printed values. |
| 2 | `MODEL_FORM_DIFFERENCE` | Two models, each implemented as published, give different results because of their stated assumptions, kinematics or idealisations. | Use when both models are reproduced or taken as published and the difference is attributable to the stated model form, not to a printed value. | One side is a printed value that the other side contradicts; use NUMERICAL_VALUE_CONFLICT. |
| 3 | `MISSING_OR_INSUFFICIENT_SOURCE_INFORMATION` | The printed equations, parameters or load-case statements are insufficient to determine a published result uniquely, so a source-bounded implementation cannot reconcile with it. | Use when the conflict disappears only by supplying information the source does not give. Do not supply it. | The missing item is only a unit (UNIT_OR_DIMENSION) or a quantity definition (QUANTITY_DEFINITION_OR_CONVENTION). |
| 4 | `UNIT_OR_DIMENSION` | A unit is missing, conflicts between source statements, or makes a stated value dimensionally or physically untenable, while the magnitudes are otherwise consistent under one unit reading. | Use when the conflict is resolved by the choice of unit alone. Takes precedence over NUMERICAL_VALUE_CONFLICT. | The digits themselves disagree under any unit reading. |
| 5 | `QUANTITY_DEFINITION_OR_CONVENTION` | The definition, sign, normalisation, amplitude or reference convention of a quantity (or of a quantitative claim) is ambiguous or used inconsistently; the numbers reconcile under one reading only. | Use when the printed numbers are reproduced under one stated reading and contradicted under another. | No reading reconciles the numbers. |
| 6 | `NOTATION_OR_TYPOGRAPHY` | A printed symbol, operator or equation text contradicts the surrounding text or neighbouring equations, without a conflicting numerical value. | Use when the contradiction is in notation only. No cause (typesetting, author error) is asserted. | A numerical value is affected; use NUMERICAL_VALUE_CONFLICT. |
| 7 | `PRECISION_OR_DIGITIZATION_RESIDUAL` | A difference between a published value and a reproduction that lies within, or is attributable to, the published rounding precision or the uncertainty of graphical digitization. | Use when the difference does not exceed the recorded rounding band or digitization uncertainty. Usually BOUNDED. | The difference exceeds the recorded band; use NUMERICAL_VALUE_CONFLICT. |
| 8 | `NUMERICAL_VALUE_CONFLICT` | A printed numerical value disagrees, beyond its stated precision, with another source statement of the same quantity or with a source-bounded reproduction or independent check of it. | Use when the same quantity has two incompatible values (printed vs printed, or printed vs recomputed). | No other value of the same quantity exists and the conflict is only with physics; use PHYSICAL_IMPLAUSIBILITY. |
| 9 | `PHYSICAL_IMPLAUSIBILITY` | A printed value or trend is contradicted by basic mechanics applied to other source data, while no other source statement gives a conflicting value of the same quantity. | Use when the conflict is established only through physical bounds (equilibrium, buoyancy, material strength, weight support). | Another printed or recomputed value of the same quantity exists; use NUMERICAL_VALUE_CONFLICT. |

## Loci (list every locus through which the discrepancy was established)

| Locus | Meaning |
|---|---|
| `WITHIN_SOURCE` | Two or more statements of the source (paragraph, table, figure axis, caption, equation) disagree with each other. |
| `SOURCE_INCOMPLETE` | A single source statement lacks information needed to interpret or reproduce it (e.g. a missing unit or parameter). |
| `SOURCE_VS_REPRODUCTION` | A published value differs from EngiProof's PUBLISHED-class implementation of the source's own method. |
| `SOURCE_VS_INDEPENDENT` | A published value differs from an INDEPENDENT-class check (different formulation, numerical method or measurement). |
| `SOURCE_VS_PHYSICAL_BOUNDS` | The conflict is established by basic mechanics applied to other source data. |
| `MODEL_VS_MODEL` | Two models, each as published, are compared. |
| `MODEL_VS_EXPERIMENT` | A model is compared with measured data. |

## Proposed mapping of the P40–P45 records

The legacy `classification_hint` in each study manifest is unchanged. Nothing takes effect until a reviewer records an approval.

| Discrepancy | Legacy hint | Proposed category | Proposed loci | Rationale | Review |
|---|---|---|---|---|---|
| P40-D001 | PUBLISHED_REFERENCE_MISMATCH | `NUMERICAL_VALUE_CONFLICT` | SOURCE_VS_REPRODUCTION, SOURCE_VS_INDEPENDENT | The same quantity has a printed value (0.66) and a recomputed value (0.7057) beyond the two-decimal rounding band; the independent work balance agrees with the recomputation. | PROPOSED |
| P41-D001 | PUBLISHED_REFERENCE_MISMATCH | `NUMERICAL_VALUE_CONFLICT` | WITHIN_SOURCE, SOURCE_VS_REPRODUCTION | Printed components (153 + 312) do not sum to the printed total (471); Eqs. (6)-(8) give a different inner increment (158.8). | PROPOSED |
| P41-D002 | PUBLISHED_REFERENCE_MISMATCH | `UNIT_OR_DIMENSION` | WITHIN_SOURCE | The magnitudes (300, 850) are consistent with the plotted scale; the conflict is resolved by the unit alone, which is the UNIT_OR_DIMENSION rule and takes precedence over NUMERICAL_VALUE_CONFLICT. | PROPOSED |
| P42-D001 | MODEL_FORM_KINEMATICS_DIFFERENCE | `MODEL_FORM_DIFFERENCE` | MODEL_VS_MODEL | Both models are as published; the source attributes the Fz dependence to model kinematics. No printed value is contradicted. | PROPOSED |
| P42-D002 | SOURCE_IMPLEMENTATION_PROVENANCE_GAP | `MISSING_OR_INSUFFICIENT_SOURCE_INFORMATION` | SOURCE_VS_REPRODUCTION, SOURCE_INCOMPLETE | A literal implementation does not reconcile with Figure 16; the printed equations and load case do not fix the contact-pressure/interface convention. The legacy label is already of this kind. | PROPOSED |
| P43-D001 | PUBLISHED_REFERENCE_MISMATCH | `NUMERICAL_VALUE_CONFLICT` | WITHIN_SOURCE, SOURCE_VS_REPRODUCTION, SOURCE_VS_INDEPENDENT | Printed eigenvalue vs recomputed 18.221 (published Eq. (10) and independent FE) and vs Table 2. | PROPOSED |
| P43-D002 | PUBLISHED_REFERENCE_MISMATCH | `NUMERICAL_VALUE_CONFLICT` | WITHIN_SOURCE, SOURCE_VS_INDEPENDENT | Printed eigenvalue vs independent FE 6.654; Table 2 error is consistent only with 6.654. | PROPOSED |
| P44-D001 | SOURCE_FIGURE_TEXT_MISMATCH | `NUMERICAL_VALUE_CONFLICT` | WITHIN_SOURCE | The same time labels have two incompatible printed values. The legacy label SOURCE_FIGURE_TEXT_MISMATCH described the locus, not the kind. | PROPOSED |
| P45-D001 | SOURCE_INTERNAL_INCONSISTENCY | `PHYSICAL_IMPLAUSIBILITY` | SOURCE_VS_PHYSICAL_BOUNDS, WITHIN_SOURCE | No other printed value of the buoyed weight exists; the conflict is established by buoyancy applied to the source geometry. | PROPOSED |
| P45-D002 | SOURCE_MAGNITUDE_IMPLAUSIBILITY | `PHYSICAL_IMPLAUSIBILITY` | SOURCE_VS_PHYSICAL_BOUNDS | The printed tensions imply 662/1141 MPa axial stress and 6-23 times the submerged weight; no other printed value of these tensions exists. The decimal-grouping explanation is not asserted. | PROPOSED |
| P45-D003 | SOURCE_UNIT_AMBIGUITY | `UNIT_OR_DIMENSION` | SOURCE_INCOMPLETE, SOURCE_VS_PHYSICAL_BOUNDS | No unit is printed; only a unit of order 10 kN supports the riser weight. No unit is asserted. | PROPOSED |
| P45-D004 | SOURCE_EQUATION_TEXT_MISMATCH | `NOTATION_OR_TYPOGRAPHY` | WITHIN_SOURCE | Notation contradicts the stated period; no printed numerical value is in conflict. No cause is asserted. | PROPOSED |
| P45-D005 | SOURCE_CONVENTION_AMBIGUITY | `QUANTITY_DEFINITION_OR_CONVENTION` | WITHIN_SOURCE, SOURCE_VS_INDEPENDENT | The figures reconcile with peak-to-peak and not with single amplitude; the source uses both readings of 'amplitude'. | PROPOSED |
| P45-D006 | SOURCE_CLAIM_DEFINITION_AMBIGUITY | `QUANTITY_DEFINITION_OR_CONVENTION` | WITHIN_SOURCE | The claim is reproduced only when read as peak absolute stress, not per envelope. | PROPOSED |

Effect of the proposal: ten legacy labels over 14 records collapse to seven categories. The three similar cases named in `PAPER_A_GAPS.md` G2 become consistent:
- P41-D002 (paragraph MNm vs axis kNm) and P45-D003 (no unit printed) are both `UNIT_OR_DIMENSION`, with different loci.
- P44-D001 (paragraph vs caption times) is `NUMERICAL_VALUE_CONFLICT` / `WITHIN_SOURCE`.

The legacy label named the locus, not the kind of conflict.

Points a reviewer may want to decide differently:
- **P45-D001:** `PHYSICAL_IMPLAUSIBILITY` rather than the legacy internal inconsistency. The conflict is established through buoyancy applied to Figure 3 geometry, not by a second printed weight.
- **P41-D002:** unit precedence over numerical conflict.
- **P43-D002:** whether `SOURCE_VS_REPRODUCTION` should be added alongside `SOURCE_VS_INDEPENDENT`.

Not mapped: P16-D001, P29-D001, P36-D001, P38-D001 and P38-D002 are outside the Paper A population and have no classification hint. `engiproof discrepancy-taxonomy` reports them as `UNMAPPED`.

## Reviewing

```
engiproof discrepancy-taxonomy [Pxx]                  # audit: legacy, proposed, approved labels
engiproof taxonomy-review P45 P45-D004 --decision APPROVED --reviewer "<name>" --note "<why>"
engiproof taxonomy-review P45 P45-D001 --decision APPROVED --reviewer "<name>" --note "<why>" \
    --category NUMERICAL_VALUE_CONFLICT --locus WITHIN_SOURCE    # approve with a different label
```

Reviews are appended to the mapping file; the latest review decides the effective label.

Approving a label does not rewrite `classification_hint` in the study manifest. `papers/P40|P41/results/discrepancy_assessment.json` are frozen evidence derived from the hint, so replacing hints would require an explicit `engiproof regenerate`. That is a separate human-approved step.

`validate_study_manifest` now rejects any `classification_hint` that is neither a taxonomy category nor a registered legacy hint. It also validates an optional per-discrepancy `taxonomy: {category, loci}` field.
