@echo off
setlocal
cd /d "%~dp0"
echo === EngiProof v0.2.0-dev3 discrepancy automation verify ===
python -m pip install -e . || exit /b 1
engiproof --version || exit /b 1
engiproof doctor || exit /b 1

rem Run in bounded batches. This avoids one large nested unittest process while
rem retaining the full 53-test coverage of this checkpoint.
python -m unittest tests.test_discrepancy_engine tests.test_ingestion tests.test_p16_engiproof tests.test_p29_engiproof tests.test_p36_engiproof tests.test_p38_engiproof tests.test_p40_engiproof tests.test_paper_studies_batch5 -v || exit /b 1
python -m unittest tests.test_engiproof.EngiProofTests.test_doctor tests.test_engiproof.EngiProofTests.test_generic_contracts tests.test_engiproof.EngiProofTests.test_p08_tool tests.test_engiproof.EngiProofTests.test_p12_tool tests.test_engiproof.EngiProofTests.test_p38_tool tests.test_engiproof.EngiProofTests.test_registry tests.test_engiproof.EngiProofTests.test_schema_backward_compatibility -v || exit /b 1
python -m unittest tests.test_engiproof.EngiProofTests.test_verify -v || exit /b 1
python -m unittest tests.test_engiproof.EngiProofTests.test_verify_all -v || exit /b 1

engiproof verify-all || exit /b 1
engiproof run P40 || exit /b 1
engiproof verify P40 || exit /b 1
engiproof assess-discrepancies P40 || exit /b 1
engiproof discrepancy-gate P40
if errorlevel 2 exit /b 1
engiproof promotion-gate P40
if errorlevel 2 exit /b 1

echo === Expected: P40 promotion is BLOCKED while P40-D001 is OPEN ===
echo === V0.2.0-DEV3 DISCREPANCY VERIFY PASS ===
endlocal
