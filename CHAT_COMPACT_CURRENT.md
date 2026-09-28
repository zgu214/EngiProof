# EngiProof — Chat Compact Current

Updated: 27 September 2026  
Development line: `v0.2.0-dev8`  
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

## P41 frozen / move to P42

P41 Phase 3 is accepted. Pipeline is 16/17 complete; only live-registry promotion is intentionally blocked by two OPEN HIGH-priority published-reference mismatches. Graph audit PASS with 25/25 represented items and coverage 1.0. Qualification remains NOT_GRANTED. Freeze P41 and start P42 with materially different mechanics.

## P42 / dev7

P42 false source-year conflict diagnosed: 2018 is received/accepted/copyright metadata; publication is Marine Structures 64 (2019) 401–420 and DOI matches. Dev7 distinguishes publication vs secondary years. It also fixes Elsevier split captions (`Table 1` + title on next line). After dev7, re-audit/re-extract, then scaffold T006,T008,T009,T066,T067; Figure16 stays review-gated comparison evidence initially.

## P42 Phase 2

Eqs31-35 callable; Eqs36-39 analytical stress families regenerated for Figs20-23. At kappa=.06, transverse amplitudes ~84.10 MPa and normal ~21.3 MPa. P42-D001 records OBSERVED model-form/kinematics difference: analytical stress independent of Fz, FP-RUC varies with Fz due sliding/wire-path assumptions. FP-RUC points not digitized; no tuning.

## P42 Phase 3 / freeze

Eqs24-26 close exactly; Eqs27-30 + Eq41 implemented explicitly. Literal zero-boundary Figure16 probe does not reconcile with high-tension plot scale, so P42-D002 is OPEN `SOURCE_IMPLEMENTATION_PROVENANCE_GAP`, not a paper error. No tuning. Verify, graph-sync/audit, freeze P42, move to P43.

## Windows batch chaining rule — discovered during P42 Phase 3

The repository provides `engiproof.cmd` as the Windows dispatcher. When an EngiProof command is invoked **inside another `.bat`/`.cmd` file**, it must be prefixed with `call`.

Correct:
`call engiproof graph-sync P42`

Incorrect inside a batch file:
`engiproof graph-sync P42`

Without `call`, Windows transfers control to `engiproof.cmd` and does not return to the parent verification batch. This explains why the original `22_VERIFY_P42_PHASE3_WINDOWS.bat` stopped after `engiproof tool ...` and never printed its final PASS marker.

Apply this rule to all future Windows verification/automation batches.

## dev8 continuity architecture / P42 frozen

P42 Phase3 PASS and frozen CONDITIONAL/NOT_GRANTED. dev8 adds Git source-of-truth + durable control plane + replaceable chat context. New PROJECT_STATE/queue/blockers/decisions/bootstrap plus `continuity-audit` and `checkpoint --bundle`. Verify, commit/push, private-backup bundle, then P43.

## P43 Phase 1

Dareing & Huang 1976 natural-frequency benchmark implemented. Independent Hermite-FE solution of Eq8 reproduces selected Table1 eigenvalues; Eq10 reproduces Table2 errors; worked example reproduces 0.815 rad/s, 7.71 s exact / 7.68 s approximate; independent Figure6 mode1 inflection ~0.09 below top vs source ~0.1. No digitization; NOT_GRANTED. Next: local verify then wider Table1/Figs4-6.

## P43 Phase 2

Full Table1/2 matrix implemented: 35 rows, 175 eigenvalues, Figures4-5 parameter families, Figure6 first 3 independent modes. Ordinary values reproduce to source rounding. P43-D001 found: source Table1 alpha=0 beta=200 lambda5 visibly 13.221; independent Eq8 FE + Eq10 ≈18.221 and Table2 says zero error. Preserve as OPEN PUBLISHED_REFERENCE_MISMATCH; inferred 18.221 not silently substituted. Verify then freeze P43 CONDITIONAL and move P44.

