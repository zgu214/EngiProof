# EngiProof v0.2.0-dev4 — Human Discrepancy Decision Workflow

Append-only human review for discrepancy blockers.

Dispositions: `RESOLVED`, `BOUNDED`, `ACCEPTED_WITH_RATIONALE`, `DEFERRED`.

Unblocking decisions require reviewer, substantive rationale, and at least one evidence reference. `DEFERRED` remains blocking. No decision grants engineering qualification.

```bat
engiproof discrepancy-decisions P40
engiproof discrepancy-decide P40 P40-D001 --disposition BOUNDED --rationale "..." --reviewer "..." --evidence-ref "source:..." --evidence-ref "analysis:..."
engiproof discrepancy-gate P40
engiproof promotion-gate P40
```

Do not record closure merely to make a gate pass.
