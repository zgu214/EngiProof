# EngiProof — Persistent Engineering & Development Contract

EngiProof converts published engineering research into source-bounded, reproducible, independently checked engineering evidence.

## Non-negotiable engineering rules

1. Preserve `PUBLISHED`, `INDEPENDENT`, and `SOLVER_NEW`.
2. Candidate extraction is not evidence.
3. Code execution is not verification.
4. Verification is not engineering qualification.
5. Never tune unknown/source inputs merely to force agreement.
6. Preserve published inconsistencies and implementation gaps explicitly.
7. Do not silently correct source values, units, equations, or conventions.
8. Do not redistribute copyrighted source PDFs/raster figures in the public repository.
9. Do not persist machine-specific absolute paths, usernames, machine names, or drive letters.
10. Every evidence-producing calculation must have persistent runnable code, traceable inputs/results, and tests.

## Continuity contract

EngiProof must not depend on one chat, model, developer, or hidden assistant memory.

Before resuming, read:
`PROJECT_STATE.json`, `HANDOVER_CURRENT.md`, `CHAT_COMPACT_CURRENT.md`,
`WORK_QUEUE.md`, `BLOCKERS.md`, `DECISIONS.md`,
`ROADMAP_v0.2.0.md`, `PROGRESS_v0.2.0.md`,
and the relevant study source contract/manifest.

Verify actual branch, HEAD, git status, current checkpoint and current study before claiming completion.

## Checkpoint contract

At each meaningful checkpoint:
focused tests -> engineering runner -> persistent results -> comparisons/discrepancies ->
graph-sync/audit -> handover/compact/state -> continuity-audit -> checkpoint bundle -> commit/push.

## Windows batch rule

Inside a `.bat`/`.cmd`, use `call engiproof ...` because the dispatcher is `engiproof.cmd`.

## Human-review boundary

Routine implementation/tests/evidence sync may proceed autonomously. Human approval remains required for genuine physics/scope changes, qualification decisions, permissions and material source-interpretation decisions.
