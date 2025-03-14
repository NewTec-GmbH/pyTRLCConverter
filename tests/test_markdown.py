"""Test the markdown requirements.
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
from pyTRLCConverter.markdown_converter import MarkdownConverter

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

def test_tc_markdown(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_markdown
    """
    The software shall support conversion of TRLC source files into Markdown.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown")

    # Mock program arguments to simulate running the script with inbuild Markdown converter.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--out", str(tmp_path),
        "markdown",
        "--single-document",
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Read the contents of the generated Markdown file and assert it is the expected valid Markdown.
    with open(tmp_path / "output.md", "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        assert lines[0] == "# Specification\n"  # Default top level name
        assert lines[1] == "\n"
        assert lines[2] == r"### req\_id\_1" + "\n"  # Expect lvl3 heading as section heading would be lvl2.
        assert lines[3] == "\n"
        assert lines[4] == r"| Attribute Name | Attribute Value |" + "\n"
        assert lines[5] == r"| -------------- | --------------- |" + "\n"
        assert lines[6] == r"| description | Test description |" + "\n"

def test_tc_markdown_section(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_markdown_section
    """
    The software shall support conversion of TRLC sections into Markdown headings.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_section")

    # Mock program arguments to convert TRLC containing a section.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_with_section.trlc",
        "--out", str(tmp_path),
        "markdown",
        "--single-document",
        "--name", "custom.md",
        "--top-level", "Requirement Specification",
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Read the contents of the generated Markdown file and assert it is the expected valid Markdown.
    with open(tmp_path / "custom.md", "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        assert lines[0] == "# Requirement Specification\n"
        assert lines[1] == "\n"
        assert lines[2] == r"## Test section" + "\n"
        assert lines[3] == "\n"
        assert lines[4] == r"### req\_id\_2" + "\n"
        assert lines[5] == "\n"
        assert lines[6] == r"| Attribute Name | Attribute Value |" + "\n"
        assert lines[7] == r"| -------------- | --------------- |" + "\n"
        assert lines[8] == r"| description | Test description |" + "\n"


def test_tc_markdown_escape(record_property, tmp_path):
    # lobster-trace: SwTests.tc_markdown_escape
    """
    The Markdown converter shall support Markdown escaping.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_escape")

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path)))

    # Escaping rules see https://daringfireball.net/projects/markdown/syntax#misc
    EscapingResult = namedtuple("EscapingResult", ["initial", "escaped"])
    checks = [
        EscapingResult(initial=r'I contain nothing weird', escaped=r"I contain nothing weird"),
        EscapingResult(initial=r'I_contain.something+weird', escaped=r"I\_contain\.something\+weird"),
        EscapingResult(initial=r'\`*_{}[]()#+-.!', escaped=r"\\\`\*\_\{\}\[\]\(\)\#\+\-\.\!"),
        EscapingResult(initial=r'unchanged', escaped=r"unchanged")
    ]

    for check in checks:
        assert markdown_converter.markdown_escape(check.initial) == check.escaped


