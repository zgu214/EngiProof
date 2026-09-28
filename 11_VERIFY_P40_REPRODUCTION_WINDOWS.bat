@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

echo === EngiProof P40 reproduction checkpoint ===
%PY% -m unittest tests.test_p40_engiproof -v || exit /b 1
%PY% papers\P40\run_calculation.py || exit /b 1
%PY% run_engiproof.py verify P40 || exit /b 1
%PY% run_engiproof.py tool P40 table2_reproduction_summary --params "{}" || exit /b 1

echo.
echo === P40 REPRODUCTION VERIFY PASS ===
endlocal
