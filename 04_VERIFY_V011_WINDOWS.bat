@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
python -m pip install -e .
if errorlevel 1 exit /b 1
python -m unittest discover -s tests -v
if errorlevel 1 exit /b 1
engiproof verify-all
if errorlevel 1 exit /b 1
engiproof evidence P38
engiproof discrepancy P38
echo.
echo EngiProof v0.1.1 P38 verification PASS
endlocal
