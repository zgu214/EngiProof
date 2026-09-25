# EngiProof v0.1.1 contracts

EngiProof separates six contracts so that code execution cannot silently become engineering evidence.

| Contract | Purpose | Key rule |
|---|---|---|
| Study | Binds a source-bounded paper/case to runners, tools, evidence and tests | A runnable study may still be `CONDITIONAL` or `BLOCKED` |
| Source | Canonical source identity, DOI and expected SHA-256 | Copyrighted source may remain external |
| Evidence | Classifies each claim as `PUBLISHED`, `INDEPENDENT`, or `SOLVER_NEW` | Evidence class must not be inferred from code ownership |
| Comparison | States the reference population, metric and boundary | In-sample published-fit checks are not independent validation |
| Discrepancy | Preserves unresolved disagreement and engineering interpretation | Do not tune unknowns to force agreement |
| Verification | Software/source/contract verification record | Verification is not engineering qualification |

Machine-readable definitions are in `engiproof/contracts/contracts.json`.

## Evidence graph

A study may provide an `engiproof.evidence_graph/1.0` document linking:

`source -> target -> implementation -> calculation/check -> comparison -> discrepancy -> interpretation/boundary`

P38 is the first study to ship this complete graph.
