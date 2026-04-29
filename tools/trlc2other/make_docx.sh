#!/bin/bash

# pyTRLCConverter - A tool to convert TRLC files to specific formats.
# Copyright (c) 2024 - 2026 NewTec GmbH
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

set -e

pushd ../plantUML
chmod +x get_plantuml.sh
. ./get_plantuml.sh
popd

TRLC_CONVERTER=pyTRLCConverter
OUTPUT_DIR=out
CONVERTER=converter/req2docx.py
TRANSLATION=converter/translation.json
RENDER_CFG=converter/renderCfg.json
TEMPLATE=converter/template.docx
OUT_FORMAT=docx

if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir $OUTPUT_DIR
else
    rm -rf "$OUTPUT_DIR"/*
fi

echo "Generate software requirements ..."
$TRLC_CONVERTER --source=../../trlc/swe-req --include=../../trlc/model --verbose --out="$OUTPUT_DIR" --project="$CONVERTER" --translation="$TRANSLATION" --renderCfg="$RENDER_CFG" "$OUT_FORMAT" --template="$TEMPLATE"
$TRLC_CONVERTER --source=../../trlc/swe-arch --include=../../trlc/model --include=../../trlc/swe-req --exclude=../../trlc/swe-req --verbose --out="$OUTPUT_DIR" --project="$CONVERTER" --translation="$TRANSLATION" "$OUT_FORMAT"
