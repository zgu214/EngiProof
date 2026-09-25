# Windows quick start — detailed

## A. First installation

Open **Command Prompt** in the extracted EngiProof folder and run:

```bat
00_SETUP_WINDOWS.bat
```

The script:

1. finds `python` or `py -3`;
2. creates `.venv`;
3. upgrades `pip`;
4. installs EngiProof in editable mode plus NumPy;
5. runs `engiproof doctor`;
6. runs the unit tests.

If successful you will see `SETUP PASS`.

## B. Run the first studies

```bat
01_DEMO_WINDOWS.bat
```

It demonstrates:

```bat
engiproof list
engiproof tool P08 critical_temperature_eq11 --params "{\"length_m\":100}"
engiproof tool P12 table4_fit_force_MN --params "{\"beta\":0.6,\"clearance_mm\":12}"
```

## C. Recalculate evidence files

```bat
.venv\Scripts\activate
engiproof run P08
engiproof run P12
```

This rewrites only each study's declared result files under `results/`.

## D. Verify all studies

```bat
02_VERIFY_WINDOWS.bat
```

Or manually:

```bat
.venv\Scripts\activate
engiproof verify-all
python -m unittest discover -s tests -v
```

`PASS_SOURCE_EXTERNAL` means the source PDF is not locally present but the source contract and tests pass. If you legally possess the PDF, put it in `01_doc/` under the exact canonical filename; EngiProof will hash-check it.

## E. JSON for agents / automation

```bat
engiproof --json list
engiproof --json verify-all
engiproof --json results P08
```

The JSON output is intended for Codex/agent workflows and downstream reports.
