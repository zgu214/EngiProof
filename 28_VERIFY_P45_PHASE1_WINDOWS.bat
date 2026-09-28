@echo off
setlocal
echo === EngiProof P45 Phase 1 nonlinear dynamic riser evidence ===

echo [1/8] Install editable package
python -m pip install -e .
if errorlevel 1 goto :fail

echo [2/8] P45 Phase 1 tests
python -m unittest tests.test_p45_phase1 -v
if errorlevel 1 goto :fail

echo [3/8] Show Phase 1 summary
call engiproof tool P45 phase1_summary
if errorlevel 1 goto :fail

echo [4/8] Verify (non-mutating: sandboxed recomputation vs frozen evidence)
call engiproof verify P45
if errorlevel 1 goto :fail

echo [5/8] Discrepancy audit
call engiproof discrepancy-audit P45

echo [6/8] Sync + audit evidence graph
call engiproof graph-sync P45
if errorlevel 1 goto :fail
call engiproof graph-audit P45
if errorlevel 1 goto :fail

echo [7/8] Pipeline
call engiproof pipeline P45

echo [8/8] Continuity audit + checkpoint
call engiproof continuity-audit
if errorlevel 1 goto :fail
call engiproof checkpoint --bundle
if errorlevel 1 goto :fail

echo.
echo === P45 PHASE1 VERIFY PASS ===
exit /b 0

:fail
echo.
echo === P45 PHASE1 VERIFY FAIL ===
echo ERRORLEVEL=%ERRORLEVEL%
exit /b 1
