# EngiProof v0.1.0 GitHub-ready R1

Windows command usability repair, 2026-09-25.

- Adds `engiproof.cmd` at repository root.
- After running `00_SETUP_WINDOWS.bat` once, `engiproof ...` works from the repository root even when the parent prompt remains `(base)` or another Conda environment.
- Setup/demo/verify batch files call the local `.venv` explicitly and no longer depend on activation state leaking into the parent shell.
- Removes obsolete internal prototype naming from live CLI study limitations and provenance text.
- Engineering calculations and evidence status are unchanged.
