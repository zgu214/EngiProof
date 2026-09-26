@echo off
setlocal
cd /d "%~dp0"
echo === EngiProof v0.2.0-dev2 verify ===
python -m pip install -e .
if errorlevel 1 exit /b 1
engiproof --version
engiproof doctor
if errorlevel 1 exit /b 1
python -m unittest tests.test_ingestion -v
if errorlevel 1 exit /b 1
engiproof verify-all
if errorlevel 1 exit /b 1
echo.
echo === ENGIPROOF V0.2.0-DEV2 CORE VERIFY PASS ===
endlocal
