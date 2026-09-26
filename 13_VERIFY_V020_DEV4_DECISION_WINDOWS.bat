@echo off
setlocal
echo === EngiProof v0.2.0-dev4 discrepancy decision workflow ===
python -m pip install -e .
if errorlevel 1 exit /b 1
engiproof --version
python -m unittest tests.test_discrepancy_engine tests.test_discrepancy_decisions tests.test_p40_engiproof -v
if errorlevel 1 exit /b 1
engiproof discrepancy-gate P40
engiproof promotion-gate P40
echo Expected: P40 remains blocked until an explicit documented human decision is recorded.
echo === DEV4 VERIFY PASS ===
