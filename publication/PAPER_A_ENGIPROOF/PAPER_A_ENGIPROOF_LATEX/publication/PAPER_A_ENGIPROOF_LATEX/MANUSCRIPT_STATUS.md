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


## Tables from repository data and final source audit — 28 September 2026 (WORK_QUEUE Q11 steps 2–3)

Tables (step 2):
- `scripts/build_tables.py` generates `generated/tab_evidence_by_study.tex` (new Table `tab:evidence` in §9), `generated/tab_crossenv.tex` (§8 table body, rows identical to the previous hand-written rows) and `generated/facts.json`. `--check` fails if any generated file is stale.
- The evidence-graph node count and coverage are taken from `audit_evidence_graph`, not from the tracked file.

Automated facts check (step 3):
- `scripts/check_manuscript_facts.py` rebuilds 19 prose phrases from `generated/facts.json` and requires each to occur verbatim: comparison counts, discrepancy counts, readiness, taxonomy counts, decision counts, graph node range, cross-environment result, failure-mode count, evidence status and qualification. Result after the owner decisions: 20 PASS, 0 FAIL, 0 OPEN (a check on the §2 qualification field was added). A mutation test (reverting 11--40 to 11--39) makes it fail as intended.

Independent source audit: a separate agent checked about 125 further statements against the study manifests, results, decision logs, taxonomy mapping, failure register and references. About 115 were confirmed. The findings and their handling:

| ID | Location | Finding | Handling |
|---|---|---|---|
| SA-1 | §7 | "11--39 nodes"; the P45 graph has 40 nodes since commit 2a57f27 (decision node P45-D004 added) | Corrected to "11--40 nodes" |
| SA-2 | §2, Fig. 1, §11, abstract | "qualification NOT_GRANTED for all six / every manifest, result artifact and graph". `engiproof/studies/P44/study.json` has no `qualification` field (only limitation text says NOT_GRANTED). The framework default `NOT_CLAIMED` is therefore written to `engiproof/studies/P44/evidence_graph.json`. Three result files carry no qualification field: `papers/P41/results/phase3_global_buckling_summary.json`, `papers/P42/results/phase1_summary.json`, `papers/P42/results/phase2_analytical_stress_summary.json` **Resolved (D-009, option a):** field added to the P44 manifest; graph resynced (NOT_GRANTED, 16/16, audit PASS). The three result files are unchanged, and §11 now reads "every result artifact that carries a qualification field" |
| SA-3 | §4 table, §4 text, §9 | "Agreement to the two-decimal table precision for all ratios except Eq. (9), PIP-3". P40-C001 records a maximum difference of 0.00546: Eq. (6), PIP-1 gives 0.5655 against a printed 0.56, just outside the ±0.005 rounding band. `papers/P40/README.md` makes the same "within source precision" statement **Resolved (D-009):** no new discrepancy. Wording in §4 (table and text), §9, `papers/P40/README.md` and the PA-06 evidence note changed to "close agreement … maximum absolute ratio difference 0.00546; Eq. (6), PIP-1 marginally outside the strict two-decimal rounding interval". P40-D001 unchanged |
| SA-4 | §4 table, P40 row | Status given as COMPARED; the row also covers P40-C003, which is CONDITIONAL | Corrected to COMPARED / CONDITIONAL |
| SA-5 | §4 table, P41 row | Status given as REPRODUCED / COMPARED, with "reproduced" in the text. The row's records are C001, C002, C004 (COMPARED) and C003 (CONDITIONAL); "four bonding categories" are really four cases in three categories | Corrected to COMPARED / CONDITIONAL, "agree", and "four … bonding classifications" |
| SA-6 | §9 | "six discrepancies of five kinds"; the taxonomy gives P45 four categories | Corrected to "four kinds" |
| SA-7 | §6 | Approvals said to be recorded in `docs/DISCREPANCY_TAXONOMY.md`; the append-only reviews are in `engiproof/contracts/discrepancy_taxonomy_mapping.json` | Corrected: mapping file named, the .md file named as the documentation |
| SA-8 | §3 | Manual review stated to be required "because the DOI does not appear in the source text". P44 also has DOI NOT_FOUND_IN_SOURCE, yet its audit passes | Causal clause replaced by the recorded checks |
| SA-9 | §8 | F22 said to be exposed by "the same cross-platform work"; the register records a local Windows batch run | Reworded to "A local Windows run during the same work" |
| SA-10 | abstract | "independent formulations decide the direction of five numerical conflicts" (PA-09: P40-D001, P41-D001, P43-D001/D002, P45-D001). P45-D001 is categorised PHYSICAL_IMPLAUSIBILITY, and P41-D001's recorded support is CORROBORATES_REPRODUCTION (published Eqs. (6)–(8) plus the printed total) **Resolved (D-009):** now "independent checks and source-consistency checks clarify five source conflicts" |
| — | §5, §6, §9 (P43-D002) | The auditor questioned "three consistent checks": Eq. (10) alone gives 6.746, and it is consistent with the FE result 6.654 only through the 1.39% error in Table 2 | No change: this matches the recorded basis `EQ8_FE_PLUS_EQ10_PLUS_TABLE2_INTERNAL_CONSISTENCY` |
| — | §3 | "not determined, because the matching PDF was not available" | No change: `ingestion_summary.py` writes NOT_RECORDED with no note only when no PDF is found |

