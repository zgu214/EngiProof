@echo off
setlocal
echo === EngiProof P42 Phase 1 verification ===
python -m pip install -e .
if errorlevel 1 exit /b 1
python -m unittest tests.test_p42_phase1 -v
if errorlevel 1 exit /b 1
python papers\P42\run_calculation.py
if errorlevel 1 exit /b 1
engiproof verify P42
engiproof graph-sync P42
engiproof graph-audit P42
engiproof pipeline P42
echo === P42 PHASE1 VERIFY PASS ===
