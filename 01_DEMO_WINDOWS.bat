@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Run 00_SETUP_WINDOWS.bat first.
  pause
  exit /b 1
)
echo === LIVE STUDIES ===
call engiproof.cmd list
echo.
echo === P08 EXAMPLE ===
call engiproof.cmd tool P08 critical_temperature_eq11 --params "{\"length_m\":100}"
echo.
echo === P12 EXAMPLE ===
call engiproof.cmd tool P12 table4_fit_force_MN --params "{\"beta\":0.6,\"clearance_mm\":12}"
echo.
echo === VERIFY ALL ===
call engiproof.cmd verify-all
pause
