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

set OUT_PATH=./out

rem Use either local jar file or plantuml server URL for rendering.
set PLANTUML=plantuml.jar
rem set PLANTUML=http://www.plantuml.com/plantuml

rem Skip plantuml jar file download check if PLANTUML points to a server.
echo %PLANTUML% | findstr /i "^http://" >nul
if %errorlevel% equ 0 goto skip_download_plantuml
echo %PLANTUML% | findstr /i "^https://" >nul
if %errorlevel% equ 0 goto skip_download_plantuml

if not exist "%PLANTUML%" (
    echo Download PlantUML java program...
    powershell -Command "Invoke-WebRequest https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar -OutFile %PLANTUML%"
)
:skip_download_plantuml

pyTRLCConverter --source=. --out=%OUT_PATH% --project=req.py markdown

if errorlevel 1 (
    pause
)
