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

# ********** Argument validation **********
# Enable online report generation only if "online" argument is provided.
# If no argument is provided, only local file paths are used.
# If any other argument is provided, an error is raised.
LOBSTER_ONLINE_REPORT_ENABLE=0  
if [ "$#" -gt 1 ]; then
    echo "Error: Too many arguments. Only optional 'online' is allowed." >&2
    exit 1
elif [ "$#" -eq 1 ]; then
    if [ "$1" == "online" ]; then
        LOBSTER_ONLINE_REPORT_ENABLE=1
    else
        echo "Error: Invalid argument '$1'. Only optional 'online' is allowed." >&2
        exit 1
    fi
fi


LOBSTER_TRLC=lobster-trlc
LOBSTER_PYTHON=lobster-python
LOBSTER_REPORT=lobster-report
LOBSTER_RENDERER=lobster-html-report
LOBSTER_ONLINE_REPORT=lobster-online-report

OUTPUT_DIR=out

SW_REQ_LOBSTER_CONF=./lobster-trlc-sw-req.yaml
SW_REQ_LOBSTER_OUT=$OUTPUT_DIR/sw_req-lobster.json

SW_TEST_LOBSTER_CONF=./lobster-trlc-sw-test.yaml
SW_TEST_LOBSTER_OUT=$OUTPUT_DIR/sw_test-lobster.json

SW_TESTRESULT_LOBSTER_CONF=./lobster-trlc-sw-test-result.yaml
SW_TESTRESULT_LOBSTER_OUT=$OUTPUT_DIR/sw_test_result-lobster.json
SW_CODE_SOURCES=./../../src/pyTRLCConverter
SW_CODE_LOBSTER_OUT=$OUTPUT_DIR/sw_code-lobster.json

SW_TEST_CODE_SOURCES=./../../tests
SW_TEST_CODE_LOBSTER_OUT=$OUTPUT_DIR/sw_test_code-lobster.json

SW_REQ_LOBSTER_REPORT_CONF=./lobster-report-sw-req.conf
SW_REQ_LOBSTER_REPORT_OUT=$OUTPUT_DIR/lobster-report-sw-req-lobster.json
SW_REQ_LOBSTER_ONLINE_REPORT_CONF=$OUTPUT_DIR/online_report_config.yaml

SW_REQ_LOBSTER_HTML_OUT=$OUTPUT_DIR/sw_req_tracing_online_report.html


# ********** Prepare output directory **********
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
else
    rm -rf "$OUTPUT_DIR"/*
fi

# ********** SW-Requirements **********
$LOBSTER_TRLC --config "$SW_REQ_LOBSTER_CONF" --out "$SW_REQ_LOBSTER_OUT"

if [ $? -ne 0 ]; then
    exit 1
fi

# ********** SW-Test **********
$LOBSTER_TRLC --config "$SW_TEST_LOBSTER_CONF" --out "$SW_TEST_LOBSTER_OUT"

if [ $? -ne 0 ]; then
    exit 1
fi

# ********** SW-Test Result **********
$LOBSTER_TRLC --config $SW_TESTRESULT_LOBSTER_CONF --out $SW_TESTRESULT_LOBSTER_OUT

if [ $? -ne 0 ]; then
    exit 1
fi

# ********** SW-Code **********
$LOBSTER_PYTHON --out "$SW_CODE_LOBSTER_OUT" "$SW_CODE_SOURCES"

if [ $? -ne 0 ]; then
    exit 1
fi

# ********** SW-Test Code **********
$LOBSTER_PYTHON --out $SW_TEST_CODE_LOBSTER_OUT $SW_TEST_CODE_SOURCES

if [ $? -ne 0 ]; then
    exit 1
fi

# ********** Combine all lobster intermediate files **********
$LOBSTER_REPORT --lobster-config "$SW_REQ_LOBSTER_REPORT_CONF" --out "$SW_REQ_LOBSTER_REPORT_OUT"

if [ $? -ne 0 ]; then
    exit 1
fi

# ********** LOBSTER Report conversion from local files to GIT URLS **********
if [ "$LOBSTER_ONLINE_REPORT_ENABLE" -eq "1" ]; then
    COMMIT_ID=$(git rev-parse HEAD)
    BASE_URL=$(git remote get-url origin)
    echo "report: '$SW_REQ_LOBSTER_REPORT_OUT'" > "$SW_REQ_LOBSTER_ONLINE_REPORT_CONF"
    echo "commit_id: '$COMMIT_ID'" >> "$SW_REQ_LOBSTER_ONLINE_REPORT_CONF"
    echo "repo_root: './../..'" >> "$SW_REQ_LOBSTER_ONLINE_REPORT_CONF"
    echo "base_url: '$BASE_URL'" >> "$SW_REQ_LOBSTER_ONLINE_REPORT_CONF"
    cat $SW_REQ_LOBSTER_ONLINE_REPORT_CONF

    # lobster-online-report v1.0.1 failes to patch the input file without --out option.
    # Create temporary one with ".online" extension and replace it with the input aftewards.
    #
    $LOBSTER_ONLINE_REPORT --config "$SW_REQ_LOBSTER_ONLINE_REPORT_CONF" --out "$SW_REQ_LOBSTER_REPORT_OUT.online"
        if [ $? -ne 0 ]; then
        exit 1
    fi
    mv "$SW_REQ_LOBSTER_REPORT_OUT.online" "$SW_REQ_LOBSTER_REPORT_OUT"
fi

# ********** Create trace report **********
$LOBSTER_RENDERER --out "$SW_REQ_LOBSTER_HTML_OUT" "$SW_REQ_LOBSTER_REPORT_OUT"

if [ $? -ne 0 ]; then
    exit 1
fi
