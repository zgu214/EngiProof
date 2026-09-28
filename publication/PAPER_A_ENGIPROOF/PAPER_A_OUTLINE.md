# Paper A — Outline (evidence-based)

Working title: **EngiProof: A Provenance-Preserving Framework for Converting Published Engineering Research into Reproducible Computational Evidence**
Target: Advances in Engineering Software (unchanged from `docs/PUBLICATION_STRATEGY.md`).

Built from `CLAIM_EVIDENCE_MATRIX.md`: each section lists only the claims it may make (PA-xx), the evidence it draws on, and what it must not say. Sections marked † depend on a gap in `PAPER_A_GAPS.md` being closed or explicitly scoped.

The existing LaTeX Draft v0.1 (`PAPER_A_ENGIPROOF_LATEX/publication/PAPER_A_ENGIPROOF_LATEX/sections/`) is kept. The last column maps each new section to the draft section it extends.

| # | Section | Claims | Evidence base | Must not say | Draft v0.1 source |
|---|---|---|---|---|---|
| 1 | **Problem.** Published engineering results are hard to reproduce, and inconsistencies are often normalised away silently: a reader or code port “fixes” a value, infers a missing unit, or tunes an unknown. | motivation; PA-11, PA-21 as the answer | Concrete examples from P40–P45: printed 13.221 vs internally consistent 18.221 (P43-D001); 153 + 312 ≠ 471 (P41-D001); tension with no unit (P45-D003) | “Literature is unreliable” in general | `01_introduction.tex` |
| 2 | **Evidence architecture.** Source → study → published method / independent check → comparison → discrepancy → decision → evidence graph → callable method → verification record; qualification kept separate. Evidence classes PUBLISHED / INDEPENDENT (SOLVER_NEW defined, reserved). | PA-01, PA-22, PA-25 (partial), PA-28 | `engiproof/contracts/contracts.json`, `docs/ARCHITECTURE.md`, `AGENTS.md` rules | That SOLVER_NEW is demonstrated | `02_framework.tex` |
| 3 | **Source ingestion and structural extraction.** Fingerprinting, identity audit, candidate discovery, readiness gate; extraction ≠ evidence. Failure-driven hardening across ASCE/ASME/Elsevier sources and a 1983 scan. † G3 | PA-01, PA-02 (partial), PA-03, PA-04 (partial) | Failure register F1–F7, F16, F18; P45 readiness PARTIAL 4/16 with manual review | Any extraction accuracy figure (PA-05) | `03_ingestion.tex` |
| 4 | **Source-bounded reproduction.** Per-target implementation from the source; outcome vocabulary REPRODUCED / COMPARED / VERIFIED / CONDITIONAL / BLOCKED; no inferred inputs. | PA-06, PA-07, PA-21 | P40-C001, P41-C001…C006, P42-C002/C004/C006, P43-C002…C008, P44-C001…C003, P45-C001 | “Paper X reproduced” | `04_case_studies.tex` (partly) |
| 5 | **Independent verification.** Methodologically independent computations and what they decide. | PA-08, PA-09; limitation PA-10 | P40 work balance; P43 Hermite-FE eigen-solution; P45 independent beam-column FE, rigid-body null space, integrator stability; `independent_support` fields | Organisational independence | new (partly `04`) |
| 6 | **Discrepancy preservation and classification; the human decision boundary.** Detection without tuning; controlled taxonomy; append-only decisions; promotion gate. † G1, G2 | PA-11, PA-13 (after G2), PA-14 (after G1); PA-12 disclaimed | 14 records (13 OPEN, 1 OBSERVED); `discrepancy-audit`; P40-D001 decision; promotion gate on P40–P45 | Completeness of detection; that closure is automatic | `05_discrepancies.tex` |
| 7 | **Provenance and the evidence graph.** Machine-auditable linkage; coverage audit; canonical text identity. | PA-15, PA-16 (partial) | `graph-audit` coverage 1.0 on all six; `src/engiproof/provenance_identity.py`; CRLF finding in the mutation inventory | That graph coverage implies correctness | `02_framework.tex` (graph part) |
| 8 | **Non-mutating verification.** The mutation defect found in the framework's own verification, its inventory, the design rule (D-005), and the four-way distinction: byte reproducibility, numerical reproducibility, engineering equivalence, engineering verification. † G4 for the cross-OS part | PA-17, PA-18, PA-19 (partial) | `docs/MUTATION_INVENTORY_v0.2.0.md`; comparator classes; P43 tolerance + guard; P45 NUMERICAL_NONMATERIAL under NumPy 2.5.3; CI gate | That tolerances are acceptance criteria | new (`b_reproducibility.tex` seed) |
| 9 | **Multi-case evaluation across P40–P45.** Organised by capability, not by paper: one cross-case table (mechanics × evidence type × discrepancy types × reproduction outcome × independent method) and short case vignettes that each illustrate a different capability. † G5 adds the model-vs-experiment row | PA-06…PA-21 | `PAPER_A_READINESS_REVIEW.md` §3 diversity table | Paper count as evidence | `04_case_studies.tex`, `06_evaluation.tex` |
| 10 | **Failure cases and limits.** The framework's own failures (F1–F22) and legitimately irreproducible targets (P41/P42/P44 FE, P45 dynamics BLOCKED). | PA-20, PA-24 | Failure register; P45-C009 missing-parameter list and the θ-stability consequence | Defect counts as quality metrics | `08_limitations.tex` |
| 11 | **Qualification boundary.** Verification ≠ qualification; recomputation tolerance ≠ acceptance; human review remains required for physics, scope and source interpretation. | PA-22, PA-23 (out of scope) | NOT_GRANTED everywhere; contract rules; `AGENTS.md` human-review boundary | Any design/qualification claim | `07_discussion.tex` (part) |
| 12 | **Discussion and future work.** Scope (offshore/subsea mechanics), SOLVER_NEW via solver adapters where the agent orchestrates and EngiProof adjudicates, external replication, extraction benchmarks, related work (including ScientistTwo / Chain-of-Evidence as architectural context only). | PA-25, PA-27, PA-29 as scope statements | — | Autonomous scientific discovery; generality beyond the domain | `07_discussion.tex`, `09_conclusion.tex` |

