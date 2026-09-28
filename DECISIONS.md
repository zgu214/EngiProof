# EngiProof — Decisions

## D-001 — Three-layer continuity architecture
Adopted:
1. Git repository source of truth.
2. Durable continuity control plane.
3. Replaceable chat/session context.

No critical project state may depend exclusively on conversation history or hidden assistant memory.

## D-002 — P42 freeze
P42 Phase 3 local verification reported `=== P42 PHASE3 VERIFY PASS ===`.
Freeze P42 as CONDITIONAL evidence; preserve D001/D002; no tuning; qualification NOT_GRANTED.

## D-003 — Checkpoint bundle policy
`engiproof checkpoint --bundle` must exclude copyrighted source PDFs and private client data.


## D-004 — P44 Phase 1 freeze

Local verification completed with `=== P44 PHASE1 VERIFY PASS ===`.

P44 is frozen as a `CONDITIONAL` evidence case at Phase 1. Preserve Table 1 checks, Eq. (1) equilibrium/FEM agreement, time discretization, K1 scale and `P44-D001`. Do not invent missing geometry or solver inputs to force full contact-profile agreement. Qualification remains `NOT_GRANTED`.


## D-005 — Verification must not mutate the evidence being verified

Adopted after the v0.2.0 mutation inventory (`docs/MUTATION_INVENTORY_v0.2.0.md`), which found 20 tracked result files rewritten by `verify`, `verify-all` and the unit-test suite: 7 BYTE_ONLY, 3 ENVIRONMENT_METADATA, 10 NUMERICAL_NONMATERIAL, 0 NUMERICAL_MATERIAL, plus P41 VERIFICATION_CONTRACT_DRIFT.

- Verification recomputes in a disposable sandbox and compares semantically with frozen evidence; it never writes frozen evidence. Replacing evidence is the explicit `engiproof regenerate` operation, not exposed through MCP.
- A numeric change is material when it crosses a declared study/comparison tolerance, changes a value at published precision where that is the applicable source boundary, or changes any evidence status, discrepancy, classification, qualification or engineering interpretation.
- P43 declares `rtol=1e-6`, `atol=1e-5` for cross-platform recomputation equivalence, with a hard guard that every Table 1 eigenvalue keeps its 3-decimal rounded value. This is not an engineering acceptance or validation tolerance.
- Historical byte hashes are preserved as recorded. New text provenance uses the checkout-independent canonical identity `text/lf-v1`.


## D-006 — P45 Phase 1 freeze

Local Windows verification `28_VERIFY_P45_PHASE1_WINDOWS.bat` reported `=== P45 PHASE1 VERIFY PASS ===` after PR #5 was merged into `develop` (`cb2a595`); `continuity-audit` PASS on a clean `develop`; `checkpoint --bundle` PASS (bundle SHA-256 `40175f054d444a018e8954ecb8a5c8e57c9a0d793a1e0441aa214af091f14557`).

- P45 (Safai 1983) is frozen as `CONDITIONAL` evidence at Phase 1.
- P45-D001 through P45-D006 remain `OPEN`; none is closed or corrected.
- Reproduction of the nonlinear dynamic riser responses (Figures 4-9, 11) remains `BLOCKED`: the paper does not give theta/beta/lambda, the iteration tolerance, structural damping, the discretisation of the comparison cases, the float properties or the tension unit.
- No tuning and no inferred completion of missing inputs. No `SOLVER_NEW` evidence.
- Qualification remains `NOT_GRANTED`. P45 stays outside the live registry.
- **Addendum, 28 September 2026 (after F22).** The original PASS banner is no longer treated as authoritative evidence. At the time, `engiproof.cmd` swallowed exit codes (F22), so that banner certified only the `python -m unittest` steps, not `engiproof verify P45`. After the dispatcher fix (`c62f038`), the owner re-ran `28_VERIFY_P45_PHASE1_WINDOWS.bat` on the PR #8 branch (`bab6764`), and it reported `=== P45 PHASE1 VERIFY PASS ===` with every `call engiproof` step's exit code checked. Environment: Windows 10 AMD64, CPython 3.12.10, NumPy 2.5.3. Result: `verify P45` = PASS_SOURCE_EXTERNAL; reproduction classes BYTE_ONLY 1, NUMERICAL_NONMATERIAL 1, 0 material. The only file modified was `engiproof/studies/P45/evidence_graph.json`, from graph-sync per-run counters (Q7); it was not committed. Windows CI also verifies P45 on Python 3.10 and 3.13. This post-F22 run is the authoritative local P45 Windows verification, alongside CI. P45 engineering evidence, discrepancies, decisions and qualification are unchanged.


