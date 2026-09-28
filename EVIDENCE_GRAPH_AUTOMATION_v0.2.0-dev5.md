# EngiProof v0.2.0-dev5 — Evidence-Graph Auto-Expansion

Dev5 makes the evidence graph a synchronized provenance artifact rather than a manually maintained diagram.

## Commands

```bat
engiproof graph-sync P40
engiproof graph-audit P40
```

`graph-sync` is additive and idempotent. It preserves existing hand-authored nodes and edges while adding missing provenance for callable tools, comparisons, discrepancies, automated discrepancy assessments and append-only human discrepancy decisions.

A human decision such as `DEFERRED` is represented explicitly in the graph and remains promotion-blocking through the discrepancy gate. Graph synchronization never changes engineering qualification.

`graph-audit` checks representation coverage only. `PASS` means the expected provenance objects are represented; it does not imply that the study is verified, accepted, or qualified.
