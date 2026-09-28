# EngiProof v0.2.0

Draft GitHub release notes. The tag is created on `main` only on the owner's explicit approval.

EngiProof converts selected published engineering methods into source-bounded, reproducible and independently checked evidence. This release is the software state cited by Paper A (Advances in Engineering Software submission).

## Scope

- Six frozen `CONDITIONAL` evidence cases, P40–P45: offshore and subsea structural mechanics sources published 1976–2019, including a 1983 scanned source. Engineering qualification is `NOT_GRANTED` in every study.
- Non-mutating verification (`engiproof verify`, `verify-all`), with semantic comparison of regenerated artifacts against frozen evidence. CI verifies all 12 studies on Linux (Python 3.10/3.12/3.13), Windows (3.10/3.13) and macOS arm64 (3.13).
- A controlled discrepancy taxonomy and append-only human decisions that gate promotion (DECISIONS.md D-007, D-008, D-009).
- The Paper A manuscript sources, with tables generated from repository data and a prose facts check.

## Not included

- Copyrighted source PDFs and publisher figures. Each source is identified by its SHA-256 and bibliographic record.
- Any engineering qualification, extraction-accuracy figure or generality claim beyond the six cases.

See `CHANGELOG.md` for details.
