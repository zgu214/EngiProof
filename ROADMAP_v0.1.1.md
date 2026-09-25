# EngiProof v0.1.1 Roadmap

## Release objective

Turn EngiProof from a two-study prototype into a reusable engineering-evidence runtime.

The release must demonstrate a complete path:

Published source
→ source contract
→ reproducible calculation
→ independent check
→ published comparison
→ discrepancy analysis
→ evidence classification
→ callable engineering method
→ machine-readable verification record

## Priority 1 — Generic contracts

Implement reusable, versioned contracts for:

1. Study Contract
2. Source Contract
3. Evidence Contract
4. Comparison Contract
5. Discrepancy Contract
6. Verification Contract

No evidence status may be promoted merely because code executes.

Required evidence classes remain:

- PUBLISHED
- INDEPENDENT
- SOLVER_NEW

Required status distinctions must include at minimum:

- DRAFT
- SOURCE_READY
- REPRODUCED
- COMPARED
- VERIFIED
- CONDITIONAL
- BLOCKED

Engineering qualification remains separate from computational verification.

## Priority 2 — P38 integration

P38 is the first full EngiProof showcase study.

Reuse existing verified material where available:

- source contract
- calculation manifest
- calculated curves
- reference comparisons
- Table 2 checks
- independent work checks
- summary data
- HTML/report evidence
- regression tests

P38 must demonstrate:

source → calculation → independent check → comparison → discrepancy → evidence result

Do not change existing numerical results merely to fit the new framework.

Do not introduce new FE work in this release.

## Priority 3 — Additional studies

Integrate, subject to source readiness:

- P16
- P29
- P36

Each study must retain paper-specific runnable calculations while using shared EngiProof infrastructure.

Unsupported inputs must remain explicit.

Do not tune missing parameters to force agreement.

## Priority 4 — Provenance

Every result must be able to identify:

- study ID
- source identifier
- DOI where available
- expected source SHA-256 where applicable
- method/tool
- input parameters
- output
- evidence class
- evidence status
- comparison reference
- limitations
- software version

## Priority 5 — Evidence graph

Add machine-readable relationships between:

source
→ equation/table/figure
→ implementation
→ calculation
→ comparison
→ independent check
→ discrepancy
→ engineering interpretation

The evidence graph must be queryable through the CLI/JSON interface.

## Priority 6 — CLI

Retain existing commands and extend without breaking v0.1.0 behavior.

Target additions:

engiproof schema
engiproof evidence <study>
engiproof compare <study>
engiproof provenance <study>
engiproof discrepancy <study>

JSON output is first-class.

## Priority 7 — Tests

Requirements:

- existing v0.1.0 tests remain passing
- schema validation tests
- provenance tests
- comparison tests
- discrepancy tests
- P38 reproduction tests
- fresh-install CI
- deterministic outputs where applicable

Python 3.10, 3.12 and 3.13 CI must remain green.

## Non-goals for v0.1.1

Do not prioritize:

- GUI
- cosmetic website work
- commercial packaging
- new FE solver development
- unsupported engineering qualification claims
- bulk paper count without reproduction evidence

## Release gate

v0.1.1 is ready only when:

- generic contracts exist and are tested
- P08 and P12 remain backward compatible
- P38 is integrated as a complete evidence-chain study
- at least one additional study is integrated if source-ready
- provenance is machine-readable
- comparison/discrepancy evidence is explicit
- all tests pass
- CI passes on supported Python versions
- no copyrighted source PDFs are distributed
- no engineering qualification is implied without evidence