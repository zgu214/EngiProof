# EngiProof architecture

```text
Published source / code / data
           |
           v
     Source contract
           |
           v
      Study contract
           |
   +-------+---------+
   |                 |
   v                 v
Published method   Independent check
   |                 |
   +-------+---------+
           v
       Comparison
           |
           v
      Discrepancy
           |
           v
      Evidence graph
           |
   +-------+---------+----------------+
   |                 |                |
   v                 v                v
CLI / JSON       callable tools     reports/adapters
```

The runtime separates **source**, **study**, **evidence**, **comparison**, **discrepancy** and **verification** contracts. Execution is never treated as qualification.

P38 is the first complete chain: published Figure/Table/Equation evidence -> deterministic reconstruction -> independent work-balance check -> comparison -> explicit Figure 11 discrepancy -> engineering interpretation. The published FE points remain source reference data; EngiProof does not claim to recreate the source shell FE model.
