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
- Final cleanup, owner review of PR #9:
  - PA-24 corrected to 22 failure modes (F1–F22), and the matrix provenance moved to the post-PR #8 state;
  - Appendix A regenerated;
  - version shown as v0.2.1 everywhere;
  - computational-reproducibility paragraph added (Peng 2011; Sandve et al. 2013; Stodden et al. 2018; Collberg & Proebsting 2016; NASEM 2019; Oberkampf & Roy 2010; all DOIs checked against Crossref);
  - acknowledgements TODO removed; acknowledgements will be added at submission.
- No TODO markers remain in the rendered draft.
- §12.3 rewritten per the owner's instruction:
  - Paper2Agent, ScientistOne and ScientistTwo are treated only as contemporary related work, described factually with shared features and differences;
  - no priority, chronology or inspiration claim is made in either direction;
  - they are not engineering validation evidence.

## Technical-prose pass — 28 September 2026 (WORK_QUEUE Q11 step 0)

- Style-only rewrite of §0–§13. List-heavy draft prose is converted into journal paragraphs. The contribution list and the repository-rule list stay as lists; tables and the figure are untouched.
- Guard: `scripts/prose_audit.py` confirms that numbers, citation keys, labels and refs, evidence identifiers, status/class macros, inline mathematics, table bodies and the TikZ figure are unchanged against `develop`.
- An independent semantic review compared old and new text paragraph by paragraph. It found 11 meaning shifts plus 6 borderline wording shifts, all corrected before commit. Its final verdict: no meaning changes.
- Word count 7075 → 6997; the PDF is 18 pages (previously 22), mainly because lists became prose.
- Noted for the later source audit, deliberately left unchanged in this pass:
  - §7 says "graphs of 11--39 nodes", but after the PR #8 graph-sync the P45 graph has 40 nodes. This number needs checking against the current `graph-audit`.

## Journal format — 28 September 2026 (WORK_QUEUE Q11 step 1)

- Converted to Elsevier `elsarticle` (`preprint,12pt`) for Advances in Engineering Software, with numbered Elsevier references (`elsarticle-num`, BibTeX in place of biblatex/biber).
- Front matter:
  - title;
  - author and affiliation;
  - abstract compressed to 236 words (about 250 allowed), keeping all numbers and claims;
  - five highlights, each ≤ 71 characters (limit 85);
  - six keywords.
- Back matter (`sections/14_declarations.tex`): data and code availability, CRediT, competing interests, funding, and the Elsevier generative-AI declaration using Elsevier's template wording. Every author statement is marked **[author to confirm]**.
- Layout only:
  - tables use ragged-right columns with tighter padding;
  - the lifecycle figure is scaled to the text width;
  - Appendix A column widths are adjusted.
- Journal requirements (abstract ≈250 words, 3–5 highlights of ≈85 characters, CRediT, data-availability and competing-interest statements, numbered references) are taken from a secondary summary. The official guide for authors returned HTTP 429 and must be checked before submission.

