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
