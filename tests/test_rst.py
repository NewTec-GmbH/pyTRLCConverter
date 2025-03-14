"""Test the reStructuredText requirements.
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

from argparse import Namespace
from collections import namedtuple

from pyTRLCConverter.__main__ import main
from pyTRLCConverter.rst_converter import RstConverter

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

def test_tc_rst(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_rst
    """
    The software shall support conversion of TRLC source files into reStructuredText.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst")

    # Mock program arguments to simulate running the script with inbuild reStructuredText converter.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--out", str(tmp_path),
        "rst",
        "--single-document",
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Read the contents of the generated reStructuredText file and assert it is the expected valid reStructuredText.
    with open(tmp_path / "output.rst", "r", encoding='utf-8') as generated_rst:
        lines = generated_rst.readlines()
        assert lines[0] == ".. _output.rst-specification:\n" # Label
        assert lines[1] == "\n"
        assert lines[2] == "Specification\n"
        assert lines[3] == "=============\n"
        assert lines[4] == "\n"
        assert lines[5] == ".. _output.rst-req\\_id\\_1:\n" # Label
        assert lines[6] == "\n"
        assert lines[7] == ".. admonition:: req\\_id\\_1\n"
        assert lines[8] == "\n"
        assert lines[9] == "    +----------------+------------------+\n"
        assert lines[10] == "    | Attribute Name | Attribute Value  |\n"
        assert lines[11] == "    +================+==================+\n"
        assert lines[12] == "    | description    | Test description |\n"
        assert lines[13] == "    +----------------+------------------+\n"
        assert lines[14] == "    | link           | N/A              |\n"
        assert lines[15] == "    +----------------+------------------+\n"

