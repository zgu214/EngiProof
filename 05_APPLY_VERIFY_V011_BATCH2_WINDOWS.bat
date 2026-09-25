@echo off
setlocal
cd /d "%~dp0"
echo === EngiProof v0.1.1 Batch 2: cleanup + verify ===
for %%F in (Current Detected Downloading Future Resolved Updating) do (
  if exist "%%F" (
    echo Removing accidental shell-output file: %%F
    del /Q "%%F"
  )
)
python -m pip install -e .
if errorlevel 1 exit /b 1
python -m unittest discover -s tests -v
if errorlevel 1 exit /b 1
engiproof verify-all
if errorlevel 1 exit /b 1
engiproof discrepancy P29
if errorlevel 1 exit /b 1
engiproof tool P16 table2_cumulative_displacement_mm --params "{\"cycle\":6}"
if errorlevel 1 exit /b 1
engiproof tool P29 positive_frequency_integral --params "{\"mass_ratio\":0.853,\"gamma\":0.2,\"zeta_t\":0.1}"
if errorlevel 1 exit /b 1
engiproof tool P36 equation8_ratio --params "{\"diameter_ratio\":0.6}"
if errorlevel 1 exit /b 1
git status -sb
echo === BATCH 2 VERIFY PASS ===
endlocal
