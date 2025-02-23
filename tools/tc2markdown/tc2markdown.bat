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
cd ..\tc2markdown

if not exist "out" (
    md out
)

rem ****************************************************************************************************
rem Software Tests
rem ****************************************************************************************************
set SW_TEST_OUT_FORMAT=markdown
set SW_TEST_OUT_DIR=.\out\sw-tests\%SW_TEST_OUT_FORMAT%
set SW_TEST_CONVERTER=..\ProjectConverter\tc2markdown

if not exist %SW_TEST_OUT_DIR% (
    md %SW_TEST_OUT_DIR%
)

echo Generate software tests ...
pyTRLCConverter --source=..\..\doc\sw-requirements --source=..\..\doc\sw-test --exclude=..\..\doc\sw-requirements --source=..\..\doc\models -o=%SW_TEST_OUT_DIR% --verbose --project=%SW_TEST_CONVERTER% %SW_TEST_OUT_FORMAT%
