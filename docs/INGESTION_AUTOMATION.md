# Paper ingestion and evidence automation

EngiProof v0.2.0 keeps paper ingestion separate from live engineering evidence.

## 1. Ingest a local source

```bat
engiproof ingest "D:\papers\paper.pdf" --paper-id P40 --title "Paper title" --doi "10.xxxx/xxxxx" --year 2026
```

The source is fingerprinted (SHA-256, size, MIME, PDF metadata/page count) and is **not copied** into the repository.

## 2. Discover candidate targets

```bat
engiproof intake P40
```

Figure/Table/Equation/Appendix references are ranked as candidates. Candidate discovery is a review queue, not evidence.

## 3. Enrich against the exact same source

```bat
engiproof enrich P40 "D:\papers\paper.pdf"
```

The source SHA-256 must match the ingestion fingerprint. EngiProof then writes:

- `source_map.json`: page line counts and page-text hashes, without full extracted text;
- `target_dossiers.json`: bounded excerpts, page/line locators, nearby units/symbols, and equation-block candidates.

Inspect:

```bat
engiproof dossiers P40
engiproof dossier P40 T001
```

## 4. Create a DRAFT scaffold

```bat
engiproof scaffold P40 --targets T001,T004,T006
```

The scaffold is not live and makes no reproduction claim.

## 5. Generate reproduction tasks

```bat
engiproof task-bundle P40
engiproof plan P40
engiproof pipeline P40
```

Task bundles are kind-specific. Equation tasks add transcription/sign/dimension checks; table tasks add schema/unit/duplicate audits; figure tasks add axes/series/normalization and digitization-uncertainty checks.

## 6. Promotion remains gated

```bat
engiproof promotion-gate P40
```

A study cannot be promoted while DRAFT/BLOCKED or without source-bounded results, tests and callable tools.

## Safety and evidence boundary

- absolute machine paths are never persisted;
- source PDFs are not copied by default;
- full extracted source text is not persisted by default;
- bounded excerpts and locators are source-review aids, not verified evidence;
- automated tasks are plans, not completed reproduction;
- code execution alone never grants `VERIFIED` or engineering qualification.
