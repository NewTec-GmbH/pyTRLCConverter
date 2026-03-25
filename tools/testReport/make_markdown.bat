@echo off

rem pyTRLCConverter - A tool to convert TRLC files to specific formats.
rem Copyright (c) 2024 - 2026 NewTec GmbH
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

pushd %~dp0

pushd ..\plantUML
call get_plantuml.bat
popd

setlocal

set SRC_PATH=./src
set TESTS_PATH=./tests
set COVERAGE_REPORT=coverage
set REPORT_TOOL_PATH=%~dp0
set TEST_RESULT_REPORT_XML=sw_test_result_report.xml
set TEST_RESULT_REPORT_TRLC=sw_test_result_report.trlc
set TRLC_CONVERTER=pyTRLCConverter
set CONVERTER_DIR=../trlc2other/converter
set OUTPUT_DIR=out
set CONVERTER=%CONVERTER_DIR%/create_test_report_in_markdown.py
set OUT_FORMAT=markdown

if not exist "%OUTPUT_DIR%" (
    md %OUTPUT_DIR%
) else (
    del /q "%OUTPUT_DIR%\*" >nul
)

rem Create the sw test report and the coverage analysis.
pushd  ..\..
pytest %TESTS_PATH% -v --cov=%SRC_PATH% --cov-report=term-missing --cov-report=html:%REPORT_TOOL_PATH%/%OUTPUT_DIR%/%COVERAGE_REPORT% -o junit_family=xunit1 --junitxml=%REPORT_TOOL_PATH%/%OUTPUT_DIR%/%TEST_RESULT_REPORT_XML% || goto :error
popd

rem Convert sw test report XML to TRLC.
python test_result_xml2trlc.py ./%OUTPUT_DIR%/%TEST_RESULT_REPORT_XML% ./%OUTPUT_DIR%/%TEST_RESULT_REPORT_TRLC% || goto :error

rem Convert sw test report TRLC to reStructuredText.
%TRLC_CONVERTER% --source=..\..\trlc\swe-req --source=..\..\trlc\swe-test --source=..\..\trlc\model --exclude=..\..\trlc\swe-req --exclude=..\..\trlc\swe-test --source=%OUTPUT_DIR%\%TEST_RESULT_REPORT_TRLC% -o=%OUTPUT_DIR% --project=%CONVERTER% --verbose %OUT_FORMAT% || goto :error

goto finished

:error

:finished

endlocal
rem Restore the previous directory from the stack.
rem This allows the script to return to the original working directory.
popd