def test_tc_rst_section(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_rst_section
    """
    The software shall support conversion of TRLC sections into reStructuredText headings.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_section")

    # Mock program arguments to convert TRLC containing a section.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_with_section.trlc",
        "--out", str(tmp_path),
        "rst",
        "--single-document",
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Read the contents of the generated reStructuredText file and assert it is the expected valid reStructuredText.
    with open(tmp_path / "output.rst", "r", encoding='utf-8') as generated_rst:
        lines = generated_rst.readlines()
        assert lines[0] == ".. _output.rst-specification:\n" # Label
        assert lines[1] == "\n"
        assert lines[2] == "Specification\n"
        assert lines[3] == "=============\n"
        assert lines[4] == "\n"
        assert lines[5] == ".. _output.rst-test-section:\n" # Label
        assert lines[6] == "\n"
        assert lines[7] == "Test section\n"
        assert lines[8] == "############\n"
        assert lines[9] == "\n"
        assert lines[10] == ".. _output.rst-req\\_id\\_2:\n" # Label
        assert lines[11] == "\n"
        assert lines[12] == ".. admonition:: req\\_id\\_2\n"
        assert lines[13] == "\n"
        assert lines[14] == "    +----------------+------------------+\n"
        assert lines[15] == "    | Attribute Name | Attribute Value  |\n"
        assert lines[16] == "    +================+==================+\n"
        assert lines[17] == "    | description    | Test description |\n"
        assert lines[18] == "    +----------------+------------------+\n"

def test_tc_rst_escape(record_property, tmp_path):
    # lobster-trace: SwTests.tc_rst_escape
    """
    The reStructuredText converter shall support reStructuredText escaping.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_escape")

    rst_converter = RstConverter(Namespace(out=str(tmp_path)))

    # Escaping rules see https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#escaping-mechanism
    EscapingResult = namedtuple("EscapingResult", ["initial", "escaped"])
    checks = [
        EscapingResult(initial=r'I contain nothing weird', escaped=r"I contain nothing weird"),
        EscapingResult(initial=r'I_contain.something+weird', escaped=r"I\_contain\.something\+weird"),
        EscapingResult(initial=r'\`*_{}[]()#+-.!', escaped=r"\\\`\*\_\{\}\[\]\(\)\#\+\-\.\!"),
        EscapingResult(initial=r'unchanged', escaped=r"unchanged")
    ]

    for check in checks:
        assert rst_converter.rst_escape(check.initial) == check.escaped

def test_tc_rst_heading(record_property, tmp_path):
    # lobster-trace: SwTests.tc_rst_heading
    """
    The reStructuredText converter shall provide a function to create reStructuredText headings.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_heading")

    rst_converter = RstConverter(Namespace(out=str(tmp_path)))

    # Test the heading function. Levels 1-6 need to be supported.
    underline_chars = ["=", "#", "~", "^", "\"", "+", "'"]

    for level, underline_char in enumerate(underline_chars):
        lines = rst_converter.rst_create_heading("Heading", level + 1, "test.rst").split('\n')
        assert lines[0] == ".. _test.rst-heading:" # Label
        assert lines[1] == ""
        assert lines[2] == "Heading"
        assert lines[3] == underline_char * len("Heading")

    # Invalid level shall return a empty string.
    assert rst_converter.rst_create_heading("Heading", 0, "test.rst") == ""
    assert rst_converter.rst_create_heading("Heading", 8, "test.rst") == ""

def test_tc_rst_admonition(record_property, tmp_path):
    # lobster-trace: SwTests.tc_rst_admonition
    """
    The reStructuredText converter shall provide a function to create reStructuredText admonition.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_admonition")

    rst_converter = RstConverter(Namespace(out=str(tmp_path)))

    # Test the admonition function.
    lines = rst_converter.rst_create_admonition("Test text", "test.rst").split('\n')
    assert lines[0] == ".. _test.rst-test-text:" # Label
    assert lines[1] == ""
    assert lines[2] == ".. admonition:: Test text"

def test_tc_rst_table(record_property, tmp_path):
    # lobster-trace: SwTests.tc_rst_table
    """
    The reStructuredText converter shall provide the functionality to create reStructuredText tables.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_table")

    rst_converter = RstConverter(Namespace(out=str(tmp_path)))

    # Create a table head.
    headers = ["Header1", "Header2"]
    max_widths = [len(header) for header in headers]
    table = rst_converter.rst_create_table_head(headers, max_widths)
    table_lines = table.split('\n')
    assert table_lines[0] == "    +---------+---------+"
    assert table_lines[1] == "    | Header1 | Header2 |"
    assert table_lines[2] == "    +=========+=========+"

    # Create a table row.
    row = ["Value1", "Value2"]
    table = rst_converter.rst_append_table_row(row, max_widths)
    table_lines = table.split('\n')
    assert table_lines[0] == "    | Value1  | Value2  |"
    assert table_lines[1] == "    +---------+---------+"

    row = ["Value3", "Value4"]
    table = rst_converter.rst_append_table_row(row, max_widths)
    table_lines = table.split('\n')
    assert table_lines[0] == "    | Value3  | Value4  |"
    assert table_lines[1] == "    +---------+---------+"

def test_tc_rst_link(record_property, tmp_path):
    # lobster-trace: SwTests.tc_rst_link
    """
    The reStructuredText converter shall provide the functionality to create reStructuredText links.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_link")

    rst_converter = RstConverter(Namespace(out=str(tmp_path)))

    # Create a reStructuredText link. Escaoubg should only apply to the text, not the url.
    assert rst_converter.rst_create_link("Link Text", "http://example.com") == \
        ":ref:`Link Text <http://example.com>`"
    assert rst_converter.rst_create_link("Another Link", "https://example.org") == \
        ":ref:`Another Link <https://example.org>`"
    assert rst_converter.rst_create_link("Special Characters", "http://example.com/path?query=1&other=2") == \
        ":ref:`Special Characters <http://example.com/path?query=1&other=2>`"
    assert rst_converter.rst_create_link("Special Characters", "http://example.com/path%20with%20spaces", \
        escape=True) == \
        ":ref:`Special Characters <http://example.com/path%20with%20spaces>`"
    assert rst_converter.rst_create_link("Link with special characters!", "http://example.com") == \
        r":ref:`Link with special characters\! <http://example.com>`"
    assert rst_converter.rst_create_link("Link with special characters!", "http://example.com", escape=False) == \
        ":ref:`Link with special characters! <http://example.com>`"

def test_tc_rst_image(record_property, tmp_path):
    # lobster-trace: SwTests.tc_rst_image
    """
    The reStructuredText converter shall provide the functionality to embed images in reStructuredText.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_image")

    rst_converter = RstConverter(Namespace(out=str(tmp_path)))

    # Create a reStructuredText diagram link. Absolute and relative paths shall be supported.
    diagram_path = "/diagram.png"
    assert rst_converter.rst_create_diagram_link(
        f"{diagram_path}",
        "Caption") == \
        f".. image:: {os.path.normpath(diagram_path)}\n    :alt: Caption\n"

    diagram_path = "diagram.png"
    assert rst_converter.rst_create_diagram_link(
        f"{diagram_path}",
        "Caption") == \
        f".. image:: {os.path.normpath(diagram_path)}\n    :alt: Caption\n"

    diagram_path = "./graph.jpg"
    assert rst_converter.rst_create_diagram_link(
        "./graph.jpg",
        "Caption with special characters!") == \
        f".. image:: {os.path.normpath(diagram_path)}\n    :alt: Caption with special characters\\!\n"

    diagram_path = "./I/am/nested.png"
    assert rst_converter.rst_create_diagram_link(
        "./I/am/nested.png",
        "Caption with special characters!",
        escape=False) == \
        f".. image:: {os.path.normpath(diagram_path)}\n    :alt: Caption with special characters!\n"

def test_tc_rst_role(record_property, tmp_path):
    # lobster-trace: SwTests.tc_rst_role
    """
    The reStructuredText converter shall provide the functionality to create reStructuredText role text output.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_role")

    rst_converter = RstConverter(Namespace(out=str(tmp_path)))

    # Test colored text output. HTML span element with style attribute should be used.
    assert rst_converter.rst_role("Text", "red") == ":red:`Text`"
    assert rst_converter.rst_role("Text", "green") == ":green:`Text`"
    assert rst_converter.rst_role("Text", "blue") == ":blue:`Text`"
    assert rst_converter.rst_role("!Text!", "yellow") == ":yellow:`\\!Text\\!`"
    assert rst_converter.rst_role("!Text!", "bad", escape=False) == ":bad:`!Text!`"

def test_tc_rst_out_folder(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_rst_out_folder
    """
    The software shall support specifying an output folder for the reStructuredText conversion.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_out_folder")

    # Mock program arguments to specify an output folder.
    output_folder = tmp_path / "output_folder"
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--out", str(output_folder),
        "rst",
        "--single-document",
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Assert the output folder contains the generated reStructuredText file.
    assert output_folder.exists()
    assert (output_folder / "output.rst").exists()

def test_tc_rst_single_doc_custom(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_rst_single_doc_custom
    """
    The software shall support conversion of TRLC source files into reStructuredText
    with a custom single document header and customer output file name.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_single_doc_custom")

    # Mock program arguments to simulate running the script with inbuild reStructuredText converter.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--out", str(tmp_path),
        "rst",
        "--single-document",
        "--name", "custom_output.rst",
        "--top-level", "Custom Specification"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Read the contents of the generated reStructuredText file and assert it is the expected valid reStructuredText.
    with open(tmp_path / "custom_output.rst", "r", encoding='utf-8') as generated_rst:
        lines = generated_rst.readlines()
        assert lines[0] == ".. _custom_output.rst-custom-specification:\n" # Label
        assert lines[1] == "\n"
        assert lines[2] == "Custom Specification\n"
        assert lines[3] == "====================\n"
        assert lines[4] == "\n"
        assert lines[5] == ".. _custom_output.rst-req\\_id\\_1:\n" # Label
        assert lines[6] == "\n"
        assert lines[7] == ".. admonition:: req\\_id\\_1\n"
        assert lines[8] == "\n"
        assert lines[9] == "    +----------------+------------------+\n"
        assert lines[10] == "    | Attribute Name | Attribute Value  |\n"
        assert lines[11] == "    +================+==================+\n"
        assert lines[12] == "    | description    | Test description |\n"
        assert lines[13] == "    +----------------+------------------+\n"
        assert lines[14] == "    | link           | N/A              |\n"
        assert lines[15] == "    +----------------+------------------+\n"

def test_tc_rst_multi_doc(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_rst_multi_doc
    """
    The software shall support conversion of TRLC source files into reStructuredText
    files with one output file per TRLC source file.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_multi_doc")

    # Mock program arguments to simulate running the script with inbuild reStructuredText converter.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils",
        "--out", str(tmp_path),
        "rst"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Read the contents of the generated reStructuredText file and assert it is the expected valid reStructuredText.
    with open(tmp_path / "single_req_no_section.rst", "r", encoding='utf-8') as generated_rst:
        lines = generated_rst.readlines()
        assert lines[0] == ".. _single_req_no_section.rst-req\\_id\\_1:\n" # Label
        assert lines[1] == "\n"
        assert lines[2] == ".. admonition:: req\\_id\\_1\n"
        assert lines[3] == "\n"
        assert lines[4] == "    +----------------+------------------+\n"
        assert lines[5] == "    | Attribute Name | Attribute Value  |\n"
        assert lines[6] == "    +================+==================+\n"
        assert lines[7] == "    | description    | Test description |\n"
        assert lines[8] == "    +----------------+------------------+\n"
        assert lines[9] == "    | link           | N/A              |\n"
        assert lines[10] == "    +----------------+------------------+\n"

    with open(tmp_path / "single_req_with_link.rst", "r", encoding='utf-8') as generated_rst:
        lines = generated_rst.readlines()
        assert lines[0] == ".. _single_req_with_link.rst-req\\_id\\_3:\n" # Label
        assert lines[1] == "\n"
        assert lines[2] == ".. admonition:: req\\_id\\_3\n"
        assert lines[3] == "\n"
        # pylint: disable=line-too-long
        assert lines[4] == "    +----------------+------------------------------------------------------------------------+\n"
        assert lines[5] == "    | Attribute Name | Attribute Value                                                        |\n"
        assert lines[6] == "    +================+========================================================================+\n"
        assert lines[7] == "    | description    | Test description                                                       |\n"
        assert lines[8] == "    +----------------+------------------------------------------------------------------------+\n"
        assert lines[9] == "    | link           | :ref:`Requirements\\.req\\_id\\_2 <single_req_with_section.rst-req_id_2>` |\n"
        assert lines[10] == "    +----------------+------------------------------------------------------------------------+\n"

    with open(tmp_path / "single_req_with_section.rst", "r", encoding='utf-8') as generated_rst:
        lines = generated_rst.readlines()
        assert lines[0] == ".. _single_req_with_section.rst-test-section:\n" # Label
        assert lines[1] == "\n"
        assert lines[2] == "Test section\n"
        assert lines[3] == "============\n"
        assert lines[4] == "\n"
        assert lines[5] == ".. _single_req_with_section.rst-req\\_id\\_2:\n" # Label
        assert lines[6] == "\n"
        assert lines[7] == ".. admonition:: req\\_id\\_2\n"
        assert lines[8] == "\n"
        assert lines[9] == "    +----------------+------------------+\n"
        assert lines[10] == "    | Attribute Name | Attribute Value  |\n"
        assert lines[11] == "    +================+==================+\n"
        assert lines[12] == "    | description    | Test description |\n"
        assert lines[13] == "    +----------------+------------------+\n"
        assert lines[14] == "    | link           | N/A              |\n"
        assert lines[15] == "    +----------------+------------------+\n"
