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

set OUT_DIR=out
set SRC_PATH=./src
set TESTS_PATH=./tests
set REPORT_TOOL_PATH=tools/createTestReport
set COVERAGE_REPORT=coverage
set TEST_RESULT_REPORT_XML=test_result_report.xml
set TEST_RESULT_REPORT_TRLC=test_result_report.trlc

if not exist "%OUT_DIR%" (
    md %OUT_DIR%
)

rem Create the test report and the coverage analysis.
cd ../..
pytest %TESTS_PATH% -v --cov=%SRC_PATH% --cov-report=term-missing --cov-report=html:%REPORT_TOOL_PATH%/%OUT_DIR%/%COVERAGE_REPORT% -o junit_family=xunit1 --junitxml=%REPORT_TOOL_PATH%/%OUT_DIR%/%TEST_RESULT_REPORT_XML%
cd %REPORT_TOOL_PATH%

rem Convert XML test report to TRLC.
python test_result_xml2trlc.py ./%OUT_DIR%/%TEST_RESULT_REPORT_XML% ./%OUT_DIR%/%TEST_RESULT_REPORT_TRLC%

rem Convert TRLC test report to Markdown.
pyTRLCConverter --source=..\..\doc\sw-requirements --source=..\..\doc\sw-test --source=..\..\doc\models --exclude=..\..\doc\sw-requirements --exclude=..\..\doc\sw-test --source=%OUT_DIR%\%TEST_RESULT_REPORT_TRLC% -o=%OUT_DIR% --project=create_test_report_in_markdown.py --verbose markdown

if errorlevel 1 (
    pause
)

rem Convert TRLC test report to reStructuredText.
pyTRLCConverter --source=..\..\doc\sw-requirements --source=..\..\doc\sw-test --source=..\..\doc\models --exclude=..\..\doc\sw-requirements --exclude=..\..\doc\sw-test --source=%OUT_DIR%\%TEST_RESULT_REPORT_TRLC% -o=%OUT_DIR% --project=create_test_report_in_rst.py --verbose rst

if errorlevel 1 (
    pause
)
