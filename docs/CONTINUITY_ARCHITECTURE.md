# EngiProof Three-Layer Continuity Architecture

## Layer 1 — Repository source of truth
Git is authoritative for code, tests, study manifests, source contracts, evidence, decisions and history. Chat claims never override repository evidence.

## Layer 2 — Continuity control plane
Core files:
`AGENTS.md`, `PROJECT_STATE.json`, `HANDOVER_CURRENT.md`,
`CHAT_COMPACT_CURRENT.md`, `WORK_QUEUE.md`, `BLOCKERS.md`,
`DECISIONS.md`, `NEW_CHAT_BOOTSTRAP.md`.

`PROJECT_STATE.json` is machine-readable current state.
`HANDOVER_CURRENT.md` is the primary engineer handover.
Git history carries detailed history.

## Layer 3 — Conversation convenience
ChatGPT/Codex/other sessions accelerate work but are replaceable. Critical engineering state must never exist only in chat.

## Commands

```bat
engiproof continuity-audit
engiproof checkpoint
engiproof checkpoint --bundle
```

## Private cloud backup

Recommended private structure:

```text
EngiProof_Private/
    source_papers/
    checkpoints/
        EngiProof_CHECKPOINT_CURRENT.zip
        archive/
    releases/
```

Do not put copyrighted source PDFs in the public GitHub repository.

## Cadence
Checkpoint after major paper phases/dev versions, before new long chats, before handoff, before long breaks, and around major merges/releases. Do not wait for context exhaustion.
