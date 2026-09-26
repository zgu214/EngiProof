# EngiProof v0.2.0 progress

Checkpoint: 26 September 2026 — `0.2.0.dev2`

## Baseline preserved

P08/P12/P16/P29/P36/P38 remain unchanged as the v0.1.1 live evidence baseline. `engiproof verify-all` passes in the dev2 build.

## dev0/dev1 already complete

Source fingerprinting, intake queue, lexical target discovery, DRAFT scaffold/promotion gate, source enrichment, bounded target dossiers, structure candidates, task bundles and comparison templates.

## dev2 complete

- grouped equation references are discovered rather than losing all but the first/last cited equation;
- standalone/Type1-CFF equation numbering artifacts such as `ð9Þ` are normalized/recovered;
- multiline displayed equations are reconstructed into bounded review candidates;
- missing equations can be appended to an existing intake without renumbering existing candidate IDs;
- tables use true caption anchors and capture header/data/footnote candidates;
- selected targets receive an explicit structural-readiness gate;
- source identity audit compares configured metadata against fingerprint-matched source text;
- metadata can be corrected without changing the source fingerprint or target IDs, but a re-audit is mandatory;
- promotion blocks source identity conflicts and selected-target structural blockers;
- `fonttools` added for CFF/Type1 parsing support;
- `HANDOVER_CURRENT.md` established as mandatory checkpoint state.

## Validation

- 44 automated tests passed across split test runs;
- ingestion/dev2 module: 16/16 tests PASS;
- remaining baseline test modules: 28/28 PASS;
- `engiproof doctor`: PASS;
- `engiproof verify-all`: PASS for all six live studies.

## P40 real-source findings driving dev2

P40 selected targets are Table 1, Table 2 and Eq. (9). dev1 found the tables but failed to reconstruct the Eq. (9) body and did not reliably recover all equations cross-referenced around Table 2. It also accepted incorrect bibliographic metadata entered at intake. These are now explicit dev2 gates rather than silent limitations.

## Immediate next

Run dev2 against the exact P40 PDF, repair/audit P40 metadata, recover missing equations, re-enrich/re-extract, inspect readiness, then begin source-bounded P40 reproduction only if the selected targets become READY.

## dev2 P40 ingestion-generated reproduction checkpoint

P40 (`Propagation Buckling in Subsea Pipe-in-Pipe Systems`) has progressed through the v0.2.0 pipeline from fingerprinted source intake to source-bounded analytical reproduction.

Implemented:

- source-reviewed Table 1 inputs and Table 2 references;
- published Eqs. (2), (3), (6), and (9);
- independent Eq. (8a-d) work-balance reconstruction;
- callable methods and deterministic result generation;
- five P40 verification tests;
- machine-readable comparison/discrepancy evidence graph.

Result: PIP-1 and PIP-2 Eq. (9) ratios reproduce Table 2 to source rounding. PIP-3 calculates `0.705666` versus published `0.66`; the approximately 6.92% relative mismatch remains OPEN and is not tuned away. The independent work-balance reconstruction agrees with direct Eq. (9) within 0.1%, supporting the analytical implementation while leaving the source-table discrepancy unresolved.

Validation checkpoint: full repository test discovery = **49 tests PASS**; `engiproof verify P40 = PASS_SOURCE_EXTERNAL / CONDITIONAL`; live `verify-all = PASS`. P40 is deliberately not yet added to the live registry.

## dev3 discrepancy automation checkpoint

Implemented generic discrepancy category/review-priority/promotion-effect classification, structured rounding-band checks, independent-check support metadata, persisted assessments, CLI audit/gate commands, and promotion blocking for unresolved high-priority conflicts. P40-D001 is the first real blocking case. P40 remains `CONDITIONAL`, `NOT_GRANTED`, and outside the live registry; no tuning is permitted.

## dev4 human discrepancy decision workflow

Added append-only discrepancy review decisions. Automated classification remains advisory; documented human review may resolve, bound, accept-with-rationale, or defer an item. Unblocking decisions require evidence references and never grant engineering qualification. P40-D001 remains OPEN/BLOCKING until the user records a justified decision.

## dev5 evidence-graph auto-expansion

Implemented generic evidence-graph synchronization and audit. P40 can now carry the complete provenance chain from published source and callable methods through comparisons, P40-D001 assessment and the append-only DEFERRED human decision. The graph is additive/idempotent and qualification remains NOT_GRANTED.

## dev6 publisher-style extraction robustness

P41 demonstrated 26/26 target localization but exposed a dev5 caption-readiness limitation: ASME captions such as `Table 1 Pipeline data` were not treated as true caption anchors. Dev6 generalizes caption recognition and engineering table-row extraction before P41 scaffolding/reproduction.

## P41 first reproduction checkpoint

The second real ingestion-generated case now reproduces a source-bounded axial load-sharing chain from Goplen et al. (2011):

- Table 1 geometry and Young's modulus;
- independent steel-area calculation;
- independent axial-stiffness (`EA`) calculation;
- Table 2 axial stiffness / soil-friction inputs;
- Eq. (6) inner load-share increment;
- Eq. (7) outer load-share increment;
- Eq. (8) total force-increment identity.

Results:

- Table 1 geometry independently reproduces Table 2 steel areas to <0.01% relative difference;
- Table 1 geometry/E reproduces Table 2 `EA` values to <0.02%;
- Eq. (8) closes exactly to `f_s = 471 N/m` by construction;
- outer force share calculates about `312.22 N/m`, agreeing with extracted Table 2 value `312 N/m` to integer rounding;
- inner force share calculates about `158.78 N/m`, while PDF text extraction currently reads `153 N/m`.

The inner-force difference is classified as `SOURCE_TRANSCRIPTION_UNCERTAINTY`, not a confirmed paper mismatch. Visual confirmation of the original Table 2 cell is required before closure or escalation.

P41 remains `CONDITIONAL`, `NOT_GRANTED`, and outside the live registry.

## dev7 source identity + split captions

P42 correctly configured 2019 as publication year but dev6 selected 2018 from received/accepted/copyright metadata and raised a false conflict. Dev7 now prioritizes bibliographic publication-year evidence. P42 also exposed split captions (`Table 1` followed by the caption title on the next line); dev7 recognizes these generically.

## dev8 — continuity architecture
P42 Phase3 is locally green/frozen. Continuity now uses Git source of truth + repository control plane + replaceable chat/session context.
