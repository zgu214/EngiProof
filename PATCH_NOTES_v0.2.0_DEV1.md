# EngiProof v0.2.0-dev1 — ingestion, source enrichment and structure automation

This cumulative v0.2.0 development patch is intended for the public v0.1.1 baseline on `develop`.

## Added

- source fingerprinting and target discovery (dev0 baseline)
- exact-source SHA-256 re-check before enrichment
- page/line source maps with page text hashes
- bounded target dossiers with locators/excerpts/unit/symbol candidates
- exact-number equation block candidates where PDF text extraction allows
- table caption/row structure candidates
- figure caption candidates
- symbol-definition candidates
- kind-specific reproduction task bundles
- target-type comparison metric templates
- pipeline stages for enrichment/structure/task/template generation
- Git-ignore protection for generated per-paper intake directories
- real-PDF smoke-test record

## Evidence boundary

All automated discoveries, extracted structures, tasks and comparison templates remain review/planning artifacts. They do not become engineering evidence automatically. Raw source PDFs are not copied and full extracted paper text is not persisted by default.

## Validation

- 39 unit/regression tests PASS
- `engiproof verify-all` PASS for all six v0.1.1 live studies
- real 8-page PiP PDF smoke test: 17 candidates discovered, 17/17 source-located
