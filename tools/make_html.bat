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

setlocal

set ONLINE_REPORT_OPTION=""

if "%~1"=="" (
    REM No arguments provided, proceed normally.
) else if "%~1"=="online" (
    set ONLINE_REPORT_OPTION="online"
) else (
    echo Error: Invalid argument "%~1". Only optional "online" is allowed. >&2
    exit /b 1
)

REM Create reStructured Text documentation from TRLC models and files.
call trlc2other/make_rst

REM Create unit test reports
call testReport/make_rst 

REM Create tracing report from TRLC and source files.
call traceReport/make %ONLINE_REPORT_OPTION%

REM Create HTML documentation.
call deployDoc/make html

endlocal