P43-D002: Table 1 alpha=200, beta=100, lambda1 is visibly printed as 6.554. Independent Eq.8 FE gives ~6.654; Eq.10/Table2 internal consistency also supports 6.654. Preserve printed 6.554; inferred correction is not applied.

## P44 Phase 1

Bueno & Morooka 1994 SPE28723 contact case. Table1 area/I independently checked; Eq1 reproduces 429.098 lb printed arithmetic and exact sin60 gives 429.111 lb vs published FEM 429.11; 5.8/10=0.58 s; K1 penalty scale ~0.00515 in at 429 lb. P44-D001: paragraph says Fig7/8 times 4.06/2.32 s, captions say 0.58/1.74 s and Fig2 agrees with captions. Preserve mismatch; no full FE curve reproduction; NOT_GRANTED.

## P44 frozen / low-budget hold

P44 Phase1 local PASS. Freeze CONDITIONAL/NOT_GRANTED; preserve P44-D001; no full nonlinear contact-profile claim. Weekly model budget nearly exhausted: checkpoint, private archive, commit/push, then pause heavy research. Resume at P45 after reset from PROJECT_STATE/HANDOVER/NEW_CHAT_BOOTSTRAP.


## Runtime since dev8 (PR #2–#4)

MCP server (read-only default; run/verify opt-in via `ENGIPROOF_MCP_ALLOW_RUN`; regenerate never). Non-mutating verification: frozen evidence is compared in a sandbox, never rewritten; `engiproof regenerate` is explicit. egg-info untracked.

## P45 Phase 1

Safai 1983 nonlinear dynamic risers. Table2 geometry/offset reproduce; tables = SI of round imperial values; Appendix1 k-functions pass identity/continuity/Euler/independent-FE/rigid-body checks; Eq7 = Wilson-θ, θ not given (θ=1 limit Δt/T=0.5513). OPEN: D001 buoyed w_p rises; D002 Table1 cases 3–6 tensions 10× implausible; D003 1200 m tension unit missing; D004 '/g' typo; D005 head 'amplitude' is peak-to-peak per Figs 4a–9a; D006 '~15%' only as peak |stress|. Dynamic responses BLOCKED; no SOLVER_NEW; NOT_GRANTED. Next: local `28_VERIFY_P45_PHASE1_WINDOWS.bat`, freeze, then Paper A readiness review.

## P45 frozen / Paper A next

P45 local Windows verify PASS; frozen CONDITIONAL/NOT_GRANTED (D-006), D001–D006 OPEN, dynamics BLOCKED. Active: Paper A readiness review over P40–P45 (Q6); no automatic P46. Low priority: make graph-sync file-idempotent (Q7).

PR #7 merged (eeb84fc). Hardening PR: G2 taxonomy (19 proposed labels), G3 ingestion summaries, G4 cross-OS CI + environment records, G1 candidates. D-007 PROPOSED (hash inheritance, path-separator rendering, scoped P45 FE tolerance) awaits owner approval. Owner actions: approve D-007, taxonomy review, G1 decisions, run 29_ batch. No P46.

28 Sep 2026: owner approved D-007 and the taxonomy (19 labels); G1 decisions recorded (D-008: 2 ACCEPTED_WITH_RATIONALE, 2 BOUNDED, 3 DEFERRED; P43 kept blocking). PR #8 waits only on local P40–P43 ingestion summaries. No P46.
G3 closed: owner-run local intakes give machine-generated ingestion summaries for P40–P44 (f651f07). F22: engiproof.cmd swallowed exit codes, fixed. Matrix 20/4/3/3. PR #8 ready on the owner's yes.
P45 Windows verify re-run after F22 fix (bab6764): PASS with exit codes checked; pre-F22 banner superseded (D-006 addendum).
PR #9 merged (36dfdcb, Draft v0.2.1). Evidence gathering closed; active stage Q11 = submission refinement (AES/elsarticle, figures/tables, compression, references, source audit, PDF review). No P46.
