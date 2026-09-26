# EngiProof — Chat Compact Current

Updated: 26 September 2026  
Development line: `v0.2.0-dev2`  
Primary branch: `develop`

## Goal

EngiProof v0.2.0 is **Paper Ingestion & Evidence Automation**, not bulk manual paper addition.

```text
paper source
 -> fingerprint
 -> source identity audit
 -> target discovery
 -> missing-equation recovery
 -> source enrichment
 -> structure extraction
 -> selected-target readiness
 -> DRAFT scaffold/tasks/templates
 -> reproduction
 -> independent check
 -> comparison/discrepancy
 -> evidence graph
 -> callable engineering method
 -> live registry only after gates
```

## Stable baseline

Released `v0.1.1` remains stable with live studies:
`P08`, `P12`, `P16`, `P29`, `P36`, `P38`.

Do not change their evidence/qualification boundaries while developing v0.2.0.

## Current dev2 focus

Dev2 adds:
- grouped equation-reference recovery, e.g. `Eqs. (2), (3), (6), and (9)`;
- recovery of PDF equation-number artifacts such as `ð9Þ`;
- multiline equation-body reconstruction candidates;
- caption-anchored table reconstruction;
- selected-target readiness: `READY / PARTIAL / BLOCKED`;
- source identity audit and metadata repair;
- stricter promotion gate;
- `fonttools` dependency;
- pipeline stages for source identity + selected-target readiness.

## Active real-source case: P40

Title: `Propagation Buckling in Subsea Pipe-in-Pipe Systems`  
Canonical source basename: `p40-karampour2017.pdf`  
SHA-256: `e83902ba46b8e713ddf2f11f5953bdf318ac539f6701ff303651e28d3d5e28bb`  
Correct DOI: `10.1061/(ASCE)EM.1943-7889.0001337`  
Correct year: `2017`  
Selected targets: `Table 2`, `Table 1`, `Equation (9)`  
Evidence status: `CONDITIONAL`  
Live registry: `NO` (promotion technically ready; deferred for user review)

The previously entered 2013 DOI/year were wrong for this PDF and must be repaired before reproduction.

## P40 resume commands

```bat
engiproof set-metadata P40 --doi "10.1061/(ASCE)EM.1943-7889.0001337" --year 2017
engiproof audit-source P40 "<local source PDF>"
engiproof recover-equations P40 "<local source PDF>"
engiproof enrich P40 "<local source PDF>"
engiproof extract-structures P40 "<local source PDF>"
engiproof readiness P40
engiproof comparison-templates P40
engiproof pipeline P40
```

## Current P40 checkpoint

Dev2 selected-target readiness is now `READY`:

- `equation_count = 21`
- `table_count = 3`
- `figure_count = 33`
- `definition_count = 4`
- `Table 1 = READY`
- `Table 2 = READY`
- `Equation (9) = READY`

This confirms the dev2 robust-ingestion objective for the selected targets.

## P40 reproduction checkpoint

P40 deterministic reproduction is now implemented:

- published Eqs. (2), (3), (6), (9);
- Table 1 source inputs and Table 2 references;
- independent work-balance reconstruction from Eqs. (8a-d);
- 5 P40 tests;
- evidence graph and callable methods;
- evidence status `CONDITIONAL`.

Key discrepancy: PIP-3 direct Eq. (9) gives `0.705666` versus Table 2 `0.66` (~6.92% relative difference). PIP-1/PIP-2 agree to rounding. Independent work-balance agrees with Eq. (9) within 0.1%, so `P40-D001` remains OPEN and must not be tuned away.

Validation: 49 full tests PASS; `verify P40 = PASS_SOURCE_EXTERNAL / CONDITIONAL`; live `verify-all = PASS`.

## Next engineering work

1. Apply/run the P40 reproduction patch locally.
2. Review `P40-D001` and decide whether to promote P40 as `CONDITIONAL`.
3. Add generic discrepancy classification/escalation automation.
4. Then run a second heterogeneous ingestion-generated case.

## Non-negotiable rules

- Candidate extraction != evidence.
- Code execution != verification.
- Verification != engineering qualification.
- Never tune unknowns to force agreement.
- Preserve `PUBLISHED / INDEPENDENT / SOLVER_NEW`.
- Do not redistribute copyrighted source PDFs/raster extracts.
- Do not persist machine-specific absolute paths.
- Update `HANDOVER_CURRENT.md` and this file at every meaningful checkpoint.

## Fresh-chat startup instruction

