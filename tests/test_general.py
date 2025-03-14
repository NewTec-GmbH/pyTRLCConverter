"""Test the general requirements.
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

def test_tc_cli_no_arguments(record_property, capsys, monkeypatch):
    # lobster-trace: SwTests.tc_cli
    """
    If the command line interface is called without any arguments, it shall require the user to
    provide at least one argument.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
    """
    record_property("lobster-trace", "SwTests.tc_cli")

    # Mock program arguments to simulate running the script without any arguments.
    monkeypatch.setattr("sys.argv", ["pyTRLCConverter"])

    # argparse will raise an exception if no arguments are provided.
    with pytest.raises(SystemExit):
        main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()

    # Check if the program requested an argument from the user.
    assert "arguments are required" in captured.err

def test_tc_prj_spec(record_property, capsys, monkeypatch):
    # lobster-trace: SwTests.tc_prj_spec
    """
    Check whether a project specific converter can be instantiated.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
    """
    record_property("lobster-trace", "SwTests.tc_prj_spec")

    # Mock program arguments to simulate running the script with a project specific converter.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--project", "./tests/utils/psc_do_nothing.py",
        "doNothing"
    ])

    # Expecting the programm to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()

    # No error output expected.
    assert captured.err == ""

    # No output expected.
    assert captured.out == ""

def test_tc_version(record_property, capsys, monkeypatch):
    # lobster-trace: SwTests.tc_version
    """
    If the command line interface is called with --version, it shall print the version of the
    program in the format <program-name> <major>.<minor>.<patch>.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
    """
    record_property("lobster-trace", "SwTests.tc_version")

    # Mock program arguments to simulate running the script with the --version flag set.
    monkeypatch.setattr("sys.argv", ["pyTRLCConverter", "--version"])

    # argparse will raise SystemExit after printing the version information.
    with pytest.raises(SystemExit):
        main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()

    # No error output expected.
    assert captured.err == ""

    # Check format of the version string.
    regex = r"pyTRLCConverter \d+\.\d+\.\d+"
    assert re.match(regex, captured.out)

def test_tc_process_trlc_symbols_one_file_one_req(record_property, capsys, monkeypatch):
    # lobster-trace: SwTests.tc_process_trlc_symbols_one_file_one_req
    """
    One TRLC file, one record.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
    """
    record_property("lobster-trace", "SwTests.tc_process_trlc_symbols_one_file_one_req")

    # Mock program arguments to simulate running the script with the single test requirement.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
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
    assert len(lines) == 2
    assert lines[0] == "req_id_1"
    assert lines[1] == "Test description"

def test_tc_process_trlc_symbols_two_files_one_req(record_property, capsys, monkeypatch):
    # lobster-trace: SwTests.tc_process_trlc_symbols_two_files_one_req
    """
    Two TRLC files, one record each.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
    """
    record_property("lobster-trace", "SwTests.tc_process_trlc_symbols_two_files_one_req")

    # Mock program arguments to simulate running the script with two test requirement files.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--source", "./tests/utils/single_req_with_section.trlc",
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

def test_tc_verbose(record_property, capsys, monkeypatch):
    # lobster-trace: SwTests.tc_verbose
    """
    One TRLC file, one record. In verbose mode there will more information printed to the console,
    than just the record id and description.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
    """
    record_property("lobster-trace", "SwTests.tc_verbose")

    # Mock program arguments to simulate running the script with the --verbose flag set.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--verbose",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
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
    assert len(lines) == 16
    assert lines[14] == "req_id_1"
    assert lines[15] == "Test description"

# Main *************************************************************************
