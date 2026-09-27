# EngiProof — Low-Budget Continuity Playbook

When remaining model budget is low:

1. Finish only the current bounded verification gate.
2. Update `PROJECT_STATE.json`, `HANDOVER_CURRENT.md`, and `CHAT_COMPACT_CURRENT.md`.
3. Run `engiproof continuity-audit`.
4. Run `engiproof checkpoint --bundle`.
5. Copy the current checkpoint ZIP to the private archive.
6. Commit and push.
7. Do not start another large paper/reproduction chain until budget resets.
8. Resume with `NEW_CHAT_BOOTSTRAP.md`.

The goal is zero-loss continuation, not squeezing one more incomplete study into the remaining budget.
