#!/bin/bash

# pyTRLCConverter - A tool to convert PlantUML diagrams to image files.
# Copyright (c) 2024 - 2025 NewTec GmbH
#
# This file is part of pyTRLCConverter program.
#
# The pyTRLCConverter program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# The pyTRLCConverter program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with pyTRLCConverter.
# If not, see <https://www.gnu.org/licenses/>.

PLANTUML="plantuml.jar"

if [ ! -f "$PLANTUML" ]; then
    echo "Download PlantUML java program..."
    curl -L -o "$PLANTUML" "https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar"
fi

if [ ! -d "out" ]; then
    mkdir out
fi

# ****************************************************************************************************
# Software Requirements
# ****************************************************************************************************
SWE_REQ_OUT_FORMAT="markdown"
SWE_REQ_OUT_DIR="./out/sw-requirements/$SWE_REQ_OUT_FORMAT"

if [ ! -d "$SWE_REQ_OUT_DIR" ]; then
    mkdir -p "$SWE_REQ_OUT_DIR"
fi

echo "Generate software requirements ..."
pyTRLCConverter --source=../../doc/sw-requirements --source=../../doc/models -o="$SWE_REQ_OUT_DIR" -p=req2markdown "$SWE_REQ_OUT_FORMAT"

if [ $? -ne 0 ]; then
    read -p "Press any key to continue..."
fi