```text
Continue EngiProof development from the existing repository.

Read AGENTS.md, ROADMAP_v0.2.0.md, PROGRESS_v0.2.0.md,
HANDOVER_CURRENT.md and CHAT_COMPACT_CURRENT.md.

Verify the actual repository state before claiming completed work.
Continue the highest-priority authorized work autonomously.
Do not restart the project or repeat completed work.
```

## P40 source-review finding

PIP-3 Eq. (9) discrepancy is OPEN: independent reconstruction from Eq. (8a-d) gives ~0.705 versus Table 2 published 0.66. PIP-1/PIP-2 agree to rounding. Direct Eq. (9) text still has CFF glyph placeholders. Visually confirm Eq. (9), Table 1 and Table 2 before coding the published method. Do not tune.

## Publication track

Paper A methodology/software manuscript is active as a living evidence capture. Keep engineering primary (~85%) and publication capture secondary (~15%). Paper B (P40 mechanics) stays parked until the P40 engineering chain is deeper.

## dev3 current checkpoint

Generic discrepancy automation is implemented. P40-D001 is `PUBLISHED_REFERENCE_MISMATCH`, HIGH, `BLOCK_PROMOTION`. Direct Eq.9 reproduction ~0.705666 and independent work-balance agree, while Table 2 reports 0.66. P40 remains CONDITIONAL/NOT_GRANTED and outside the live registry. Next: documented human discrepancy decision/acceptance workflow, then evidence-graph auto-expansion.
## Current dev4 state

v0.2.0-dev4 adds append-only human discrepancy decisions. P40-D001 remains OPEN/BLOCK_PROMOTION; no closure is recorded. A justified `RESOLVED`, `BOUNDED`, or `ACCEPTED_WITH_RATIONALE` decision requires reviewer + rationale + evidence refs and can unblock promotion, but never changes qualification (`NOT_GRANTED`).

## Current dev5 state

Dev5 adds generic evidence-graph synchronization/audit. P40-D001 has a human `DEFERRED` decision, remains `BLOCK_PROMOTION`, and qualification stays `NOT_GRANTED`. Run `graph-sync P40` then `graph-audit P40`; graph coverage may PASS while promotion remains blocked. Next major test is a second heterogeneous ingestion-generated case.

## P41 / dev6

P41 (ASME OMAE2011-49960) localized 26/26 targets and exposed a publisher-format bug: punctuation-free ASME table captions were not true-caption anchors in dev5. Dev6 generalizes caption/table-row recognition before scaffolding P41. First intended evidence chain: Table 1 -> Table 2 -> Eqs. 6-8. Table 3/Eq.9 follow after the first chain. Do not label any Table 2 numeric mismatch as a paper discrepancy until visual source confirmation.


## P41 reproduction checkpoint

P41 first chain is implemented: Table 1 geometry -> independent area/EA -> Table 2 -> Eqs. 6-8. Areas and EA reproduce Table 2 closely; Eq.8 closes to `f_s=471 N/m`; outer force share gives ~312.22 vs 312. Inner gives ~158.78 while extracted text says 153. Classify only as `SOURCE_TRANSCRIPTION_UNCERTAINTY` until visual Table 2 confirmation. P41 stays CONDITIONAL/NOT_GRANTED/outside live registry. Next after source-cell check: Table 3 + Eq.9 bonding/end-expansion chain.

## P41 Phase 2

P41 Table 2 mismatch is visually confirmed and reclassified `PUBLISHED_REFERENCE_MISMATCH`: published 153+312=465 N/m while fS=471 and Eqs.6-8 reproduce ~158.8+312.2=471. No tuning; 153->159 is plausible but unconfirmed. Eq.9 threshold ~158.78 N/m reproduces Table3 bonding classes. Dry-weight friction 1195*0.3=358.5 N/m supports the rounded 358 case. Eq.10 is callable but direct end-expansion reproduction remains conditional due missing source-bounded S0_total inputs.


## P41 Phase 3 / freeze

Figures 8-10 + Eq14 completed as source-bounded Phase 3. EI outer/inner ≈3.3966. New OPEN mismatch P41-D002: paragraph ~300/850 MNm vs Figure10 axis kNm. No silent correction. After verification, freeze P41 and move to a third mechanically different paper.
## Journal manuscript draft

A compile-ready LaTeX draft v0.1 now exists under `publication/PAPER_A_ENGIPROOF_LATEX/`. It includes P40/P41 source-backed discrepancy examples and a claim-evidence appendix. Keep it as a living draft; engineering remains primary. Next: P42, then update the cross-case results section.

