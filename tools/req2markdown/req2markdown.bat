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

cd ..\plantuml
call get_plantuml.bat
cd ..\req2markdown

if not exist "out" (
    md out
)

rem ****************************************************************************************************
rem Software Requirements
rem ****************************************************************************************************
set SWE_REQ_OUT_FORMAT=markdown
set SWE_REQ_OUT_DIR=.\out\sw-requirements\%SWE_REQ_OUT_FORMAT%
set SWE_REQ_CONVERTER=..\ProjectConverter\req2markdown

if not exist %SWE_REQ_OUT_DIR% (
    md %SWE_REQ_OUT_DIR%
)

echo Generate software requirements ...
pyTRLCConverter --source=..\..\doc\sw-requirements --source=..\..\doc\models -o=%SWE_REQ_OUT_DIR% --verbose -p=%SWE_REQ_CONVERTER% %SWE_REQ_OUT_FORMAT%

if errorlevel 1 (
    pause
)
