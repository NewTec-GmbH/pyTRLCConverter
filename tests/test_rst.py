"""Test the reStructuredText requirements.
"""
# pylint: disable=too-many-lines

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

# Imports **********************************************************************
import os
from unittest.mock import patch

from collections import namedtuple

from pyTRLCConverter.__main__ import main
from pyTRLCConverter.rst_converter import RstConverter
from pyTRLCConverter.rst.element import RstHeading, RstAdmonition, RstTable, RstBulletList, RstImage
from pyTRLCConverter.rst.text import RstText

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

def test_tc_rst_escape(record_property):
    # lobster-trace: SwTests.tc_rst_escape
    """
    The reStructuredText converter shall support reStructuredText escaping.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
    """
    record_property("lobster-trace", "SwTests.tc_rst_escape")

    # Escaping rules see https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#escaping-mechanism
    EscapingResult = namedtuple("EscapingResult", ["initial", "escaped"])
    checks = [
        EscapingResult(initial=r'I contain nothing weird', escaped=r"I contain nothing weird"),
        EscapingResult(initial=r'I_contain.something+weird', escaped=r"I\_contain\.something\+weird"),
        EscapingResult(initial=r'\`*_{}[]()#+-.!', escaped=r"\\\`\*\_\{\}\[\]\(\)\#\+\-\.\!"),
        EscapingResult(initial=r'unchanged', escaped=r"unchanged")
    ]

    for check in checks:
        assert RstText.escape(check.initial) == check.escaped

def test_tc_rst_heading(record_property):
    # lobster-trace: SwTests.tc_rst_heading
    """
    The reStructuredText converter shall provide a function to create reStructuredText headings.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
    """
    record_property("lobster-trace", "SwTests.tc_rst_heading")

    # Test the heading function. Levels 1-6 need to be supported.
    underline_chars = ["=", "#", "~", "^", "\"", "+", "'"]

    for level, underline_char in enumerate(underline_chars):
        lines = RstHeading("Heading", level + 1, "test.rst").render().split('\n')
        assert lines[0] == ".. _test.rst-heading:" # Label
        assert lines[1] == ""
        assert lines[2] == "Heading"
        assert lines[3] == underline_char * len("Heading")

    # Invalid level shall return a empty string.
    assert RstHeading("Heading", 0, "test.rst").render() == ""
    assert RstHeading("Heading", 8, "test.rst").render() == ""

def test_tc_rst_admonition(record_property):
    # lobster-trace: SwTests.tc_rst_admonition
    """
    The reStructuredText converter shall provide a function to create reStructuredText admonition.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
    """
    record_property("lobster-trace", "SwTests.tc_rst_admonition")

    # Test the admonition function.
    lines = RstAdmonition("Test text", "test.rst").render().split('\n')
    assert lines[0] == ".. _test.rst-test-text:" # Label
    assert lines[1] == ""
    assert lines[2] == ".. admonition:: Test text"

def test_tc_rst_table(record_property):
    # lobster-trace: SwTests.tc_rst_table
    """
    The reStructuredText converter shall provide the functionality to create reStructuredText tables.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
    """
    record_property("lobster-trace", "SwTests.tc_rst_table")

    # Create a table with a head and two rows. The column width is driven by the
    # widest cell content of each column.
    headers = ["Header1", "Header2"]
    rows = [["Value1", "Value2"], ["Value3", "Value4"]]
    table_lines = RstTable(headers, rows).render().split('\n')

    # Table head.
    assert table_lines[0] == "    +---------+---------+"
    assert table_lines[1] == "    | Header1 | Header2 |"
    assert table_lines[2] == "    +=========+=========+"

    # First table row.
    assert table_lines[3] == "    | Value1  | Value2  |"
    assert table_lines[4] == "    +---------+---------+"

    # Second table row.
    assert table_lines[5] == "    | Value3  | Value4  |"
    assert table_lines[6] == "    +---------+---------+"

def test_tc_rst_list(record_property):
    # lobster-trace: SwTests.tc_rst_list
    """
    The reStructuredText converter shall provide the functionality to create reStructuredText lists.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
    """
    record_property("lobster-trace", "SwTests.tc_rst_list")

    # Create a list with items.
    items = ["Item1", "Item2!", "Item3"]
    list_output = RstBulletList(items, escape=True).render()
    assert list_output == "* Item1\n* Item2\\!\n* Item3"

    # Without escaping the values are taken as is.
    assert RstBulletList([":ref:`a <x>`", ":ref:`b <y>`"], escape=False).render() == \
        "* :ref:`a <x>`\n* :ref:`b <y>`"

