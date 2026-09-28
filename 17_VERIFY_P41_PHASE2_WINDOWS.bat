@echo off
setlocal
echo === EngiProof P41 Phase 2 verification ===
python -m pip install -e .
if errorlevel 1 exit /b 1
python -m unittest tests.test_p41_engiproof tests.test_p41_phase2 -v
if errorlevel 1 exit /b 1
engiproof tool P41 table3_bonding_summary
engiproof discrepancy-audit P41
engiproof graph-sync P41
engiproof graph-audit P41
echo === P41 PHASE2 VERIFY PASS ===
