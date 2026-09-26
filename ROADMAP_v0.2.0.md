# EngiProof v0.2.0 — Paper Ingestion & Evidence Automation

## Objective

Scale EngiProof from manually assembled evidence studies into a conservative automation pipeline:

```text
PDF / paper source
        ↓
source fingerprint
        ↓
target discovery
        ↓
equation / table / figure candidate extraction
        ↓
DRAFT study scaffold
        ↓
reproduction
        ↓
independent check
        ↓
comparison
        ↓
discrepancy
        ↓
evidence graph
        ↓
callable engineering method
```

## v0.2.0 invariants

1. Automatic discovery produces **candidates**, never verified evidence.
2. Original copyrighted PDFs remain external by default.
3. Absolute machine paths are never persisted in public metadata.
4. A DRAFT/BLOCKED study cannot enter the live registry.
5. Promotion requires source-bounded targets, result files, verification tests and callable tools.
6. Execution alone never grants `VERIFIED` status or engineering qualification.
7. Existing v0.1.1 studies remain backward compatible.

## Phase A — implemented in 0.2.0-dev0

- source fingerprinting (SHA-256, size, MIME, PDF metadata/page count)
- PDF/TXT/MD/RST text extraction
- lexical Figure/Table/Equation/Appendix candidate discovery
- evidence-oriented candidate scoring
- persistent intake queue separated from live registry
- DRAFT study/evidence-graph scaffolding
- promotion gate that blocks incomplete studies
- CLI commands for ingestion/intake/scaffold/promotion gate

## Phase B — implemented in 0.2.0-dev1

- fingerprint-matched source re-opening and enrichment
- page/line source locators with page-text hashes
- bounded target dossiers for Figure/Table/Equation/Appendix candidates
- equation-block text candidates for review
- local unit/symbol inventories around targets
- kind-specific reproduction task bundles
- pipeline stages for enrichment and generated task bundles

## Phase B2 — next

- table row/header structure candidates with bounded source excerpts
- figure caption candidates
- equation-block candidates and symbol-definition mapping
- target-type comparison metric templates

## Phase B3 — next

- robust table column/header parsing with units and merged-cell handling
- figure axis/series/legend metadata extraction
- stronger equation transcription and symbol-definition association
- DOI/bibliographic metadata reconciliation
- section-heading/source-location contracts
- deterministic comparison execution templates

## Phase C — evidence automation

- independent-calculation candidate generation
- comparison metric templates by target type
- discrepancy classification and escalation
- evidence-graph expansion from generated artifacts
- callable-tool generation only after verification gates

## Non-goals

- automatic engineering qualification
- silent parameter tuning
- bulk paper counts without evidence
- redistributing copyrighted source PDFs
- pretending lexical extraction equals reproduction
