# EngiProof Development Standard v0.1

## Run Further, Higher, Faster - but always with traceable evidence

**Project:** EngiProof - From Published Research to Verified Engineering  
**Purpose:** A durable development standard for building engineering software that remains valuable even when similar tools appear.  
**Status:** Working development standard  
**Date:** 2026-09-26

### 中文说明

这份文件保存并正式化了我们刚才关于 EngiProof 长期价值、竞争壁垒、代码持久化和开发纪律的回答。  
它不是宣传口号，而是从现在开始用于约束未来开发的工作标准。  

**跑得更远、更高、更快，但任何速度都不能破坏证据链。**  

核心要求：  
工程结果不能只存在于聊天、临时脚本或一次性计算中。  
凡是进入 EngiProof 证据体系的计算，都必须有可运行、可追溯、可测试、可复现的持久源码和证据记录。  

---

## 1. The durable value of EngiProof

Similar software may appear later. That can reduce the value of a generic paper-to-code feature, but it does not automatically reduce the value of EngiProof if the project keeps building the parts that are difficult to copy.

The long-term value of EngiProof is **not simply PDF parsing, equation extraction, or automatic code generation**. Those capabilities will become increasingly common.

The durable value is the complete engineering-evidence chain:

**PDF / paper source -> source fingerprint -> source identity -> target selection -> published-result reproduction -> independent mechanics -> comparison -> discrepancy classification -> human decision record -> evidence graph -> verification tests -> callable engineering method -> qualification boundary**

A competitor can reproduce an interface quickly. Recreating a large body of source-reviewed, independently checked, discrepancy-aware engineering evidence is much harder.

### Durable moat hierarchy

| Layer | Ease of imitation | Long-term value |
|---|---:|---:|
| PDF text extraction | High | Low |
| Equation-to-code generation | High | Low to medium |
| Paper-specific runnable study | Medium | Medium |
| Independent mechanics checks | Medium to hard | High |
| Discrepancy classification and provenance | Hard | High |
| Evidence graph + verification history | Hard | Very high |
| Large reviewed engineering evidence corpus | Very hard | Very high |
| Qualification history and trusted engineering use | Very hard | Strategic |

The goal is therefore not to defend a single algorithm. The goal is to accumulate a **verified engineering evidence corpus** and a rigorous operating system around it.

---

## 2. Core principle: paper-to-code is not enough

EngiProof must always distinguish:

- what the source actually publishes;
- what EngiProof reproduces from the source;
- what EngiProof calculates independently;
- where the two agree;
- where they disagree;
- what the discrepancy means;
- whether the discrepancy is unresolved, bounded, accepted, or deferred;
- whether engineering qualification has or has not been granted.

A successful tool must be able to say **"the paper itself cannot be internally reconciled"** when that is what the evidence shows.

This is more valuable than forcing agreement.

### Never tune away evidence

If a published value, equation, figure, table, or unit cannot be reconciled:

1. preserve the published value exactly;
2. preserve the independent result separately;
3. quantify the difference;
4. classify the discrepancy;
5. record the provenance and review state;
6. do not alter inputs merely to make the values match.

P40, P41, and P42 demonstrate why this matters: numerical-reference mismatch, internal force-balance mismatch, unit inconsistency, and model-form/kinematic difference are not the same failure class.

---

## 3. Permanent repository rule

> **No engineering result used as EngiProof evidence may exist only in a chat, temporary notebook, scratch calculation, or one-off tool call. Every evidence-producing calculation must have a persistent runnable source file in the repository.**

This is a mandatory rule for future development.

### What must be persistent

Engineering evidence should live in version-controlled files such as:

```text
papers/Pxx/
    SOURCE.md
    mechanics.py
    tool_api.py
    run_calculation.py
    inputs/
    reference/
    results/

engiproof/studies/Pxx/
    study.json
    evidence_graph.json

tests/
    test_pxx_*.py
```

Temporary orchestration used to assemble ZIP patches, copy files, or calculate checksums does not need to be retained. The **engineering mechanics, callable methods, inputs, results, comparisons, discrepancies, and tests do**.

