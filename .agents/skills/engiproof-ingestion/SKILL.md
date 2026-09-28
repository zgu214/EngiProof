---
name: engiproof-ingestion
description: Convert a local engineering paper intake into a source-bounded EngiProof DRAFT study and execute authorized reproduction work without promoting unsupported evidence.
---

# EngiProof ingestion skill

Use EngiProof's intake pipeline rather than manually inventing study structure.

1. Run `engiproof ingest <source> --paper-id <ID> ...`.
2. Run `engiproof audit-source <ID> <source>`; resolve title/DOI/year conflicts before reproduction.
3. Run `engiproof recover-equations <ID> <source>` when grouped references or printed equation numbers reveal missing equations. Existing target IDs must be preserved.
4. Run `engiproof enrich <ID> <source>` to verify the same SHA-256 source and build bounded page/line target dossiers.
5. Select important targets; prioritize source figures/tables/equations that support reproducible engineering mechanics or published comparisons.
6. Run `engiproof scaffold <ID> --targets ...` if no scaffold exists.
7. Run `engiproof extract-structures <ID> <source>` and `engiproof readiness <ID>`; do not equate an existing structure file with selected-target readiness.
8. Run `engiproof task-bundle <ID>`, `engiproof comparison-templates <ID>`, and `engiproof plan <ID>`.
9. Never guess missing inputs or tune parameters to force source agreement.
10. Keep `PUBLISHED`, `INDEPENDENT`, and `SOLVER_NEW` separate.
11. Preserve source inconsistencies as discrepancy records.
12. Add deterministic tests and comparison metrics.
13. Run `engiproof promotion-gate <ID>`; do not bypass a blocked gate.
14. Only run `engiproof promote <ID>` after the gate is genuinely ready.
15. Update `HANDOVER_CURRENT.md` at every meaningful development checkpoint so another chat/agent/developer can resume without reconstructing project state from conversation history.

Raw copyrighted source files stay local. Persist fingerprints and source locators, not machine-specific absolute paths.

Generated intake artifacts under `engiproof/intake/<ID>/` remain local by default through `.gitignore`; do not force-add source excerpts or private paper-derived intake artifacts to public Git history.

## dev3 discrepancy gate

16. Run `engiproof assess-discrepancies <ID>` and `engiproof discrepancy-gate <ID>` after comparison/discrepancy records exist.
17. If the discrepancy gate returns `BLOCK_PROMOTION`, do not promote the study until the discrepancy is resolved, bounded, or explicitly accepted through a documented decision.
18. Update both `HANDOVER_CURRENT.md` and `CHAT_COMPACT_CURRENT.md` at meaningful checkpoints.
