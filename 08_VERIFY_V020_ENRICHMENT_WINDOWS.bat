@echo off
setlocal
cd /d "%~dp0"
echo === EngiProof v0.2.0-dev1 source enrichment verification ===
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe -m pip install -e .
  .venv\Scripts\python.exe -m unittest discover -s tests -v
  .venv\Scripts\python.exe run_engiproof.py verify-all
  .venv\Scripts\python.exe run_engiproof.py --version
) else (
  python -m pip install -e .
  python -m unittest discover -s tests -v
  python run_engiproof.py verify-all
  python run_engiproof.py --version
)
if errorlevel 1 exit /b 1
echo === V0.2.0 DEV1 ENRICHMENT VERIFY PASS ===
endlocal
