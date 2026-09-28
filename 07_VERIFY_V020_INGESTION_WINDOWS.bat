@echo off
setlocal
cd /d "%~dp0"
echo === EngiProof v0.2.0-dev0 ingestion verification ===
python -m pip install -e .
if errorlevel 1 exit /b 1
python -m unittest discover -s tests -v
if errorlevel 1 exit /b 1
engiproof doctor
if errorlevel 1 exit /b 1
engiproof verify-all
if errorlevel 1 exit /b 1
engiproof schema ingestion
if errorlevel 1 exit /b 1
echo === V0.2.0 INGESTION VERIFY PASS ===
