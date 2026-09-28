# G1 — Human discrepancy decision candidates

Prepared 27 September 2026 for the study owner. **No decision has been recorded.** Each candidate below is a proposal to accept, change or reject. The agent does not record RESOLVED, BOUNDED or ACCEPTED_WITH_RATIONALE decisions. Qualification stays NOT_GRANTED whatever is decided. Decisions are appended to `engiproof/studies/<ID>/discrepancy_decisions.json` and never change the discrepancy record, its observation or any evidence value.

**Why this is needed (PA-14).** The only real decision on record is P40-D001 `DEFERRED`. Paper A needs to show the boundary in both directions:
- an unblocking decision with a rationale and evidence references, and the promotion gate responding to it;
- a deliberate DEFERRED decision that keeps promotion blocked.

**Gate effects** were computed by dry-run on a temporary copy of the repository (`discrepancy_gate` / `promotion_gate`). In this environment the P41/P43 intakes are absent, so their promotion gate also reports “source identity not audited / readiness not assessed”. Those items are independent of the decisions, and they may read differently on the machine that holds the intakes.

## Candidates

### C1 — P45-D004 · printed `sin(2πt/g)` vs the stated 9 s period

| | |
|---|---|
| Record | OPEN, legacy `SOURCE_EQUATION_TEXT_MISMATCH`, proposed taxonomy `NOTATION_OR_TYPOGRAPHY` |
| Evidence | The sentence before the equation states a 9 s period and 7.70 m amplitude. The tension equation on the same page uses `2πt/9`. The tool uses the text period and preserves the printed equation (`papers/P45/reference/example_1200m_inputs.json`, `S(P45).discrepancies`). |
| Proposed disposition | **ACCEPTED_WITH_RATIONALE** |
| Rationale option A | “Notation-only conflict. The period is stated explicitly in the text and in the companion tension equation. The implementation uses the stated 9 s; the printed equation is preserved unchanged in the record.” |
| Rationale option B | DEFERRED — if the reviewer wants an erratum before accepting any reading of a printed equation. |
| Gate effect | P45 blockers 6 → 5. P45 stays blocked (D001–D003, D005, D006; readiness PARTIAL). |
| Evidence refs to cite | `papers/P45/reference/example_1200m_inputs.json`, `engiproof/studies/P45/study.json#P45-D004` |

### C2 — P41-D002 · paragraph “MNm” vs Figure 10 axis “kNm”

| | |
|---|---|
| Record | OPEN, legacy `PUBLISHED_REFERENCE_MISMATCH`, proposed `UNIT_OR_DIMENSION` |
| Evidence | The paragraph values (~300 and ~850) sit on the plotted 0–1000 scale labelled kNm; a literal MNm reading is three orders of magnitude off. The EngiProof comparison uses the plotted axis (`S(P41)` Phase 3). |
| Proposed disposition | **ACCEPTED_WITH_RATIONALE** |
| Rationale option A | “For comparison with Figure 10, the plotted axis unit (kNm) governs: it is consistent with the plotted scale and with the reproduced moments. The paragraph unit is preserved as a recorded source inconsistency and is not corrected.” |
| Rationale option B | DEFERRED — if the reviewer does not want any comparison to depend on choosing between the two source statements. |
| Gate effect | P41 blockers 2 → 1. P41 stays blocked by P41-D001 (force balance 153 + 312 ≠ 471). |
| Evidence refs | `papers/P41/results/phase3_global_buckling_summary.json`, `engiproof/studies/P41/study.json#P41-D002` |

### C3 — P43-D001 and P43-D002 · printed eigenvalues vs internal consistency

| | |
|---|---|
| Record | Both OPEN, legacy `PUBLISHED_REFERENCE_MISMATCH`, proposed `NUMERICAL_VALUE_CONFLICT` |
| Evidence | D001: printed λ5 = 13.221, while the independent Eq. (8) FE and Eq. (10) give ≈ 18.221, and Table 2 reports zero error for α = 0. D002: printed λ1 = 6.554, while FE gives ≈ 6.654, and Table 2’s 1.39 % error is consistent only with 6.654. |
| Proposed disposition | **ACCEPTED_WITH_RATIONALE** (for both), or DEFERRED |
| Conflict to resolve first | The records’ own `closure_requirements` say “Resolve only with authoritative erratum/author clarification”. ACCEPTED_WITH_RATIONALE is not RESOLVED, but it does unblock promotion, so the reviewer should confirm that accepting is consistent with those requirements. If not, choose DEFERRED. |
| Rationale option A | “The printed value is retained as the published record and is not substituted. Promotion may proceed with the discrepancy explicitly accepted. Three independent internal checks (independent FE, Eq. (10), Table 2 error column) agree with each other and not with the printed value.” |
| Rationale option B | DEFERRED pending an erratum search (SPE-5620-PA). |
| Gate effect (both accepted) | P43 discrepancy gate becomes ready (2 → 0 blockers). Promotion still requires the ingestion items. P43 would be the first Paper A study whose discrepancy gate is cleared by recorded human decisions. |
| Evidence refs | `papers/P43/results/table1_full_matrix_comparison.csv`, `papers/P43/results/phase2_full_matrix_summary.json` |