- No numerical result, evidence record, discrepancy, decision, taxonomy label or qualification was changed.

## Author declarations — 28 September 2026

- Confirmed by the author: affiliation (Independent researcher, Norway), CRediT roles, competing interests (none), funding (no specific grant). All [author to confirm] markers are removed, together with the `\authorconfirm` macro.
- Generative-AI declaration replaced by the author's wording: Claude (Anthropic) and ChatGPT (OpenAI) were used for software development and testing, manuscript drafting and revision, and bibliographic checking, followed by author review, with the author responsible for the content.
- The conclusion no longer says the author statements are still to be confirmed.

## Final PDF review — 28 September 2026 (WORK_QUEUE Q11 step 5)

Owner corrections:
- Abstract grammar: the sentence now reads "… normalise the problem away by choosing one of two printed values, inferring a missing unit, or tuning an unknown …". No claim changed.
- Conclusion (SA-3 consistency): the sentence now reads "Bounded targets are reproduced or compared against the published values with their agreement reported explicitly, target by target."

Review corrections (layout and reference only; `prose_audit.py develop` shows no change to numbers, citations, evidence ids, status macros, mathematics or tables):
- "Appendix Appendix A/B" doubled: elsarticle's `\ref` already includes "Appendix", so `Appendix~\ref{app:…}` became `\ref{app:…}` (§1, the data-availability statement, Appendix B).
- Doubled full stops after run-in paragraph headings: trailing periods removed from the five `\paragraph{…}` titles.
- Appendix B: the stale list of tables to regenerate was replaced. The generated tables are `tab:crossenv` and `tab:evidence`; the facts check and Appendix A follow; Tables 1–3, 5 and 7 are marked as hand-written and source-audited.

Checks:

| Item | Result |
|---|---|
| Front matter | Title, author, affiliation (Independent researcher, Norway), e-mail, abstract, keywords |
| Abstract | 236 words |
| Highlights | 5 items; 70, 71, 62, 71, 64 characters (≤ 85) |
| Keywords | 6 |
| Figures and tables | Figure 1 and Tables 1–7 legible, none exceed the text width. Tables 2, 4 and 7 are placed as floats with white space around them; acceptable for a preprint |
| Cross-references and citations | 0 undefined; 16 of 16 bibliography entries cited |
| Markers | No TODO, FIXME, TBD or [author to confirm] |
| Declarations | Data/code availability, CRediT, competing interests (none), funding (no specific grant) |
| AI declaration | Identical to the owner-approved text |
| Appendix A | Regenerated; identical to the committed version |
| Generated tables and facts | `build_tables.py --check` OK; facts check 20 PASS / 0 FAIL / 0 OPEN |
| Build | Clean `latexmk` build: 29 pages, US letter, 0 undefined |

Remaining build messages, all benign:
- One 2.6 pt overfull box in `\output` on the title page (elsarticle preprint footer).
- A duplicate `page.1` hyperref destination (elsarticle highlights page plus title page).
- One underfull line (badness 1796) in §6 caused by a long monospaced path.
- BibTeX: "empty pages in Bueno1994". The SPE conference paper has no page range in the source records; it is cited by paper number and DOI.
- PA-06 (owner correction, 28 September 2026): the claim now reads "Published methods re-implemented from the source reproduce or closely agree with published values for bounded targets, with residual differences reported explicitly at target level", consistent with SA-3. Status stays SUPPORTED. Appendix A regenerated; claim counts unchanged (20 SUPPORTED / 4 PARTIALLY_SUPPORTED / 3 NOT_SUPPORTED_YET / 3 OUT_OF_SCOPE).

## Licence — 28 September 2026 (D-010)

- The data and code availability statement keeps "openly available" and adds "under the Apache License 2.0". It now states that the third-party publications used as sources retain their original rights and are neither redistributed nor relicensed.
- The PDF is 30 pages because references [13]–[16] reflow onto a new page. No number, citation or claim changed.

## Release v0.2.0 and Zenodo DOI — 28 September 2026 (WORK_QUEUE Q11 step 4)

- The GitHub release is v0.2.0, and tag `v0.2.0` points at `d0d96eb82c63236781d553423442275e50d2e38d` on `main`. The tree at that tag is identical to `develop` at the time, so the generated tables, Appendix A and the facts check correspond to the tagged release.
- Zenodo record https://zenodo.org/records/23017727. The version DOI is 10.5281/zenodo.23017727, and the concept DOI is 10.5281/zenodo.23017726.
- Verified from the owner's screenshots: title, author Gu, Zhiqiang, version v0.2.0, Software, open access, Apache License 2.0, and archive folder `zgu214-EngiProof-d0d96eb`.
- Reference [16] now carries the version DOI. The data-availability statement adds "archived on Zenodo (version 0.2.0)".

## Completion wording — 28 September 2026 (owner correction)

- The conclusion and Appendix B no longer describe regeneration as a future action. They state that Tables 4 and 6 and Appendix A were regenerated and checked against the released v0.2.0 evidence state, and that the manuscript facts check passed.
- Verified at tag v0.2.0 (`d0d96eb`):
  - `build_tables.py --check` OK;
  - facts check 20 passed, 0 failed, 0 open;
  - Appendix A regenerates identically.
- `git diff v0.2.0 develop` shows no change to `engiproof/`, `papers/`, `src/`, the cross-environment record or the claim–evidence matrix.
