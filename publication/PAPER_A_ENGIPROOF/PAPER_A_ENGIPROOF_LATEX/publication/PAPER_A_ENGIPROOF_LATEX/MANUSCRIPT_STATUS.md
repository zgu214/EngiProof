# Manuscript status - Draft v0.1

## Current evidence included

- Framework architecture and evidence classes/statuses.
- P40 propagation-buckling reproduction example and open Eq. (9)/Table 2 mismatch.
- P41 Table 2 force-balance mismatch.
- P41 Eq. (9)/Table 3 axial-bonding classification reproduction.
- P41 Figure 10 paragraph-vs-axis unit mismatch.
- P41 independent elastic bending-stiffness ratio and callable Eq. (14).

## Intentionally not claimed yet

- general extraction accuracy;
- generalization to arbitrary engineering papers;
- fully automatic paper-to-verified or paper-to-qualified engineering;
- independent reproduction of P41 full FE global-buckling response;
- final journal selection.

## Next manuscript checkpoint

After P42 (mechanically different source) reaches a meaningful evidence chain, add a third case subsection and convert the evaluation section from a development plan into a cross-case results section.

## Status update — 27 September 2026

Draft v0.1 still covers P40–P41 only. The evidence base now spans P40–P45 plus non-mutating verification. The post-P45 readiness review (`publication/PAPER_A_ENGIPROOF/PAPER_A_READINESS_REVIEW.md`) gives decision gate B: runtime/method work (gaps G2–G4, human decisions G1, optional deeper P40 work G5), no P46. The manuscript synthesis should follow `publication/PAPER_A_ENGIPROOF/PAPER_A_OUTLINE.md`, which maps each new section to the existing `sections/*.tex` files. Appendix A should be regenerated from `CLAIM_EVIDENCE_MATRIX.md`.


## Draft v0.2 — 28 September 2026 (synthesis over P40–P45)

The draft now follows `publication/PAPER_A_ENGIPROOF/PAPER_A_OUTLINE.md`. It has 13 sections plus two appendices, and the evaluation is organised by capability. The Draft v0.1 files were renamed with history kept (04→04_reproduction, 05→06, 06→09, 07→12, 08→10, 09→13); the rest are new (05, 07, 08, 11). It builds with `latexmk -pdf` (20 pages). The build needs `lmodern` and `biblatex`/`biber`.

- Appendix A is generated from `CLAIM_EVIDENCE_MATRIX.md` with `python scripts/build_claim_appendix.py`.
- Numbers come from repository artifacts: study results, `docs/MUTATION_INVENTORY_v0.2.0.md`, `docs/CROSS_ENVIRONMENT_VERIFICATION.md`, `docs/DISCREPANCY_TAXONOMY.md`, and the recounted manifest statuses (38 comparisons: 14 REPRODUCED, 19 COMPARED, 4 CONDITIONAL, 1 BLOCKED).
- These pending owner decisions are marked in the text:
  - G1 discrepancy decisions (§6.3);
  - G2 taxonomy approval (Table 2 is labelled “proposed”);
  - D-007 cross-environment comparator rules (§8.3);
  - local ingestion summaries for P40–P43 (§3.3).
- Open `\todo`s:
  - related-work citations (Paper2Agent; ScientistTwo / Chain-of-Evidence, as context only; reproducibility literature);
  - complete the P42 author list in `references.bib`;
  - acknowledgements.
- Not claimed: extraction accuracy, completeness, organisational independence, generality beyond offshore/subsea mechanics, autonomous discovery, qualification.

## Draft v0.2.1 — 28 September 2026 (after PR #8)

- Rebased onto `develop` after PR #8 merged.
- Wording updated to the recorded state:
  - eight human decisions in both directions (D-008), with P43 deliberately deferred;
  - reviewer-approved taxonomy labels;
  - D-007 approved;
  - machine-generated ingestion summaries for all six cases;
  - F22 (Windows dispatcher) and the post-fix P45 re-verification;
  - 22 failure modes.
- Appendix A regenerated from the final matrix (20 / 4 / 3 / 3).
- References completed:
  - Paper2Agent (Miao et al., Nature 2026; arXiv:2509.06917);
  - ScientistOne / Chain-of-Evidence (Meng et al., arXiv:2605.26340);
  - ScientistTwo (Nam et al., arXiv:2609.19644);
  - full P42 author list (Lukassen et al. 2019).
- Remaining TODOs: the reproducibility-literature paragraph and acknowledgements.
