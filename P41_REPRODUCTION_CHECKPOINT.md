# P41 reproduction checkpoint

## Study

**Global Buckling of Pipe-in-Pipe: Structural Response and Design Criteria**  
Goplen, Fyrileiv, Grandal & Børsheim (2011)  
OMAE2011-49960  
DOI: `10.1115/OMAE2011-49960`

## First reproduced chain

```text
Table 1 geometry / E
  -> independent steel area
  -> independent EA
  -> Table 2
  -> Eq. (6) inner load share
  -> Eq. (7) outer load share
  -> Eq. (8) total force identity
```

## Independent results

Using Table 1 geometry:

- inner steel area = `0.0127252174 m²` vs extracted Table 2 `0.012725 m²`;
- outer steel area = `0.0240543896 m²` vs extracted Table 2 `0.024054 m²`;
- inner EA = `2.532318261e9 N` vs extracted Table 2 `2.532e9 N`;
- outer EA = `4.979258637e9 N` vs extracted Table 2 `4.979e9 N`.

Using `f_s = 471 N/m`:

- Eq. (6) inner share = `158.7845 N/m`;
- Eq. (7) outer share = `312.2155 N/m`;
- Eq. (8) total = `471.0 N/m`.

The extracted Table 2 text reports `153` and `312 N/m`. The outer value agrees to integer rounding. The inner value does not.

## Evidence decision

Do **not** label the inner value as a confirmed published inconsistency yet.

Current classification: `SOURCE_TRANSCRIPTION_UNCERTAINTY`.

Required closure:

1. visually inspect the original Table 2 inner force-increment cell;
2. if it reads `159`, correct the machine-readable extraction and close as extraction error;
3. if it reads `153`, retain the discrepancy and investigate the published calculation without tuning inputs.

## Status

- evidence status: `CONDITIONAL`;
- source identity: title/year match; DOI externally confirmed but not found in extracted PDF text;
- global-buckling FE reproduction: not performed;
- qualification: `NOT_GRANTED`;
- live registry: no.
