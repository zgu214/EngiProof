# EngiProof v0.2.0 progress

Checkpoint: 26 September 2026

## Implemented

- `engiproof.ingestion/1.0`
- `engiproof.source_fingerprint/1.0`
- `engiproof.target_candidates/1.0`
- conservative promotion gate
- local PDF/TXT/MD/RST source fingerprinting
- PDF page/text metadata extraction with `pypdf`
- automatic Figure/Table/Equation/Appendix candidate discovery
- persistent intake queue outside the live study registry
- DRAFT study + evidence-graph scaffolding from intake
- explicit no-copy default for copyrighted source files
- absolute-path privacy protection

## Next

1. source-location contracts and symbol inventories;
2. structured table extraction;
3. equation-block extraction;
4. figure caption/axis extraction;
5. generated reproduction task plans;
6. independent-check templates;
7. comparison/discrepancy automation;
8. tool-generation gate after verified reproduction.


## dev1 source-enrichment batch

Implemented:

- exact-source SHA-256 re-check before enrichment;
- `engiproof.source_map/1.0` page-level line counts and text hashes;
- `engiproof.target_dossiers/1.0` page/line locators and bounded excerpts;
- nearby unit/symbol candidate inventory;
- equation-block text candidates marked `review_required`;
- `engiproof.reproduction_tasks/1.0` kind-specific task bundles;
- CLI: `enrich`, `dossiers`, `dossier`, `task-bundle`;
- pipeline now exposes `source_enrichment` and `task_bundle` stages;
- source mismatch is rejected before enrichment.

The public-safety boundary remains unchanged: raw source files are not copied and full extracted source text is not persisted by default.

## Next

1. structured table/header extraction;
2. figure axis/series/caption metadata;
3. symbol-definition mapping and equation transcription review contracts;
4. automatic comparison-template generation;
5. discrepancy classification;
6. evidence-graph expansion from approved extraction artifacts.


## dev1 structure-extraction extension

Also implemented:

- `engiproof.structure_candidates/1.0`;
- equation-block candidates tied to exact printed equation numbers where possible;
- table caption/row structure candidates;
- figure caption candidates;
- source symbol-definition candidates;
- `engiproof.comparison_templates/1.0`;
- CLI: `extract-structures`, `structures`, `comparison-templates`;
- generated intake artifacts ignored by Git by default while preserving `engiproof/intake/README.md`.

Real-PDF smoke test: an 8-page pipe-in-pipe paper produced 17 target candidates, all 17 source-located during enrichment, with equation blocks and reproduction task generation completing without copying the source PDF.

Validation checkpoint: **39 tests PASS**, `engiproof verify-all = PASS`, and real-PDF smoke test completed with 17/17 discovered targets source-located.
