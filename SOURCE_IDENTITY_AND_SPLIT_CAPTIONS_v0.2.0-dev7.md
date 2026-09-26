# EngiProof v0.2.0-dev7 — publication-year semantics and split captions

P42 exposed two generic ingestion issues.

## Publication-year semantics

The P42 first page contains:
- DOI `10.1016/j.marstruc.2018.09.010`;
- received/revised/accepted dates in 2018;
- `Marine Structures 64 (2019) 401–420`;
- copyright 2018.

The configured year `2019` is therefore the publication year. Dev6 incorrectly treated an administrative/copyright year as the source year and raised a conflict.

Dev7 now distinguishes:
- `PUBLICATION` year evidence;
- `SECONDARY` year evidence such as received/accepted/copyright dates.

Only a conflicting publication-year candidate can create a year conflict.

## Split captions

Elsevier-style tables may use:
`Table 1`
followed on the next line by
`Geometric parameters ...`

Dev7 recognizes this as a true caption anchor while preserving conservative rejection of ordinary in-text references.

The change is generic and is tested independently of P42.