Appendices: A — claim–evidence matrix (from `CLAIM_EVIDENCE_MATRIX.md`, replacing `a_claim_evidence.tex`); B — reproducibility entry points (`verify-all`, per-study verify scripts, CI, mutation inventory; extends `b_reproducibility.tex`).

## Figures and tables

| ID | Content | Source of truth |
|---|---|---|
| Fig. 1 | Evidence lifecycle with the qualification boundary | `docs/ARCHITECTURE.md` (redrawn) |
| Fig. 2 | Evidence-graph schema with one real P45 subgraph | `engiproof/studies/P45/evidence_graph.json` |
| Fig. 3 | Discrepancy → decision → promotion flow | `src/engiproof/discrepancy.py` |
| Fig. 4 | Non-mutating verification: sandbox, comparator classes, regenerate boundary | `src/engiproof/isolation.py` |
| Table 1 | Cross-case capability matrix P40–P45 | readiness review §3 |
| Table 2 | Discrepancy taxonomy with one example each † G2 | `S(Pxx).discrepancies` |
| Table 3 | Mutation inventory summary (by class, before/after) | `docs/MUTATION_INVENTORY_v0.2.0.md` |
| Table 4 | Failure register (condensed) | readiness review §4 |

All figures are to be redrawn from repository data; no publisher raster is reproduced.

## Writing constraints

- Every numerical statement traces to a repository artifact listed above.
- Every case states PUBLISHED vs INDEPENDENT explicitly; OPEN discrepancies stay OPEN in the text.
- No sentence implies qualification, generality beyond the domain, extraction accuracy, detection completeness or autonomous discovery.
- The abstract and conclusions describe a methodology and its evidence, not an AI novelty.
