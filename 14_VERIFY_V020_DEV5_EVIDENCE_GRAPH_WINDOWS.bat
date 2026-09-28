@echo off
setlocal
echo === EngiProof v0.2.0-dev5 evidence graph automation ===
python -m pip install -e .
if errorlevel 1 exit /b 1
engiproof --version
python -m unittest tests.test_evidence_graph_sync tests.test_discrepancy_engine tests.test_discrepancy_decisions tests.test_p40_engiproof -v
if errorlevel 1 exit /b 1
engiproof graph-sync P40
if errorlevel 1 exit /b 1
engiproof graph-audit P40
if errorlevel 1 exit /b 1
engiproof discrepancy-gate P40
engiproof promotion-gate P40
echo Expected: graph audit PASS, but P40 remains BLOCK_PROMOTION because the latest human decision is DEFERRED.
echo === DEV5 VERIFY PASS ===
