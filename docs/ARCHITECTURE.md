# EngiProof architecture

```text
Published source / code / data
           |
           v
     Source contract
           |
           v
  Paper-specific runner ------> machine-readable results
           |                              |
           v                              v
 Independent mechanics       published comparison
           \                              /
            \                            /
             +---- evidence manifest ----+
                        |
                        v
                 callable tool API
                        |
          +-------------+-------------+
          |                           |
          v                           v
      CLI / JSON                 agent / MCP adapter
          |
          v
 engineering library / report / textbook / product solver
```

The key boundary is that **execution is not qualification**. A study can be runnable while still `DRAFT`, `REPRODUCED`, `COMPARED`, `CONDITIONAL`, or another explicitly defined evidence state.
