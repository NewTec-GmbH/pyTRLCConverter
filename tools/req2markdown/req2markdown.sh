@echo off

rem pyTRLCConverter - A tool to convert PlantUML diagrams to image files.
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

set PLANTUML=plantuml.jar

if not exist "%PLANTUML%" (
    echo Download PlantUML java program...
    powershell -Command "Invoke-WebRequest https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar -OutFile %PLANTUML%"
)

if not exist "out" (
    md out
)

rem ****************************************************************************************************
rem Software Requirements
rem ****************************************************************************************************
set SWE_REQ_OUT_FORMAT=markdown
set SWE_REQ_OUT_DIR=.\out\sw-requirements\%SWE_REQ_OUT_FORMAT%

if not exist %SWE_REQ_OUT_DIR% (
    md %SWE_REQ_OUT_DIR%
)

echo Generate software requirements ...
pyTRLCConverter --source=..\..\doc\sw-requirements --source=..\..\doc\models -o=%SWE_REQ_OUT_DIR% -p=req2markdown %SWE_REQ_OUT_FORMAT%

if errorlevel 1 (
    pause
)
