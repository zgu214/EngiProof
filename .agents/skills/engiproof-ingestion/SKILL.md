---
name: engiproof-ingestion
description: Convert a local engineering paper intake into a source-bounded EngiProof DRAFT study and execute authorized reproduction work without promoting unsupported evidence.
---

# EngiProof ingestion skill

Use EngiProof's intake pipeline rather than manually inventing study structure.

1. Run `engiproof ingest <source> --paper-id <ID> ...`.
2. Review `engiproof/intake/<ID>/source_fingerprint.json` and `target_candidates.json`.
3. Run `engiproof enrich <ID> <source>` to verify the same SHA-256 source and build bounded page/line target dossiers.
4. Run `engiproof extract-structures <ID> <source>` to build equation/table/figure/definition structure candidates.
5. Select important targets; prioritize source figures/tables/equations that support reproducible engineering mechanics or published comparisons.
6. Run `engiproof scaffold <ID> --targets ...`.
7. Run `engiproof task-bundle <ID>`, `engiproof comparison-templates <ID>`, and `engiproof plan <ID>`.
8. Never guess missing inputs or tune parameters to force source agreement.
9. Keep `PUBLISHED`, `INDEPENDENT`, and `SOLVER_NEW` separate.
10. Preserve source inconsistencies as discrepancy records.
11. Add deterministic tests and comparison metrics.
12. Run `engiproof promotion-gate <ID>`; do not bypass a blocked gate.
13. Only run `engiproof promote <ID>` after the gate is genuinely ready.

Raw copyrighted source files stay local. Persist fingerprints and source locators, not machine-specific absolute paths.

Generated intake artifacts under `engiproof/intake/<ID>/` remain local by default through `.gitignore`; do not force-add source excerpts or private paper-derived intake artifacts to public Git history.