def test_tc_markdown_heading(record_property, tmp_path):
    # lobster-trace: SwTests.tc_markdown_heading
    """
    The Markdown converter shall provide a function to create Markdown headings.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_heading")

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path)))

    # Test the heading function. Levels 1-6 need to be supported.
    assert markdown_converter.markdown_create_heading("Heading", 1) == r"# Heading" + "\n"
    assert markdown_converter.markdown_create_heading("Heading", 2) == r"## Heading" + "\n"
    assert markdown_converter.markdown_create_heading("Heading", 3) == r"### Heading" + "\n"
    assert markdown_converter.markdown_create_heading("Heading", 4) == r"#### Heading" + "\n"
    assert markdown_converter.markdown_create_heading("Heading", 5) == r"##### Heading" + "\n"
    assert markdown_converter.markdown_create_heading("Heading", 6) == r"###### Heading" + "\n"
    assert markdown_converter.markdown_create_heading("Chapter.2", 2) == r"## Chapter\.2" + "\n"
    assert markdown_converter.markdown_create_heading("Chapter.2", 2, escape=False) == r"## Chapter.2" + "\n"

    # Invalid level shall return a empty string.
    assert markdown_converter.markdown_create_heading("Heading", 0) == ""

def test_tc_markdown_table(record_property, tmp_path):
    # lobster-trace: SwTests.tc_markdown_table
    """
    The Markdown converter shall provide the functionality to create Markdown tables.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_table")

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path)))

    # Create a table header. Expect 2 lines. First containing the column titles, second the separator.
    assert markdown_converter.markdown_create_table_head(["Header1", "Header2"]).split('\n') == \
        [r"| Header1 | Header2 |", r"| ------- | ------- |", ""]
    assert markdown_converter.markdown_create_table_head(["Header1", "Header2", "Header3"]).split('\n') == \
        [r"| Header1 | Header2 | Header3 |", r"| ------- | ------- | ------- |", ""]
    assert markdown_converter.markdown_create_table_head(["Header!", "Header#"]).split('\n') == \
        [r"| Header\! | Header\# |", r"| -------- | -------- |", ""]
    assert markdown_converter.markdown_create_table_head(["Header!", "Header#"], escape=False).split('\n') == \
        [r"| Header! | Header# |", r"| ------- | ------- |", ""]

    # Create a table row.
    assert markdown_converter.markdown_append_table_row(["Value1", "Value2"]) == \
        r"| Value1 | Value2 |" + "\n"
    assert markdown_converter.markdown_append_table_row(["Value1", "Value2", "Value3"]) == \
        r"| Value1 | Value2 | Value3 |" + "\n"
    assert markdown_converter.markdown_append_table_row(["Value!", "Value#"]) == \
        r"| Value\! | Value\# |" + "\n"
    assert markdown_converter.markdown_append_table_row(["Value!", "Value#"], escape=False) == \
        r"| Value! | Value# |" + "\n"

def test_tc_markdown_link(record_property, tmp_path):
    # lobster-trace: SwTests.tc_markdown_link
    """
    The Markdown converter shall provide the functionality to create Markdown links.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_link")

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path)))

    # Create a Markdown link. Escaoubg should only apply to the text, not the url.
    assert markdown_converter.markdown_create_link("Link Text", "http://example.com") == \
        r"[Link Text](http://example.com)"
    assert markdown_converter.markdown_create_link("Another Link", "https://example.org") == \
        r"[Another Link](https://example.org)"
    assert markdown_converter.markdown_create_link("Special Characters", "http://example.com/path?query=1&other=2") == \
        r"[Special Characters](http://example.com/path?query=1&other=2)"
    assert markdown_converter.markdown_create_link(
        "Special Characters",
        "http://example.com/path%20with%20spaces",
         escape=True) == r"[Special Characters](http://example.com/path%20with%20spaces)"
    assert markdown_converter.markdown_create_link("Link with special characters!", "http://example.com") == \
        r"[Link with special characters\!](http://example.com)"
    assert markdown_converter.markdown_create_link(
        "Link with special characters!",
        "http://example.com",
         escape=False) == r"[Link with special characters!](http://example.com)"

def test_tc_markdown_image(record_property, tmp_path):
    # lobster-trace: SwTests.tc_markdown_image
    """
    The Markdown converter shall provide the functionality to embed images in Markdown.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_image")

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path)))

    # Create a Markdown diagram link. Absolute and relative paths shall be supported.
    diagram_path = "/diagram.png"
    assert markdown_converter.markdown_create_diagram_link(
        f"{diagram_path}",
        "Caption") == \
        f"![Caption]({os.path.normpath(diagram_path)})\n"

    diagram_path = "diagram.png"
    assert markdown_converter.markdown_create_diagram_link(
        f"{diagram_path}",
        "Caption") == \
        f"![Caption]({os.path.normpath(diagram_path)})\n"

    diagram_path = "./graph.jpg"
    assert markdown_converter.markdown_create_diagram_link(
        "./graph.jpg",
        "Caption with special characters!") == \
        f"![Caption with special characters\!]({os.path.normpath(diagram_path)})\n"

    diagram_path = "./I/am/nested.png"
    assert markdown_converter.markdown_create_diagram_link(
        "./I/am/nested.png",
        "Caption with special characters!",
        escape=False) == f"![Caption with special characters!]({os.path.normpath(diagram_path)})\n"

