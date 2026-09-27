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