### C4 — P44-D001 · paragraph times (4.06 s / 2.32 s) vs captions (0.58 s / 1.74 s)

| | |
|---|---|
| Record | OPEN, legacy `SOURCE_FIGURE_TEXT_MISMATCH`, proposed `NUMERICAL_VALUE_CONFLICT` |
| Proposed disposition | **DEFERRED** — a deliberate non-unblocking decision |
| Rationale | “Two incompatible printed time pairs. Figure 2 supports the captions, but the full FE contact profiles are not reproduced, so no EngiProof evidence can arbitrate. Keep blocked pending author clarification.” |
| Gate effect | None: P44 stays blocked. It shows that a recorded decision can deliberately keep the block. |

### C5 (optional) — P16-D001 and P36-D001 · formalise the BOUNDED manifest status

Both are BOUNDED in the manifest and already have no promotion effect, but there is no recorded decision. Recording **BOUNDED** with the existing evidence (P16 max graph–table difference 0.917 mm; P36 in-sample residual mean 1.75 % / max 3.59 %) would give them an audit trail. The gate is unchanged.

## Commands (the reviewer runs these; the reviewer's name is required)

```
engiproof discrepancy-decide P45 P45-D004 --disposition ACCEPTED_WITH_RATIONALE --reviewer "<name>" --rationale "<chosen text>" --evidence-ref papers/P45/reference/example_1200m_inputs.json
engiproof discrepancy-decide P41 P41-D002 --disposition ACCEPTED_WITH_RATIONALE --reviewer "<name>" --rationale "<chosen text>" --evidence-ref papers/P41/results/phase3_global_buckling_summary.json
engiproof discrepancy-decide P43 P43-D001 --disposition <ACCEPTED_WITH_RATIONALE|DEFERRED> --reviewer "<name>" --rationale "<chosen text>" --evidence-ref papers/P43/results/table1_full_matrix_comparison.csv
engiproof discrepancy-decide P43 P43-D002 --disposition <ACCEPTED_WITH_RATIONALE|DEFERRED> --reviewer "<name>" --rationale "<chosen text>" --evidence-ref papers/P43/results/table1_full_matrix_comparison.csv
engiproof discrepancy-decide P44 P44-D001 --disposition DEFERRED --reviewer "<name>" --rationale "<chosen text>"
engiproof discrepancy-gate <ID>      # then: engiproof promotion-gate <ID>; engiproof graph-sync <ID>; engiproof graph-audit <ID>
```

After decisions are recorded, the agent can do the evidence sync (graph-sync/audit, handover and Paper A matrix PA-14) and open a PR.

## Outcome — recorded 28 September 2026 (D-008)

The owner (Zhiqiang Gu) approved the following, and they were recorded with his rationales:

| Candidate | Decision recorded | Gate effect (before → after) |
|---|---|---|
| P45-D004 | ACCEPTED_WITH_RATIONALE | P45 blockers 6 → 5 |
| P41-D002 | ACCEPTED_WITH_RATIONALE | P41 blockers 2 → 1 |
| P43-D001, P43-D002 | **DEFERRED**, per the recorded closure requirements; not accepted to clear the gate | P43 unchanged (2 blockers) |
| P44-D001 | DEFERRED | P44 unchanged (1 blocker) |
| P16-D001, P36-D001 | BOUNDED, formalising the existing status (P36 is in-sample, not held-out) | Unchanged (already ready) |

- Decision files: `engiproof/studies/{P16,P36,P41,P43,P44,P45}/discrepancy_decisions.json`.
- Before/after gate evidence and graph audits: `G1_GATE_EVIDENCE.json`.
- Qualification remains NOT_GRANTED.
