# Changelog

## 0.2.0 — 2026-09-28

The first release of the v0.2.0 line: paper ingestion and evidence automation, and the software state cited by Paper A.

- **Licence:** Apache License 2.0 (`LICENSE.txt`, `NOTICE`). It replaces the previous all-rights-reserved notice. Third-party publications and source materials keep their original rights and are neither distributed nor relicensed.

- Six frozen CONDITIONAL evidence cases, P40–P45 (1976–2019, including a 1983 scanned source). Every case is source-bounded, has independent checks, and keeps discrepancy records without tuning. Qualification is NOT_GRANTED throughout.
- Non-mutating verification (D-005). It runs in a disposable sandbox with a six-class comparator. Cross-environment equivalence rules were approved in D-007. CI verifies all 12 studies on Linux, Windows and macOS with a tracked-file non-mutation gate. The Windows dispatcher now propagates exit codes (F22).
- Controlled discrepancy taxonomy: 9 categories and 7 loci, with all 19 records approved (D-008). Append-only human discrepancy decisions gate promotion (D-008, D-009).
- Text-free, machine-generated ingestion summaries for P40–P45, and the environment record.
- P44 manifest: explicit `qualification: NOT_GRANTED`, a metadata-consistency correction (D-009).
- Paper A manuscript (Advances in Engineering Software, elsarticle). Tables and a facts file are generated from repository data (`scripts/build_tables.py`), with a prose facts check (`scripts/check_manuscript_facts.py`), the claim–evidence appendix and the final source audit (SA-1..SA-10).

## 0.2.0-dev2 — 2026-09-26

Added the first P40 ingestion-generated reproduction checkpoint: source-bounded Tables 1-2, published Eqs. (2)/(3)/(6)/(9), an independent Eq. (8a-d) work-balance check, callable tools, verification tests, and an explicit OPEN PIP-3 discrepancy. P40 remains outside the live registry pending user review.

Added source-identity audit and metadata repair, cross-reference/printed-number equation recovery, multiline equation reconstruction, true-caption table data-block extraction, selected-target readiness gating, stricter promotion checks, CFF/Type1 font support, and mandatory `HANDOVER_CURRENT.md` checkpoint continuity.

## 0.2.0-dev1 — 2026-09-26

Added fingerprint-matched source enrichment, page/line locators, bounded target dossiers, equation/table/figure/definition structure candidates, unit/symbol inventories, kind-specific reproduction task bundles, target-type comparison templates, and new CLI/pipeline stages. Generated intake artifacts are ignored by Git by default; full extracted paper text remains ephemeral by default.

## 0.1.1 — 2026-09-25

Promoted the engineering-evidence runtime from the v0.1.0 two-study prototype to six live studies. Added generic Study, Source, Evidence, Comparison, Discrepancy and Verification contracts; machine-readable provenance/evidence/comparison/discrepancy queries; P38 complete evidence-chain integration; and source-bounded P16, P29 and P36 studies with independent checks and explicit unresolved discrepancies. P08/P12 remain backward compatible. Engineering qualification remains separate and is not granted by this release.

## 0.1.0 — 2026-09-25

Initial public-ready engineering evidence framework package with P08 and P12 live studies.

## 0.2.0-dev0 — 2026-09-26

Added source fingerprinting, paper-intake queue, conservative Figure/Table/Equation candidate discovery, DRAFT study scaffolding and a promotion gate. Automatic discovery remains explicitly separate from verified evidence and engineering qualification.

## 0.2.0-dev3 — 2026-09-26

Added generic discrepancy classification, review-priority/escalation assessment, a discrepancy promotion gate, persisted assessment artifacts, all-study discrepancy audit, and P40 as the first real `PUBLISHED_REFERENCE_MISMATCH` case. P40-D001 blocks promotion while unresolved; existing live CONDITIONAL studies are not retroactively demoted.

## 0.2.0-dev4 — 2026-09-26

Added append-only human discrepancy decisions with RESOLVED/BOUNDED/ACCEPTED_WITH_RATIONALE/DEFERRED dispositions, evidence-reference requirements for unblocking decisions, decision-aware discrepancy gates, and explicit preservation of the engineering-qualification boundary.

## 0.2.0-dev5 — 2026-09-26

Added additive/idempotent evidence-graph synchronization and provenance-coverage auditing for callable tools, comparisons, discrepancies, automated assessments and human discrepancy decisions. Graph synchronization preserves hand-authored content and never changes engineering qualification.

## 0.2.0-dev6 — 2026-09-26

Improved publisher-style structure extraction after the P41 ASME stress test. Added punctuation-free and hyphenated caption recognition, conservative cross-reference rejection, table-block termination at subsequent publisher captions, and engineering parameter/unit/value row recognition.

## 0.2.0-dev7 — 2026-09-26

Fixed source-identity year semantics by distinguishing publication-year evidence from received/accepted/copyright years. Added split/multiline publisher-caption recognition for tables and figures, triggered by the P42 Marine Structures stress test.

## 0.2.0-dev8 — Three-layer continuity architecture
Added machine state, queue/blockers/decisions/bootstrap controls, continuity audit, resumable source-PDF-free checkpoint bundle, and private-cloud recovery workflow.