This rule protects EngiProof from loss of context, loss of chat history, changes in developers, changes in AI systems, and future maintenance problems.

---

## 4. Development checkpoint standard

Every meaningful development checkpoint should follow the same closure sequence:

```text
source / code change
      |
      v
focused tests
      |
      v
engineering runner
      |
      v
result artifacts
      |
      v
comparison + discrepancy records
      |
      v
graph-sync
      |
      v
graph-audit
      |
      v
pipeline status
      |
      v
HANDOVER_CURRENT.md
CHAT_COMPACT_CURRENT.md
      |
      v
commit / CI
```

### Mandatory checkpoint gates

A checkpoint is not complete merely because the calculation executes.

It should explicitly answer:

- Did the source identity pass?
- Are selected targets structurally ready?
- Are results persisted?
- Are independent checks present where meaningful?
- Are comparisons recorded?
- Are discrepancies retained rather than hidden?
- Is the evidence graph synchronized?
- Does the evidence graph audit pass?
- Is the qualification state explicit?
- Is the current handover updated?

### Graph rule

**Manifest changes make the evidence graph stale until synchronization.**

Therefore, after adding tools, comparisons, discrepancies, assessments, or decisions, always run:

```bat
engiproof graph-sync Pxx
engiproof graph-audit Pxx
```

A failed graph audit caused by missing representation is a provenance/graph synchronization problem, not automatically an engineering-physics failure.

---

## 5. Evidence classes and qualification boundary

EngiProof should keep evidence classes separate:

- **PUBLISHED** - source material, equations, tables, figures, or documented source claims.
- **INDEPENDENT** - calculations or checks independently reconstructed by EngiProof.
- **SOLVER_NEW** - new solver-generated evidence not present in the source.

Evidence status and engineering qualification are not the same thing.

A study can be `REPRODUCED`, `COMPARED`, or `CONDITIONAL` while still having:

```text
qualification = NOT_GRANTED
```

This distinction must never be blurred for convenience.

---

## 6. The real competitive advantage

The strongest future EngiProof asset is not one clever algorithm. It is the cumulative body of engineering evidence:

- hundreds of source fingerprints;
- precise source targets;
- reproduced equations and published results;
- independent mechanical checks;
- regenerated figures and comparison metrics;
- unresolved and resolved discrepancies;
- human review decisions;
- evidence graphs;
- automated tests;
- callable engineering methods;
- explicit limitations and qualification history.

That corpus compounds in value.

Every new paper should improve not only the evidence library but also the generic ingestion and verification framework. A real paper that exposes a new failure mode is useful twice:

1. it becomes an engineering study;
2. it makes the EngiProof framework more robust for all future papers.

---

## 7. Development philosophy

**Run further.** Build beyond isolated paper reproductions into a reusable engineering evidence system.

**Run higher.** Increase the standard of evidence: provenance, independent mechanics, discrepancy handling, reproducibility, and qualification discipline.

**Run faster.** Automate repetitive work, but never automate away engineering judgment, uncertainty, or source boundaries.

Speed is valuable only when the evidence chain remains intact.

The standard for future EngiProof development is therefore:

> **Automate aggressively. Verify independently. Preserve discrepancies. Persist every engineering result. Keep provenance complete. Never claim more than the evidence supports.**

---

## 8. Continuity standard

EngiProof must not depend on one conversation or one developer remembering the project history.

At every development checkpoint maintain:

- `HANDOVER_CURRENT.md` - current engineering state, accepted results, blockers, next authorized work;
- `CHAT_COMPACT_CURRENT.md` - compact conversational/project context for rapid resumption;
- machine-readable study manifests;
- evidence graphs;
- tests and result artifacts.

The repository should become the authoritative memory of the engineering work.

---

## Closing statement

EngiProof should be designed so that the project becomes **more valuable as competing automation becomes more common**, because its advantage shifts from generic automation to accumulated engineering evidence, traceability, discrepancy intelligence, reproducibility, and trust.

The target is not merely to be earlier than others.

The target is to build a system whose evidence base, engineering discipline, and accumulated verification become progressively harder to replicate.

**Run further. Run higher. Run faster. Keep the evidence intact.**
