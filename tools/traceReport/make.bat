@echo off

rem pyTRLCConverter - A tool to convert TRLC files to specific formats.
rem Copyright (c) 2024 - 2025 NewTec GmbH
rem
rem This file is part of pyTRLCConverter program.
rem
rem The pyTRLCConverter program is free software: you can redistribute it and/or modify it under
rem the terms of the GNU General Public License as published by the Free Software Foundation,
rem either version 3 of the License, or (at your option) any later version.
rem
rem The pyTRLCConverter program is distributed in the hope that it will be useful, but
rem WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
rem FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
rem
rem You should have received a copy of the GNU General Public License along with pyTRLCConverter.
rem If not, see <https://www.gnu.org/licenses/>.

REM ********** Argument validation **********
REM Enable online report generation only if "online" argument is provided.
REM If no argument is provided, only local file paths are used.
REM If any other argument is provided, an error is raised.

set LOBSTER_ONLINE_REPORT_ENABLE=0
if "%~1"=="" (
    REM No arguments provided, proceed normally.
) else if "%~1"=="online" (
    set LOBSTER_ONLINE_REPORT_ENABLE=1
) else (
    echo Error: Invalid argument "%~1". Only optional "online" is allowed. >&2
    exit /b 1
)

REM Keep all environment variables local to this script.
setlocal

pushd %~dp0

set LOBSTER_TRLC=lobster-trlc
set LOBSTER_PYTHON=lobster-python
set LOBSTER_REPORT=lobster-report
set LOBSTER_RENDERER=lobster-html-report
set LOBSTER_ONLINE_REPORT=lobster-online-report

set OUTPUT_DIR=out

set SW_REQ_LOBSTER_CONF=.\lobster-trlc-sw-req.yaml
set SW_REQ_LOBSTER_OUT=%OUTPUT_DIR%\sw_req-lobster.json

set SW_TEST_LOBSTER_CONF=.\lobster-trlc-sw-test.yaml
set SW_TEST_LOBSTER_OUT=%OUTPUT_DIR%\sw_test-lobster.json

set SW_TESTRESULT_LOBSTER_CONF=.\lobster-trlc-sw-test-result.yaml
set SW_TESTRESULT_LOBSTER_OUT=%OUTPUT_DIR%\sw_test_result-lobster.json

set SW_CODE_SOURCES=.\..\..\src\pyTRLCConverter
set SW_CODE_LOBSTER_OUT=%OUTPUT_DIR%\sw_code-lobster.json

set SW_TEST_CODE_SOURCES=.\..\..\tests
set SW_TEST_CODE_LOBSTER_OUT=%OUTPUT_DIR%\sw_test_code-lobster.json

set SW_REQ_LOBSTER_REPORT_CONF=.\lobster-report-sw-req.conf
set SW_REQ_LOBSTER_REPORT_OUT=%OUTPUT_DIR%\lobster-report-sw-req-lobster.json
set SW_REQ_LOBSTER_ONLINE_REPORT_CONF=%OUTPUT_DIR%\online_report_config.yaml

set SW_REQ_LOBSTER_HTML_OUT=%OUTPUT_DIR%\sw_req_tracing_online_report.html

if not exist "%OUTPUT_DIR%" (
    md %OUTPUT_DIR%
) else (
    del /q /s "%OUTPUT_DIR%\*" >nul
)

REM ********** SW-Requirements **********
%LOBSTER_TRLC% --config %SW_REQ_LOBSTER_CONF% --out %SW_REQ_LOBSTER_OUT%

if errorlevel 1 (
    goto error
)

REM ********** SW-Test **********
%LOBSTER_TRLC% --config %SW_TEST_LOBSTER_CONF% --out %SW_TEST_LOBSTER_OUT%

if errorlevel 1 (
    goto error
)

REM ********** SW-Test Result **********
%LOBSTER_TRLC% --config %SW_TESTRESULT_LOBSTER_CONF% --out %SW_TESTRESULT_LOBSTER_OUT%

if errorlevel 1 (
    goto error
)

REM ********** SW-Code **********
%LOBSTER_PYTHON% --out %SW_CODE_LOBSTER_OUT% %SW_CODE_SOURCES%

if errorlevel 1 (
    goto error
)

REM ********** SW-Test Code **********
%LOBSTER_PYTHON% --out %SW_TEST_CODE_LOBSTER_OUT% %SW_TEST_CODE_SOURCES%

if errorlevel 1 (
    goto error
)

REM ********** Combine all lobster intermediate files **********
%LOBSTER_REPORT% --lobster-config %SW_REQ_LOBSTER_REPORT_CONF% --out %SW_REQ_LOBSTER_REPORT_OUT%

if errorlevel 1 (
    goto error
)

REM ********** LOBSTER Report conversion from local files to GIT URLS **********
if not %LOBSTER_ONLINE_REPORT_ENABLE% ==1 goto skip_online

    for /f "delims=" %%i in ('git rev-parse HEAD') do set COMMIT_ID=%%i
    for /f "delims=" %%i in ('git remote get-url origin') do set BASE_URL=%%i
    echo report: '%SW_REQ_LOBSTER_REPORT_OUT%' > %SW_REQ_LOBSTER_ONLINE_REPORT_CONF%
    echo commit_id: '%COMMIT_ID%' >> %SW_REQ_LOBSTER_ONLINE_REPORT_CONF%
    echo repo_root: '.\..\..' >> %SW_REQ_LOBSTER_ONLINE_REPORT_CONF%
    echo base_url: '%BASE_URL%' >> %SW_REQ_LOBSTER_ONLINE_REPORT_CONF%
    type "%SW_REQ_LOBSTER_ONLINE_REPORT_CONF%"

    REM lobster-online-report v1.0.1 failes to patch the input file without --out option.
    REM Create temporary one with ".online" extension and replace it with the input aftewards.
    REM
    %LOBSTER_ONLINE_REPORT% --config "%SW_REQ_LOBSTER_ONLINE_REPORT_CONF%" --out "%SW_REQ_LOBSTER_REPORT_OUT%.online"
    move /Y "%SW_REQ_LOBSTER_REPORT_OUT%.online" "%SW_REQ_LOBSTER_REPORT_OUT%"

    if errorlevel 1 (
        goto error
    )

:skip_online

REM ********** Create trace report **********
%LOBSTER_RENDERER% --out %SW_REQ_LOBSTER_HTML_OUT% %SW_REQ_LOBSTER_REPORT_OUT%

if errorlevel 1 (
    goto error
)

goto finished

:error

:finished

endlocal
popd