## D-007 — Cross-environment recomputation equivalence (APPROVED by Zhiqiang Gu, 28 September 2026)

The first CI run on Windows and macOS, and the first CI run of the frozen non-live studies, found the following (failure register F20/F21 in `publication/PAPER_A_ENGIPROOF/PAPER_A_READINESS_REVIEW.md`). None of it changes engineering evidence.

- **Provenance-hash inheritance.** A SHA-256 field that identifies another regenerated artifact of the same study inherits that artifact's classification. Any other hash change remains `MATERIAL_NON_NUMERIC` unless it is a line-ending rendering of the same file. Case: P38 manifest hashes of CSVs that changed non-materially.
- **Path-separator rendering.** Dictionary key sets that differ only by `\` vs `/` are `ENVIRONMENT_METADATA`, and their values are still compared. Case: the P38 runner uses `str(Path)` keys (runner fix deferred to the next approved regeneration, WORK_QUEUE Q9).
- **P45 scoped tolerance.** A path-scoped recomputation tolerance (`rel 1e-6`, `abs 1e-7`) applies only to `.appendix1_checks.independent_fe_comparison` in `phase1_summary.json`. The study-wide default (`1e-9`/`1e-12`) is unchanged, and the engineering statement `appendix1_matches_independent_fe` (residual < 1e-6) is compared exactly. Measured variation: ≤ 2.9e-7 abs on FE outputs; ≤ 1e-8 abs on the ~3e-8 residual.
- Environment fields (`verification_environment`, `frozen_environment_declared`) are verification output only. `ENVIRONMENT_KEYS` is not broadened, and frozen evidence is untouched.
- None of these is an engineering acceptance or validation tolerance.

Approval conditions, as stated by the owner:
- D-007 covers cross-environment recomputation equivalence only.
- No frozen engineering result changes, no discrepancy is closed, and qualification is unchanged.
- **Scoped P45 tolerance.** Accepted for the Appendix-1 independent FE comparison only; the study default is unchanged, and `appendix1_matches_independent_fe` is still checked exactly.
- **Hash inheritance.** Accepted provided the referenced artifact's own classification controls the inherited one.
- **Path-separator keys.** Treated as `ENVIRONMENT_METADATA` only when the normalised keys match and all corresponding values are still compared.
- **P38 runner cleanup.** Stays as WORK_QUEUE Q9; no silent regeneration now.


## D-008 — Taxonomy approval and first human discrepancy decisions (G1/G2)

Approved by Zhiqiang Gu on 28 September 2026.

- **Taxonomy (G2).** The controlled taxonomy and the proposed mapping of all 19 records are approved as documented. Approvals are recorded append-only (`engiproof/contracts/discrepancy_taxonomy_mapping.json`, one `*-TAX-001` review per record). No observation, value, status, qualification or frozen assessment was rewritten to apply the labels, and legacy `classification_hint` values stay unchanged.
- **Decisions (G1).** Recorded in `engiproof/studies/<ID>/discrepancy_decisions.json`, each with reviewer, rationale and evidence references:

  | Record | Decision | Effect |
  |---|---|---|
  | P45-D004 | ACCEPTED_WITH_RATIONALE | Unblocks |
  | P41-D002 | ACCEPTED_WITH_RATIONALE | Unblocks |
  | P43-D001 | DEFERRED | Keeps blocking; the closure requirements ask for an erratum or author clarification. It was not accepted just to clear the gate. |
  | P43-D002 | DEFERRED | Keeps blocking (same reason). |
  | P44-D001 | DEFERRED | Keeps blocking. |
  | P16-D001 | BOUNDED | Formalises the existing bounded status. |
  | P36-D001 | BOUNDED | Formalises the existing bounded status; in-sample, not held-out validation. |

- Gate evidence before and after: `publication/PAPER_A_ENGIPROOF/G1_GATE_EVIDENCE.json`.
  - P45 blockers go from 6 to 5.
  - P41 blockers go from 2 to 1.
  - P43 and P44 are unchanged.
  - P16 and P36 stay ready.
- No discrepancy record was edited. Qualification remains NOT_GRANTED everywhere.


## D-009 — P44 qualification metadata consistency (SA-2) and Paper A source-audit wording (SA-3, SA-10)

Approved by Zhiqiang Gu on 28 September 2026.

- **SA-2 (metadata-consistency correction).**
  - Found by the Paper A source audit: `engiproof/studies/P44/study.json` had no structured `qualification` field. Its recorded limitations already stated "Engineering qualification is NOT_GRANTED", and D-004 froze P44 with qualification NOT_GRANTED. The framework default `NOT_CLAIMED` had therefore been written into `engiproof/studies/P44/evidence_graph.json`.
  - Change: `"qualification": "NOT_GRANTED"` was added to the P44 manifest, and the graph was resynced with `graph-sync P44`.
  - Graph after resync: qualification NOT_GRANTED; 16 nodes and 16 edges, 0 added; `graph-audit` PASS, coverage 1.0. The per-run sync counters were rewritten, which is the known file-idempotency item (Q7).
  - This is not a new qualification decision and not a promotion. No P44 result, comparison, discrepancy or decision changed.
  - Three result files record no qualification field: `papers/P41/results/phase3_global_buckling_summary.json` and `papers/P42/results/phase1_summary.json`, `phase2_analytical_stress_summary.json`. They are left unchanged. The Paper A wording is narrowed to "every result artifact that carries a qualification field".
- **SA-3 (no new discrepancy).**
  - P40 Eq. (6), PIP-1 gives 0.5654599 against a printed 0.56 (difference 0.00546, about 0.98% relative). This is close engineering agreement, only marginally outside the strict two-decimal rounding interval.
  - The "within the two-decimal source precision" wording is replaced in `papers/P40/README.md`, in the PA-06 evidence note and in the manuscript.
  - P40-D001 remains the materially larger discrepancy: Eq. (9), PIP-3, 0.705666 against 0.66.
- **SA-10.** In the Paper A abstract, "independent formulations decide the direction of five numerical conflicts" becomes "independent checks and source-consistency checks clarify five source conflicts". Not all five records are numerical conflicts, and not all are decided by methodologically independent formulations.

## D-010 — Licence: Apache License 2.0 from v0.2.0

Decided by Zhiqiang Gu on 28 September 2026.

- EngiProof is released under Apache-2.0 from v0.2.0: `LICENSE.txt` (the full licence text) and `NOTICE`. It replaces the previous all-rights-reserved notice.
- Reasons: reproducible, open engineering software; academic and industrial reuse; a standard SPDX licence for software citation and Zenodo; clear redistribution terms with an explicit patent grant.
- Licence and provenance audit of the tracked repository (392 files), done before applying the licence:
  - No vendored third-party code. Every commit is by the owner, including AI-assisted work, which is disclosed.
  - Runtime dependencies (NumPy, pypdf, fontTools, optional MCP SDK) are installed separately under their own permissive licences.
  - No source PDFs or publisher rasters are tracked. The only tracked PDF is the owner's own Paper A draft v0.1, which has no embedded images.
  - Third-party-derived content is limited to factual reference values transcribed or digitised from the cited publications (`papers/*/reference/`, published values in manifests), bibliographic records, and short caption and footer fragments in test fixtures and source-review notes.
- `NOTICE` states that third-party publications keep their original rights and are neither distributed nor relicensed. Apache-2.0 covers only EngiProof's own contributions.
- Historical v0.1.x release manifests (`RELEASE_MANIFEST.json`, `SHA256SUMS.txt`) record the licence file of that release and are left unchanged.
- Trademark (added 28 September 2026, owner's decision): `NOTICE` and the README state that EngiProof™ is a trademark of Zhiqiang Gu. Apache-2.0 does not grant permission to use the name, logo, or branding except as necessary to accurately describe the origin of the software; this is consistent with Apache-2.0 section 6. The ™ symbol claims the mark only. ® is not used unless the mark is registered. Registration (for example, a word mark at Patentstyret) is a separate decision for the owner.
- Paper A target journal confirmed by the owner on 28 September 2026: Advances in Engineering Software. The stale pending owner action in PROJECT_STATE is closed.
