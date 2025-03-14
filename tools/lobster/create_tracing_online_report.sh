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

LOBSTER_TRLC=lobster-trlc
LOBSTER_PYTHON=lobster-python
LOBSTER_REPORT=lobster-report
LOBSTER_ONLINE_REPORT=lobster-online-report
LOBSTER_RENDERER=lobster-html-report
OUT_DIR=out
MODELS=../../../doc/models

SW_REQ_SOURCES=../../../doc/sw-requirements
SW_REQ_LOBSTER_CONF=../lobster-sw-req.conf
SW_REQ_LOBSTER_OUT=sw_req.lobster

SW_TEST_SOURCES=../../../doc/sw-test
SW_TEST_LOBSTER_CONF=../lobster-sw-test.conf
SW_TEST_LOBSTER_OUT=sw_test.lobster

SW_CODE_SOURCES=../../../src/pyTRLCConverter
SW_CODE_LOBSTER_OUT=sw_code.lobster

SW_TEST_CODE_SOURCES=../../../tests
SW_TEST_CODE_LOBSTER_OUT=sw_test_code.lobster

SW_REQ_LOBSTER_REPORT_CONF=../lobster-report-sw-req.conf
SW_REQ_LOBSTER_REPORT_OUT=lobster-report-sw-req.lobster
SW_REQ_LOBSTER_ONLINE_REPORT_OUT=lobster-online-report-sw-req.lobster
SW_REQ_LOBSTER_HTML_OUT=sw_req_tracing_online_report.html

SW_TEST_LOBSTER_REPORT_CONF=../lobster-report-sw-test.conf
SW_TEST_LOBSTER_REPORT_OUT=lobster-report-sw-test.lobster
SW_TEST_LOBSTER_ONLINE_REPORT_OUT=lobster-online-report-sw-rest.lobster
SW_TEST_LOBSTER_HTML_OUT=sw_test_tracing_online_report.html

LOCAL_REPOSITORY_ROOT=../../..

if [ ! -d "$OUT_DIR" ]; then
    mkdir -p $OUT_DIR
fi

cd $OUT_DIR || exit

# ********** SW-Requirements **********
$LOBSTER_TRLC --config-file $SW_REQ_LOBSTER_CONF --out $SW_REQ_LOBSTER_OUT $SW_REQ_SOURCES $MODELS
if [ $? -ne 0 ]; then
    exit 1
fi

# ********** SW-Tests **********
$LOBSTER_TRLC --config-file $SW_TEST_LOBSTER_CONF --out $SW_TEST_LOBSTER_OUT $SW_REQ_SOURCES $SW_TEST_SOURCES $MODELS
if [ $? -ne 0 ]; then
    exit 1
fi

# ********** SW-Code **********
$LOBSTER_PYTHON --out $SW_CODE_LOBSTER_OUT $SW_CODE_SOURCES
if [ $? -ne 0 ]; then
    exit 1
fi

# ********** SW-Test Code **********
$LOBSTER_PYTHON --out $SW_TEST_CODE_LOBSTER_OUT --activity $SW_TEST_CODE_SOURCES
if [ $? -ne 0 ]; then
    exit 1
fi

# ********** Report SW-Requirements **********
$LOBSTER_REPORT --lobster-config $SW_REQ_LOBSTER_REPORT_CONF --out $SW_REQ_LOBSTER_REPORT_OUT
if [ $? -ne 0 ]; then
    exit 1
fi

# ********** Online Report SW-Requirements **********
$LOBSTER_ONLINE_REPORT --out $SW_REQ_LOBSTER_ONLINE_REPORT_OUT $SW_REQ_LOBSTER_REPORT_OUT --repo-root $LOCAL_REPOSITORY_ROOT
if [ $? -ne 0 ]; then
    exit 1
fi

# ********** Report SW-Requirements to HTML **********
$LOBSTER_RENDERER --out $SW_REQ_LOBSTER_HTML_OUT $SW_REQ_LOBSTER_ONLINE_REPORT_OUT
if [ $? -ne 0 ]; then
    exit 1
fi

# ********** Report SW-Tests **********
$LOBSTER_REPORT --lobster-config $SW_TEST_LOBSTER_REPORT_CONF --out $SW_TEST_LOBSTER_REPORT_OUT
if [ $? -ne 0 ]; then
    exit 1
fi

# ********** Online Report SW-Requirements **********
$LOBSTER_ONLINE_REPORT --out $SW_TEST_LOBSTER_ONLINE_REPORT_OUT $SW_TEST_LOBSTER_REPORT_OUT --repo-root $LOCAL_REPOSITORY_ROOT
if [ $? -ne 0 ]; then
    exit 1
fi

# ********** Report SW-Tests to HTML **********
$LOBSTER_RENDERER --out $SW_TEST_LOBSTER_HTML_OUT $SW_TEST_LOBSTER_ONLINE_REPORT_OUT
if [ $? -ne 0 ]; then
    exit 1
fi

cd ..
