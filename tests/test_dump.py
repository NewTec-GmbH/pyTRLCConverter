"""Test the dump requirements.
"""

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

# Imports **********************************************************************
import os
from pyTRLCConverter.__main__ import main

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

def test_tc_ascii_conversion(record_property, capsys, monkeypatch):
    # lobster-trace: SwTests.tc_ascii_conversion
    """
    The software shall support conversion of TRLC source files into ASCII format.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
    """
    record_property("lobster-trace", "SwTests.tc_ascii_conversion")

    # Mock program arguments to simulate running the script with inbuild reStructuredText converter.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils",
        "--exclude", "./tests/utils/single_req_description_md.trlc",
        "dump"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()

    # Check that no errors were reported.
    assert captured.err == ""

    # Check that the ASCII output is as expected.
    lines = captured.out.split("\n")
    assert lines[0] == f"Entering file: {os.path.normpath('./tests/utils/single_req_no_section.trlc')}"
    assert lines[1] == "Record req_id_1, Level: 0"
    assert lines[2] == "   Record_Object req_id_1"
    assert lines[3] == "      Type: Requirement"
    assert lines[4] == "      Field description"
    assert lines[5] == "         String Literal 'Test description'"
    assert lines[6] == "      Field link"
    assert lines[7] == "         Implicit_Null"
    assert lines[8] == "      Field index"
    assert lines[9] == "         Integer Literal 1"
    assert lines[10] == "      Field precision"
    assert lines[11] == "         Implicit_Null"
    assert lines[12] == "      Field valid"
    assert lines[13] == "         Implicit_Null"
    assert lines[14] == "None"
    assert lines[15] == f"Leaving file: {os.path.normpath('./tests/utils/single_req_no_section.trlc')}"
    assert lines[16] == f"Entering file: {os.path.normpath('./tests/utils/single_req_with_link.trlc')}"
    assert lines[17] == "Record req_id_3, Level: 0"
    assert lines[18] == "   Record_Object req_id_3"
    assert lines[19] == "      Type: Requirement"
    assert lines[20] == "      Field description"
    assert lines[21] == "         String Literal 'Test description'"
    assert lines[22] == "      Field link"
    assert lines[23] == "         Record Reference req_id_2"
    assert lines[24] == "            Resolved: True"
    assert lines[25] == "      Field index"
    assert lines[26] == "         Implicit_Null"
    assert lines[27] == "      Field precision"
    assert lines[28] == "         Implicit_Null"
    assert lines[29] == "      Field valid"
    assert lines[30] == "         Boolean Literal False"
    assert lines[31] == "None"
    assert lines[32] == f"Leaving file: {os.path.normpath('./tests/utils/single_req_with_link.trlc')}"
    assert lines[33] == f"Entering file: {os.path.normpath('./tests/utils/single_req_with_section.trlc')}"
    assert lines[34] == "Section: Test section at level: 0"
    assert lines[35] == "Record req_id_2, Level: 0"
    assert lines[36] == "   Record_Object req_id_2"
    assert lines[37] == "      Type: Requirement"
    assert lines[38] == "      Field description"
    assert lines[39] == "         String Literal 'Test description'"
    assert lines[40] == "      Field link"
    assert lines[41] == "         Implicit_Null"
    assert lines[42] == "      Field index"
    assert lines[43] == "         Implicit_Null"
    assert lines[44] == "      Field precision"
    assert lines[45] == "         Decimal Literal 0"  # Current bug in TRLC will incorrectly dump Decimals.
    assert lines[46] == "      Field valid"
    assert lines[47] == "         Implicit_Null"
    assert lines[48] == "      Section Test section"
    assert lines[49] == "         Parent: None"
    assert lines[50] == "None"
    assert lines[51] == f"Leaving file: {os.path.normpath('./tests/utils/single_req_with_section.trlc')}"
