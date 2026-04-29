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

SRC_PATH=./src
TESTS_PATH=./tests
COVERAGE_REPORT=coverage
REPORT_TOOL_PATH=./tools/testReport
TEST_RESULT_REPORT_XML=sw_test_result_report.xml
TEST_RESULT_REPORT_TRLC=sw_test_result_report.trlc
TRLC_CONVERTER=pyTRLCConverter
CONVERTER_DIR=../trlc2other/converter
OUTPUT_DIR=out
CONVERTER=$CONVERTER_DIR/create_test_report_in_rst.py
OUT_FORMAT=rst

if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
else
    rm -f "$OUTPUT_DIR"/*
fi

# Create the test report and the coverage analysis.
pushd ../..
pytest $TESTS_PATH -v --cov=$SRC_PATH --cov-report=term-missing --cov-report=html:$REPORT_TOOL_PATH/$OUTPUT_DIR/$COVERAGE_REPORT -o junit_family=xunit1 --junitxml=$REPORT_TOOL_PATH/$OUTPUT_DIR/$TEST_RESULT_REPORT_XML
popd

# Convert XML test report to TRLC.
python test_result_xml2trlc.py ./$OUTPUT_DIR/$TEST_RESULT_REPORT_XML ./$OUTPUT_DIR/$TEST_RESULT_REPORT_TRLC

# Convert TRLC test report to reStructuredText.
$TRLC_CONVERTER --source=../../trlc/swe-req --source=../../trlc/swe-test --source=../../trlc/model --exclude=../../trlc/swe-req --exclude=../../trlc/swe-test --source=$OUTPUT_DIR/$TEST_RESULT_REPORT_TRLC -o=$OUTPUT_DIR --project=$CONVERTER --verbose $OUT_FORMAT
