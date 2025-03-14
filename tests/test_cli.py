"""Test the program's command line interface.
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

import re
import pytest

from pyTRLCConverter.__main__ import main

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

def test_tc_help(record_property, capsys, monkeypatch):
    # lobster-trace: SwTests.tc_help
    """
    Check for the help information in case there is no project specific converter available.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
    """
    record_property("lobster-trace", "SwTests.tc_help")

    # Mock program arguments to simulate running the script without any arguments.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--help"
    ])

    # argparse will raise an exception if --help is provided.
    with pytest.raises(SystemExit):
        main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()

    # Check just the first line of the help message.
    print(captured.out)
    regex = r"usage: pyTRLCConverter \[\-h\] \[\-\-version\] \[\-v\] \[\-i INCLUDE\] \-s SOURCE"
    assert re.match(regex, captured.out)

def test_tc_help_prj_spec(record_property, capsys, monkeypatch):
    # lobster-trace: SwTests.tc_help_prj_spec
    """
    Check for the help information in case there is a project specific converter available.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
    """
    record_property("lobster-trace", "SwTests.tc_help_prj_spec")

    # Mock program arguments to simulate running the script without any arguments.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--help",
        "--project", "./tests/utils/psc_do_nothing.py",
    ])

    # argparse will raise an exception if --help is provided.
    with pytest.raises(SystemExit):
        main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()

    # Check just the first line of the help message.
    print(captured.out)
    regex = r"usage: pyTRLCConverter \[\-h\] \[\-\-version\] \[\-v\] \[\-i INCLUDE\] \-s SOURCE"
    assert re.match(regex, captured.out)

def test_tc_cli_exclude(record_property, capsys, monkeypatch):
    # lobster-trace: SwTests.tc_cli_exclude
    """
    This test case checks whether a TRLC file can be excluded from the conversion.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
    """
    record_property("lobster-trace", "SwTests.tc_cli_exclude")

    # Mock program arguments to simulate running the script with two test requirement files.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils",
        "--exclude", "./tests/utils/single_req_with_link.trlc",
        "--project", "./tests/utils/psc_simple",
        "simple"
    ])

    # Expecting the programm to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()

    # No error output expected.
    assert captured.err == ""

    # Check if the expected output.
    lines = captured.out.splitlines()
    assert len(lines) == 6
    assert lines[0] == "req_id_1"
    assert lines[1] == "Test description"
    assert lines[2] == "Test section"
    assert lines[3] == ""
    assert lines[4] == "req_id_2"
    assert lines[5] == "Test description"

# Main *************************************************************************
