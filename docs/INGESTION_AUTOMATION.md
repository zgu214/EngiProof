# Paper ingestion and evidence automation

EngiProof v0.2.0 keeps paper ingestion, extraction, reproduction and evidence promotion as separate states.

## Core sequence

```bat
engiproof ingest "<source.pdf>" --paper-id P40 --title "Paper title" --doi "10.xxxx/..." --year 2026
engiproof audit-source P40 "<source.pdf>"
engiproof recover-equations P40 "<source.pdf>"
engiproof enrich P40 "<source.pdf>"
engiproof scaffold P40 --targets T001,T004,T006
engiproof extract-structures P40 "<source.pdf>"
engiproof readiness P40
engiproof task-bundle P40
engiproof comparison-templates P40
engiproof pipeline P40
```

The raw source is not copied. SHA-256 is the source identity anchor; full extracted text remains ephemeral by default.

## Source identity audit (dev2)

`audit-source` compares configured title/DOI/year with candidates found in the exact fingerprint-matched source. A DOI/year conflict is a blocker.

If metadata was entered incorrectly, repair metadata without deleting the intake or changing target IDs:

```bat
engiproof set-metadata P40 --doi "10.xxxx/correct" --year 2026
engiproof audit-source P40 "<source.pdf>"
```

## Equation recovery (dev2)

`recover-equations` recognizes grouped references such as `Eqs. (2), (3), (6), and (9)` and common printed-equation-number extraction artifacts. Missing equation candidates are appended while existing target IDs are preserved. Re-run `enrich` and `extract-structures` afterwards.

## Selected-target readiness (dev2)

`structure_candidates.json` existing is not enough. `readiness` checks the selected targets themselves:

- equation: a bounded equation-body candidate must exist;
- table: a true table-caption anchor plus at least one data-row candidate must exist;
- figure: caption location is only `PARTIAL` until axes/series are reviewed.

Reproduction/promotion must not be treated as ready merely because extraction artifacts were generated.

## Evidence boundary

- candidates are not evidence;
- extracted equation/table text requires source review;
- comparison templates are not comparison results;
- code execution is not verification;
- verification is not engineering qualification;
- no silent parameter tuning;
- no absolute machine paths in persistent/public metadata.
