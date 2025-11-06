#!/bin/bash

# pyTRLCConverter - A tool to convert TRLC files to specific formats.
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

cd ../plantuml
chmod +x get_plantuml.sh
. ./get_plantuml.sh
cd ../req2rst

if [ ! -d "out" ]; then
    mkdir out
else
    rm -rf "out"/*
fi

# ****************************************************************************************************
# Software Requirements
# ****************************************************************************************************
SWE_REQ_OUT_FORMAT="rst"
SWE_REQ_OUT_DIR="./out/sw-requirements/$SWE_REQ_OUT_FORMAT"
SWE_REQ_CONVERTER=../ProjectConverter/req2rst
TRANSLATION=../ProjectConverter/translation.json
RENDERER_CFG=../ProjectConverter/renderCfg.json

if [ ! -d "$SWE_REQ_OUT_DIR" ]; then
    mkdir -p "$SWE_REQ_OUT_DIR"
fi

echo "Generate software requirements ..."
pyTRLCConverter --source=../../trlc/swe-req --source=../../trlc/model -o="$SWE_REQ_OUT_DIR" --verbose --project="$SWE_REQ_CONVERTER" --translation="$TRANSLATION" --renderCfg="$RENDERER_CFG" "$SWE_REQ_OUT_FORMAT"

if [ $? -ne 0 ]; then
    read -p "Press any key to continue..."
fi
