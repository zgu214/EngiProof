# EngiProof v0.2.0 — Paper Ingestion & Evidence Automation

## Objective

Scale EngiProof from manually assembled evidence studies into a conservative paper-to-engineering-evidence automation pipeline while preserving source traceability and explicit human/verification gates.

## Invariants

1. Automatic extraction creates **candidates**, not verified evidence.
2. Source identity (fingerprint + bibliographic metadata) must be internally consistent before reproduction.
3. Copyrighted source PDFs remain external by default; absolute machine paths are never persisted.
4. DRAFT/BLOCKED studies cannot enter the live registry.
5. Missing inputs and source inconsistencies remain visible; never tune unknowns to force agreement.
6. `PUBLISHED`, `INDEPENDENT`, and `SOLVER_NEW` evidence remain distinct.
7. Execution/tests do not automatically grant `VERIFIED` status or engineering qualification.
8. `HANDOVER_CURRENT.md` is updated at every meaningful development checkpoint.

## Phase A — dev0 complete

- source fingerprinting;
- PDF/TXT/MD/RST ingestion;
- lexical Figure/Table/Equation/Appendix discovery;
- intake queue;
- DRAFT study scaffolding;
- basic promotion gate.

## Phase B — dev1 complete

- fingerprint-matched source re-opening;
- bounded page/line source dossiers;
- unit/symbol candidates;
- heuristic equation/table/figure/definition structures;
- reproduction task bundles;
- comparison templates;
- pipeline status.

## Phase B robustness — dev2 complete

- source identity audit (title/DOI/year + SHA-256 boundary);
- metadata repair without changing source fingerprint or candidate IDs;
- plural/cross-reference equation recovery;
- Type1/CFF printed-equation-number recovery (`ð...Þ`);
- multiline equation-block reconstruction candidates;
- candidate-ID-preserving missing-equation append;
- true-caption table block extraction with header/data/footnote candidates;
- selected-target readiness (`READY` / `PARTIAL` / `BLOCKED`);
- promotion gate blocks identity conflicts and structurally unready selected targets;
- pipeline distinguishes generated structure artifacts from engineering-ready selected targets.

## Phase C — next: evidence automation

- verify dev2 on P40 exact source;
- P40 Table 1 -> Eq. (9) -> Table 2 source-bounded reproduction;
- independent limiting-case/dimensional/arithmetic checks;
- deterministic comparison execution;
- discrepancy classification/escalation;
- evidence-graph expansion from approved artifacts;
- callable-tool generation after verification gates.

## Later

- stronger table column typing/merged-cell handling;
- figure axis/series/legend metadata and digitization contracts;
- DOI/title metadata reconciliation against optional external bibliographic services;
- section-heading/source-location contracts;
- batch intake only after single-paper evidence quality is reliable.

## Non-goals

- automatic engineering qualification;
- silent parameter tuning;
- maximizing paper count;
- redistributing copyrighted sources;
- treating extraction confidence as engineering confidence.

## First Phase C case — P40 in progress

P40 is the first ingestion-generated study to reach deterministic reproduction and an independent mechanics comparison. It remains `CONDITIONAL` because the source Table 2 PIP-3 Eq. (9) normalized value (`0.66`) does not agree with direct Eq. (9) evaluation from Table 1 (`~0.7057`). The mismatch is retained as an open discrepancy.

Next Phase C priorities:

1. accept/review P40 local verification and decide whether to promote the conditional study;
2. add discrepancy classification/escalation support to the generic runtime;
3. automate evidence-graph expansion from approved reproduction/comparison artifacts;
4. only then use another heterogeneous paper to test generality.

## Phase C1 — implemented in 0.2.0-dev3

Generic discrepancy classification/escalation, rounding-band assessment, independent-check corroboration metadata, persisted assessment artifacts, and a discrepancy promotion gate are implemented. Next: documented human decision/acceptance workflow, evidence-graph auto-expansion, and multi-case comparison/discrepancy execution.

## Phase C2 — implemented in 0.2.0-dev4

- append-only human discrepancy decisions;
- RESOLVED / BOUNDED / ACCEPTED_WITH_RATIONALE / DEFERRED dispositions;
- evidence-reference requirement for unblocking decisions;
- decision-aware promotion gate;
- explicit no-qualification effect from discrepancy decisions.

## Phase C3 — implemented in 0.2.0-dev5

- additive/idempotent evidence-graph synchronization;
- provenance nodes for tools, comparisons, discrepancies, automated assessments and human decisions;
- evidence-graph coverage audit;
- preservation of hand-authored graph content and qualification boundary.

## Phase B4 — implemented in 0.2.0-dev6

- punctuation-free publisher table captions;
- hyphenated publisher figure captions;
- rejection of obvious caption-like cross-references;
- table-block termination at the next recognized publisher caption;
- engineering property rows with parameter/unit/value layout;
- P41 used as the second real-format generalization stress test.

## P41 next engineering phase

After visual closure of the Table 2 inner `ΔS` cell, continue with:

- Table 3 case matrix;
- Eq. (9) axial-bonding criterion;
- partial/full bonding transition;
- end-expansion reproduction for Cases 1-4;
- independent criterion check and discrepancy assessment;
- evidence-graph expansion and promotion gate review.

## Phase B5 — implemented in 0.2.0-dev7

- publication-year vs received/accepted/copyright-year semantics;
- source-identity evidence contexts;
- no false year conflict when only administrative dates differ;
- split/multiline table and figure caption recognition;
- contextual table-block termination at split captions.

## Phase C1 — continuity architecture (dev8)
Machine-readable state; bootstrap/queue/blockers/decisions; continuity audit; source-PDF-free checkpoint bundle; private-cloud backup; P43 next.
