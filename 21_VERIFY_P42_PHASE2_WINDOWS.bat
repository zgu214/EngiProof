@echo off
setlocal
echo === EngiProof P42 Phase 2 verification ===
python -m pip install -e .
if errorlevel 1 exit /b 1
python -m unittest tests.test_p42_phase1 tests.test_p42_phase2 -v
if errorlevel 1 exit /b 1
python papers\P42\run_calculation.py
if errorlevel 1 exit /b 1
engiproof tool P42 phase2_analytical_stress_summary
engiproof discrepancy-audit P42
engiproof graph-sync P42
engiproof graph-audit P42
engiproof pipeline P42
echo === P42 PHASE2 VERIFY PASS ===
