@echo off
setlocal
echo === EngiProof v0.2.0-dev8 three-layer continuity architecture ===
echo [1/6] Install editable package
python -m pip install -e .
if errorlevel 1 goto :fail
echo [2/6] Runtime version
call engiproof --version
if errorlevel 1 goto :fail
echo [3/6] Continuity tests
python -m unittest tests.test_continuity -v
if errorlevel 1 goto :fail
echo [4/6] Continuity audit
call engiproof continuity-audit
if errorlevel 1 goto :fail
echo [5/6] Build checkpoint bundle
call engiproof checkpoint --bundle
if errorlevel 1 goto :fail
echo [6/6] Doctor
call engiproof doctor
if errorlevel 1 goto :fail
echo.
echo === DEV8 CONTINUITY VERIFY PASS ===
echo Generated private backup bundle:
echo checkpoints\EngiProof_CHECKPOINT_CURRENT.zip
exit /b 0
:fail
echo.
echo === DEV8 CONTINUITY VERIFY FAIL ===
echo ERRORLEVEL=%ERRORLEVEL%
exit /b 1
