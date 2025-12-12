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
pushd %~dp0

pushd ..\plantUML
call get_plantuml.bat
popd

rem Keep all environment variables local to this script.
setlocal

set TRLC_CONVERTER=pyTRLCConverter
set OUTPUT_DIR=out
set CONVERTER=converter/req2rst.py
set TRANSLATION=converter/translation.json
set OUT_FORMAT=rst
set RENDERER_CFG=converter/renderCfg.json

if not exist "%OUTPUT_DIR%" (
    md %OUTPUT_DIR%
) else (
    del /q /s "%OUTPUT_DIR%\*" >nul
)

%TRLC_CONVERTER% --source=..\..\trlc\swe-req --include=..\..\trlc\model --verbose --out=%OUTPUT_DIR% --project=%CONVERTER% --translation=%TRANSLATION% --renderCfg=%RENDERER_CFG% %OUT_FORMAT%

if errorlevel 1 (
    goto error
)

set CONVERTER=converter/tc2rst.py

%TRLC_CONVERTER% --source=..\..\trlc\swe-test --include=..\..\trlc\model --include=..\..\trlc\swe-req --exclude=..\..\trlc\swe-req --verbose --out=%OUTPUT_DIR% --project=%CONVERTER% --translation=%TRANSLATION% %OUT_FORMAT%

if errorlevel 1 (
    goto error
)

goto finished

:error

:finished

endlocal
rem Restore the previous directory from the stack.
rem This allows the script to return to the original working directory.
popd