def test_tc_markdown_text_color(record_property, tmp_path):
    # lobster-trace: SwTests.tc_markdown_text_color
    """
    The Markdown converter shall provide the functionality to create colored Markdown text output.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_text_color")

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path)))

    # Test colored text output. HTML span element with style attribute should be used.
    assert markdown_converter.markdown_text_color("Text", "red") == r'<span style="red">Text</span>'
    assert markdown_converter.markdown_text_color("Text", "green") == r'<span style="green">Text</span>'
    assert markdown_converter.markdown_text_color("Text", "blue") == r'<span style="blue">Text</span>'
    assert markdown_converter.markdown_text_color("!Text!", "yellow") == r'<span style="yellow">\!Text\!</span>'
    assert markdown_converter.markdown_text_color("!Text!", "bad", escape=False) == r'<span style="bad">!Text!</span>'

def test_tc_markdown_soft_return(record_property, tmp_path):
    # lobster-trace: SwTests.tc_markdown_soft_return
    """
    The Markdown converter shall provide the functionality to convert line feeds to Markdown soft returns.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_soft_return")

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path)))

    # The markdown_lf2soft_return function is expected to replace line feeds with a backslash and newline.
    assert markdown_converter.markdown_lf2soft_return("Line 1\nLine 2") == "Line 1\\\nLine 2"
    assert markdown_converter.markdown_lf2soft_return("No newline") == "No newline"
    assert markdown_converter.markdown_lf2soft_return("Multiple\nLines\nHere") == "Multiple\\\nLines\\\nHere"
    assert markdown_converter.markdown_lf2soft_return("Ends with newline\n") == "Ends with newline\\\n"
    assert markdown_converter.markdown_lf2soft_return("\nStarts with newline") == "\\\nStarts with newline"

def test_tc_markdown_out_folder(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_markdown_out_folder
    """
    The software shall support specifying an output folder for the Markdown conversion.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_out_folder")

    # Mock program arguments to specify an output folder.
    output_folder = tmp_path / "output_folder"
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--out", str(output_folder),
        "markdown",
        "--single-document",
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Assert the output folder contains the generated Markdown file.
    assert output_folder.exists()
    assert (output_folder / "output.md").exists()

def test_tc_markdown_multi_doc(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_markdown_multi_doc
    """
    The software shall support conversion of TRLC source files into reStructuredText
    files with one output file per TRLC source file.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_multi_doc")

    # Mock program arguments to simulate running the script with inbuild reStructuredText converter.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils",
        "--out", str(tmp_path),
        "markdown"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Read the contents of the generated reStructuredText file and assert it is the expected valid reStructuredText.
    with open(tmp_path / "single_req_no_section.md", "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        assert lines[0] == "# Specification\n"
        assert lines[1] == "\n"
        assert lines[2] == r"## req\_id\_1" + "\n"
        assert lines[3] == "\n"
        assert lines[4] == r"| Attribute Name | Attribute Value |" + "\n"
        assert lines[5] == r"| -------------- | --------------- |" + "\n"
        assert lines[6] == r"| description | Test description |" + "\n"

    with open(tmp_path / "single_req_with_link.md", "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        assert lines[0] == "# Specification\n"
        assert lines[1] == "\n"
        assert lines[2] == r"## req\_id\_3" + "\n"
        assert lines[3] == "\n"
        assert lines[4] == r"| Attribute Name | Attribute Value |" + "\n"
        assert lines[5] == r"| -------------- | --------------- |" + "\n"
        assert lines[6] == r"| description | Test description |" + "\n"
        assert lines[7] == r"| link | [Requirements\.req\_id\_2](single_req_with_section.md#req_id_2) |" + "\n"

    with open(tmp_path / "single_req_with_section.md", "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        assert lines[0] == r"# Test section" + "\n"
        assert lines[1] == "\n"
        assert lines[2] == r"## req\_id\_2" + "\n"
        assert lines[3] == "\n"
        assert lines[4] == r"| Attribute Name | Attribute Value |" + "\n"
        assert lines[5] == r"| -------------- | --------------- |" + "\n"
        assert lines[6] == r"| description | Test description |" + "\n"