def test_tc_rst_link(record_property):
    # lobster-trace: SwTests.tc_rst_link
    """
    The reStructuredText converter shall provide the functionality to create reStructuredText links.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
    """
    record_property("lobster-trace", "SwTests.tc_rst_link")

    # Create a reStructuredText link. Escaping should only apply to the text, not the url.
    assert RstText.link("Link Text", "http://example.com") == \
        ":ref:`Link Text <http://example.com>`"
    assert RstText.link("Another Link", "https://example.org") == \
        ":ref:`Another Link <https://example.org>`"
    assert RstText.link("Special Characters", "http://example.com/path?query=1&other=2") == \
        ":ref:`Special Characters <http://example.com/path?query=1&other=2>`"
    assert RstText.link("Special Characters", "http://example.com/path%20with%20spaces", \
        escape=True) == \
        ":ref:`Special Characters <http://example.com/path%20with%20spaces>`"
    assert RstText.link("Link with special characters!", "http://example.com") == \
        r":ref:`Link with special characters\! <http://example.com>`"
    assert RstText.link("Link with special characters!", "http://example.com", escape=False) == \
        ":ref:`Link with special characters! <http://example.com>`"

def test_tc_rst_image(record_property):
    # lobster-trace: SwTests.tc_rst_image
    """
    The reStructuredText converter shall provide the functionality to embed images in reStructuredText.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
    """
    record_property("lobster-trace", "SwTests.tc_rst_image")

    # Create a reStructuredText diagram link. Absolute and relative paths shall be supported.
    diagram_path = "/diagram.png"
    assert RstImage(f"{diagram_path}", "Caption").render() == \
        f".. figure:: {os.path.normpath(diagram_path)}\n    :alt: Caption\n\n    Caption\n"

    diagram_path = "diagram.png"
    assert RstImage(f"{diagram_path}", "Caption").render() == \
        f".. figure:: {os.path.normpath(diagram_path)}\n    :alt: Caption\n\n    Caption\n"

    diagram_path = "./graph.jpg"
    assert RstImage("./graph.jpg", "Caption with special characters!").render() == \
        f".. figure:: {os.path.normpath(diagram_path)}\n    :alt: Caption with special characters\\!\n\n    Caption with special characters\\!\n" # pylint: disable=line-too-long

    diagram_path = "./I/am/nested.png"
    assert RstImage(
        "./I/am/nested.png",
        "Caption with special characters!",
        escape=False).render() == \
        f".. figure:: {os.path.normpath(diagram_path)}\n    :alt: Caption with special characters!\n\n    Caption with special characters!\n" # pylint: disable=line-too-long

def test_tc_rst_role(record_property):
    # lobster-trace: SwTests.tc_rst_role
    """
    The reStructuredText converter shall provide the functionality to create reStructuredText role text output.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
    """
    record_property("lobster-trace", "SwTests.tc_rst_role")

    # Test role text output.
    assert RstText.role("Text", "red") == ":red:`Text`"
    assert RstText.role("Text", "green") == ":green:`Text`"
    assert RstText.role("Text", "blue") == ":blue:`Text`"
    assert RstText.role("!Text!", "yellow") == ":yellow:`\\!Text\\!`"
    assert RstText.role("!Text!", "bad", escape=False) == ":bad:`!Text!`"

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

def test_tc_rst_single_doc_exclude(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_cli_exclude
    """
    The software shall support excluding specific files from the conversion.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_cli_exclude")

    # Mock program arguments to specify an output folder.
    output_file_name = "myReq.rst"
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--source", "./tests/utils/single_req_with_link.trlc",
        "--source", "./tests/utils/single_req_with_section.trlc",
        "--exclude", "./tests/utils/single_req_no_section.trlc",
        "--exclude", "./tests/utils/single_req_with_section.trlc",
        "--out", str(tmp_path),
        "rst",
        "--single-document",
        "--name", output_file_name
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Verify
    with open(os.path.join(tmp_path, output_file_name), "r", encoding='utf-8') as generated_rst:
        lines = generated_rst.readlines()
        assert lines[0] == ".. _myReq.rst-specification:\n" # Label
        assert lines[1] == "\n"
        assert lines[2] == "Specification\n"
        assert lines[3] == "=============\n"
        assert lines[4] == "\n"
        assert lines[5] == ".. _myReq.rst-req\\_id\\_3:\n" # Label
        assert lines[6] == "\n"
        assert lines[7] == ".. admonition:: req\\_id\\_3\n"
        assert lines[8] == "\n"
        # pylint: disable-next=line-too-long
        assert lines[9] == "    +----------------+------------------------------------------------------------------------+\n"
        # pylint: disable-next=line-too-long
        assert lines[10] == "    | Attribute Name | Attribute Value                                                        |\n"
        # pylint: disable-next=line-too-long
        assert lines[11] == "    +================+========================================================================+\n"
        # pylint: disable-next=line-too-long
        assert lines[12] == "    | description    | Test description                                                       |\n"
        # pylint: disable-next=line-too-long
        assert lines[13] == "    +----------------+------------------------------------------------------------------------+\n"
        # pylint: disable-next=line-too-long
        assert lines[14] == "    | link           | :ref:`Requirements\\.req\\_id\\_2 <single_req_with_section.rst-req_id_2>` |\n"
        # pylint: disable-next=line-too-long
        assert lines[15] == "    +----------------+------------------------------------------------------------------------+\n"

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
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--source", "./tests/utils/single_req_with_link.trlc",
        "--source", "./tests/utils/single_req_with_section.trlc",
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
        # pylint: disable-next=line-too-long
        assert lines[4] == "    +----------------+------------------------------------------------------------------------+\n"
        # pylint: disable-next=line-too-long
        assert lines[5] == "    | Attribute Name | Attribute Value                                                        |\n"
        # pylint: disable-next=line-too-long
        assert lines[6] == "    +================+========================================================================+\n"
        # pylint: disable-next=line-too-long
        assert lines[7] == "    | description    | Test description                                                       |\n"
        # pylint: disable-next=line-too-long
        assert lines[8] == "    +----------------+------------------------------------------------------------------------+\n"
        # pylint: disable-next=line-too-long
        assert lines[9] == "    | link           | :ref:`Requirements\\.req\\_id\\_2 <single_req_with_section.rst-req_id_2>` |\n"
        # pylint: disable-next=line-too-long
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

def test_tc_rst_string_format(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_rst_string_format
    """
    The forstare shall not escape stings that are already in reStructuredText format.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_string_format")

    # Mock program arguments to specify an output folder.
    output_file_name = "myReq.rst"
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_rst.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfgRst.json",
        "rst",
        "--single-document",
        "--name", output_file_name
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Verify
    with open(os.path.join(tmp_path, output_file_name), "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        assert "| description    | Heading 1           " in lines[12]
        assert "|                | =========           " in lines[13]
        assert "|                |                     " in lines[14]
        assert "|                | Heading 2           " in lines[15]
        assert "|                | ---------           " in lines[16]
        assert "|                |                     " in lines[17]
        assert "|                | - Bullet point 1    " in lines[18]
        assert "|                | - Bullet point 2    " in lines[19]
        assert "|                |   - Sub bullet point" in lines[20]

# pylint: disable-next=too-many-statements
def test_tc_rst_render_md(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_rst_render_md
    """
    The software shall support rendering requirement attributes containing CommonMark Markdown syntax.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_render_md")

    # Mock program arguments to specify an output folder.
    output_file_name = "myReq.rst"
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_md.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfg.json",
        "rst",
        "--single-document",
        "--name", output_file_name
    ])

    svg_payload = (
        b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>'
    )
    with patch("pyTRLCConverter.marko.md2rst_renderer.PlantUML.generate_to_bytes",
               return_value=svg_payload):
        main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Verify
    with open(os.path.join(tmp_path, output_file_name), "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        assert lines[0] == ".. _myReq.rst-specification:\n"
        assert lines[1] == "\n"
        assert lines[2] == "Specification\n"
        assert lines[3] == "=============\n"
        assert lines[4] == "\n"
        assert lines[5] == ".. _myReq.rst-req\\_id\\_md:\n"
        assert lines[6] == "\n"
        assert lines[7] == ".. admonition:: req\\_id\\_md\n"
        assert lines[8] == "\n"
        # pylint: disable=line-too-long
        assert lines[9] == "    +----------------+-----------------------------------------------------------------------------+\n"
        assert lines[10] == "    | Attribute Name | Attribute Value                                                             |\n"
        assert lines[11] == "    +================+=============================================================================+\n"
        assert lines[12] == "    | description    | .. rubric:: Heading 1                                                       |\n"
        assert lines[13] == "    |                |                                                                             |\n"
        assert lines[14] == "    |                | .. rubric:: Heading 2                                                       |\n"
        assert lines[15] == "    |                |                                                                             |\n"
        assert lines[16] == "    |                | - Bullet point 1                                                            |\n"
        assert lines[17] == "    |                |                                                                             |\n"
        assert lines[18] == "    |                |                                                                             |\n"
        assert lines[19] == "    |                | - Bullet point 2                                                            |\n"
        assert lines[20] == "    |                |                                                                             |\n"
        assert lines[21] == "    |                |   - Sub bullet point 1                                                      |\n"
        assert lines[22] == "    |                |                                                                             |\n"
        assert lines[23] == "    |                |                                                                             |\n"
        assert lines[24] == "    |                |   - Sub bullet point 2                                                      |\n"
        assert lines[25] == "    |                |                                                                             |\n"
        assert lines[26] == "    |                |                                                                             |\n"
        assert lines[27] == "    |                |                                                                             |\n"
        assert lines[28] == "    |                |                                                                             |\n"
        assert lines[29] == "    |                | 1. Numbered point 1                                                         |\n"
        assert lines[30] == "    |                |                                                                             |\n"
        assert lines[31] == "    |                |                                                                             |\n"
        assert lines[32] == "    |                | 2. Numbered point 2                                                         |\n"
        assert lines[33] == "    |                |                                                                             |\n"
        assert lines[34] == "    |                |   1. Sub numbered point 1                                                   |\n"
        assert lines[35] == "    |                |                                                                             |\n"
        assert lines[36] == "    |                |                                                                             |\n"
        assert lines[37] == "    |                |   2. Sub numbered point 2                                                   |\n"
        assert lines[38] == "    |                |                                                                             |\n"
        assert lines[39] == "    |                |                                                                             |\n"
        assert lines[40] == "    |                |                                                                             |\n"
        assert lines[41] == "    |                |                                                                             |\n"
        assert lines[42] == "    |                | **Bold text** and *italic text*.                                            |\n"
        assert lines[43] == "    |                |                                                                             |\n"
        assert lines[44] == "    |                |                                                                             |\n"
        assert lines[45] == "    |                | .. code-block::                                                             |\n"
        assert lines[46] == "    |                |                                                                             |\n"
        assert lines[47] == "    |                |     Code block example                                                      |\n"
        assert lines[48] == "    |                |                                                                             |\n"
        assert lines[49] == "    |                |                                                                             |\n"
        assert ".. image:: plantuml_" in lines[50]
        assert lines[50].endswith(".svg                                        |\n")
        assert lines[51] == "    |                |                                                                             |\n"
        assert lines[52] == "    |                |                                                                             |\n"
        assert lines[53] == "    |                |                                                                             |\n"
        assert lines[54] == "    |                | |                                                                           |\n"
        assert lines[55] == "    |                |                                                                             |\n"
        assert lines[56] == "    |                |   Blockquote example                                                        |\n"
        assert lines[57] == "    |                |                                                                             |\n"
        assert lines[58] == "    |                |                                                                             |\n"
        assert lines[59] == "    |                |                                                                             |\n"
        assert lines[60] == "    |                | `Link to pyTRLCConverter <https://github.com/NewTec-GmbH/pyTRLCConverter>`_ |\n"
        assert lines[61] == "    |                |                                                                             |\n"
        assert lines[62] == "    |                |                                                                             |\n"
        assert lines[63] == "    +----------------+-----------------------------------------------------------------------------+\n"
        assert lines[64] == "    | link           | N/A                                                                         |\n"
        assert lines[65] == "    +----------------+-----------------------------------------------------------------------------+\n"
        assert lines[66] == "    | index          | N/A                                                                         |\n"
        assert lines[67] == "    +----------------+-----------------------------------------------------------------------------+\n"
        assert lines[68] == "    | precision      | N/A                                                                         |\n"
        assert lines[69] == "    +----------------+-----------------------------------------------------------------------------+\n"
        assert lines[70] == "    | valid          | N/A                                                                         |\n"
        assert lines[71] == "    +----------------+-----------------------------------------------------------------------------+\n"

# pylint: disable-next=too-many-statements
def test_tc_rst_render_gfm(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_rst_render_gfm
    """
    The software shall support rendering requirement attributes containing GitHub Flavored Markdown syntax.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_render_gfm")

    # Mock program arguments to specify an output folder.
    output_file_name = "myReq.rst"
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_gfm.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfgGfm.json",
        "rst",
        "--single-document",
        "--name", output_file_name
    ])

    svg_payload = (
        b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>'
    )
    with patch("pyTRLCConverter.marko.md2rst_renderer.PlantUML.generate_to_bytes",
               return_value=svg_payload):
        main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Verify
    with open(os.path.join(tmp_path, output_file_name), "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        assert lines[0] == ".. _myReq.rst-specification:\n"
        assert lines[1] == "\n"
        assert lines[2] == "Specification\n"
        assert lines[3] == "=============\n"
        assert lines[4] == "\n"
        assert lines[5] == ".. _myReq.rst-req\\_id\\_gfm:\n"
        assert lines[6] == "\n"
        assert lines[7] == ".. admonition:: req\\_id\\_gfm\n"
        assert lines[8] == "\n"
        # pylint: disable=line-too-long
        # pylint: disable=line-too-long
        assert lines[9] == "    +----------------+----------------------------------------------------------------------------------------------------+\n"
        assert lines[10] == "    | Attribute Name | Attribute Value                                                                                    |\n"
        assert lines[11] == "    +================+====================================================================================================+\n"
        assert lines[12] == "    | description    | .. rubric:: Heading 1                                                                              |\n"
        assert lines[13] == "    |                |                                                                                                    |\n"
        assert lines[14] == "    |                | .. rubric:: Heading 2                                                                              |\n"
        assert lines[15] == "    |                |                                                                                                    |\n"
        assert lines[16] == "    |                | - Bullet point 1                                                                                   |\n"
        assert lines[17] == "    |                |                                                                                                    |\n"
        assert lines[18] == "    |                |                                                                                                    |\n"
        assert lines[19] == "    |                | - Bullet point 2                                                                                   |\n"
        assert lines[20] == "    |                |                                                                                                    |\n"
        assert lines[21] == "    |                |   - Sub bullet point 1                                                                             |\n"
        assert lines[22] == "    |                |                                                                                                    |\n"
        assert lines[23] == "    |                |                                                                                                    |\n"
        assert lines[24] == "    |                |   - Sub bullet point 2                                                                             |\n"
        assert lines[25] == "    |                |                                                                                                    |\n"
        assert lines[26] == "    |                |                                                                                                    |\n"
        assert lines[27] == "    |                |                                                                                                    |\n"
        assert lines[28] == "    |                |                                                                                                    |\n"
        assert lines[29] == "    |                | 1. Numbered point 1                                                                                |\n"
        assert lines[30] == "    |                |                                                                                                    |\n"
        assert lines[31] == "    |                |                                                                                                    |\n"
        assert lines[32] == "    |                | 2. Numbered point 2                                                                                |\n"
        assert lines[33] == "    |                |                                                                                                    |\n"
        assert lines[34] == "    |                |   1. Sub numbered point 1                                                                          |\n"
        assert lines[35] == "    |                |                                                                                                    |\n"
        assert lines[36] == "    |                |                                                                                                    |\n"
        assert lines[37] == "    |                |   2. Sub numbered point 2                                                                          |\n"
        assert lines[38] == "    |                |                                                                                                    |\n"
        assert lines[39] == "    |                |                                                                                                    |\n"
        assert lines[40] == "    |                |                                                                                                    |\n"
        assert lines[41] == "    |                |                                                                                                    |\n"
        assert lines[42] == "    |                | **Bold text** and *italic text*.                                                                   |\n"
        assert lines[43] == "    |                |                                                                                                    |\n"
        assert lines[44] == "    |                |                                                                                                    |\n"
        assert lines[45] == "    |                | - [x] Checked task                                                                                 |\n"
        assert lines[46] == "    |                |                                                                                                    |\n"
        assert lines[47] == "    |                |                                                                                                    |\n"
        assert lines[48] == "    |                | - [ ] Unchecked task                                                                               |\n"
        assert lines[49] == "    |                |                                                                                                    |\n"
        assert lines[50] == "    |                |                                                                                                    |\n"
        assert lines[51] == "    |                |                                                                                                    |\n"
        assert lines[52] == "    |                | .. code-block::                                                                                    |\n"
        assert lines[53] == "    |                |                                                                                                    |\n"
        assert lines[54] == "    |                |     Code block example                                                                             |\n"
        assert lines[55] == "    |                |                                                                                                    |\n"
        assert lines[56] == "    |                |                                                                                                    |\n"
        assert ".. image:: plantuml_" in lines[57]
        assert lines[57].endswith(".svg                                                               |\n")
        assert lines[58] == "    |                |                                                                                                    |\n"
        assert lines[59] == "    |                |                                                                                                    |\n"
        assert lines[60] == "    |                |                                                                                                    |\n"
        assert lines[61] == "    |                | |                                                                                                  |\n"
        assert lines[62] == "    |                |                                                                                                    |\n"
        assert lines[63] == "    |                | `https://github.com/NewTec-GmbH/pyTRLCConverter <https://github.com/NewTec-GmbH/pyTRLCConverter>`_ |\n"
        assert lines[64] == "    |                |                                                                                                    |\n"
        assert lines[65] == "    |                |                                                                                                    |\n"
        assert lines[66] == "    |                |   Blockquote example                                                                               |\n"
        assert lines[67] == "    |                |                                                                                                    |\n"
        assert lines[68] == "    |                |                                                                                                    |\n"
        assert lines[69] == "    |                |                                                                                                    |\n"
        assert lines[70] == "    |                | `Link to pyTRLCConverter <https://github.com/NewTec-GmbH/pyTRLCConverter>`_                        |\n"
        assert lines[71] == "    |                |                                                                                                    |\n"
        assert lines[72] == "    |                |                                                                                                    |\n"
        assert lines[73] == "    |                | +-------+-------+                                                                                  |\n"
        assert lines[74] == "    |                | | Col 0 | Col 1 |                                                                                  |\n"
        assert lines[75] == "    |                | +=======+=======+                                                                                  |\n"
        assert lines[76] == "    |                | | A     | B     |                                                                                  |\n"
        assert lines[77] == "    |                | +-------+-------+                                                                                  |\n"
        assert lines[78] == "    |                |                                                                                                    |\n"
        assert lines[79] == "    |                |                                                                                                    |\n"
        assert lines[80] == "    |                | ~~I am strikethrough.~~                                                                            |\n"
        assert lines[81] == "    |                |                                                                                                    |\n"
        assert lines[82] == "    |                |                                                                                                    |\n"
        assert lines[83] == "    +----------------+----------------------------------------------------------------------------------------------------+\n"
        assert lines[84] == "    | link           | N/A                                                                                                |\n"
        assert lines[85] == "    +----------------+----------------------------------------------------------------------------------------------------+\n"
        assert lines[86] == "    | index          | N/A                                                                                                |\n"
        assert lines[87] == "    +----------------+----------------------------------------------------------------------------------------------------+\n"
        assert lines[88] == "    | precision      | N/A                                                                                                |\n"
        assert lines[89] == "    +----------------+----------------------------------------------------------------------------------------------------+\n"
        assert lines[90] == "    | valid          | N/A                                                                                                |\n"
        assert lines[91] == "    +----------------+----------------------------------------------------------------------------------------------------+\n"


def test_tc_rst_render_plantuml(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_rst_render_plantuml
    """A plantuml fenced code block in a Markdown attribute shall be rendered as a
    reStructuredText ``.. image::`` directive referencing a generated SVG file copied
    to the output folder.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_render_plantuml")

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_md.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfg.json",
        "rst",
        "--single-document",
    ])

    svg_payload = (
        b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>'
    )

    with patch("pyTRLCConverter.marko.md2rst_renderer.PlantUML.generate_to_bytes",
               return_value=svg_payload):
        main()

    captured = capsys.readouterr()
    assert captured.err == ""

    rst_content = (tmp_path / RstConverter.OUTPUT_FILE_NAME_DEFAULT).read_text(encoding="utf-8")

    assert ".. image::" in rst_content

    svg_files = [f for f in os.listdir(tmp_path)
                 if f.startswith("plantuml_") and f.endswith(".svg")]
    assert len(svg_files) == 1
    assert svg_files[0] in rst_content

    assert (tmp_path / svg_files[0]).read_bytes() == svg_payload


def test_tc_rst_render_plantuml_error(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_rst_render_plantuml_error
    """If PlantUML is not available, a plantuml fenced code block shall be replaced by a
    [PlantUML error: ...] paragraph instead of failing the conversion.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_rst_render_plantuml_error")

    monkeypatch.delenv("PLANTUML", raising=False)

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_md.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfg.json",
        "rst",
        "--single-document",
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    rst_content = (tmp_path / RstConverter.OUTPUT_FILE_NAME_DEFAULT).read_text(encoding="utf-8")

    assert "[PlantUML error:" in rst_content

    svg_files = [f for f in os.listdir(tmp_path)
                 if f.startswith("plantuml_") and f.endswith(".svg")]
    assert len(svg_files) == 0

# Main *************************************************************************
