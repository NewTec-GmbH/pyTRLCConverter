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

def _assert_heading(lines: list[str], level: int, text: str) -> int:
    """Helper function to assert a Markdown heading line.

    Args:
        lines (list[str]): The lines to check.
        level (int): The expected heading level (1-6).
        text (str): The expected heading text.

    Returns:
        int: The number of lines consumed (always 1).
    """
    expected_heading = "#" * level + " " + text + "\n"
    assert lines[0] == expected_heading
    return 1

def _assert_empty_line(lines: list[str]) -> int:
    """Helper function to assert an empty line.

    Args:
        lines (list[str]): The lines to check.

    Returns:
        int: The number of lines consumed (always 1).
    """
    assert lines[0] == "\n"
    return 1

def _assert_table(lines: list[str],
                  expected_headers: list[list[str]],
                  expected_rows: list[list[str]]) -> int:
    """Helper function to assert a Markdown table.

    Args:
        lines (list[str]): The lines to check.
        expected_headers (list[list[str]]): The expected table headers.
        expected_rows (list[list[str]]): The expected table rows.

    Returns:
        int: The number of lines consumed.
    """
    index = 0

    # Check for HTML table.
    assert lines[index] == "<table>\n"
    index += 1

    # Check for table header.
    assert lines[index] == "<thead>\n"
    index += 1

    # Check table header.
    for row in expected_headers:
        assert lines[index] == "<tr>\n"
        index += 1

        for cell in row:
            assert lines[index] == f"<th>{cell}</th>\n"
            index += 1

        assert lines[index] == "</tr>\n"
        index += 1

    assert lines[index] == "</thead>\n"
    index += 1

    # Check for table body.
    assert lines[index] == "<tbody>\n"
    index += 1

    # Check for table rows after header.
    for row in expected_rows:
        assert lines[index] == "<tr>\n"
        index += 1

        for cell in row:
            assert lines[index] == "<td>\n"
            index += 1
            assert lines[index] == "\n"
            index += 1

            # Get cell content line(s).
            content = ""
            while lines[index] != "</td>\n":
                content += lines[index]
                index += 1

            assert content == f"{cell}\n\n"

            assert lines[index] == "</td>\n"
            index += 1

        assert lines[index] == "</tr>\n"
        index += 1

    assert lines[index] == "</tbody>\n"
    index += 1

    assert lines[index] == "</table>\n"
    index += 1

    return index

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
        line_index = 0
        line_index += _assert_heading(lines[line_index:], 1, "Specification")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_heading(lines[line_index:], 3, r"req\_id\_1")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_table(lines[line_index:],
                                    [["Attribute Name", "Attribute Value"]],
                                    [["description", "Test description"],
                                     ["link", "N/A"],
                                     ["index", "1"],
                                     ["precision", "N/A"],
                                     ["valid", "N/A"]])

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
        line_index = 0
        line_index += _assert_heading(lines[line_index:], 1, "Requirement Specification")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_heading(lines[line_index:], 2, "Test section")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_heading(lines[line_index:], 3, r"req\_id\_2")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_table(lines[line_index:],
                                    [["Attribute Name", "Attribute Value"]],
                                    [["description", "Test description"],
                                     ["link", "N/A"],
                                     ["index", "N/A"],
                                     ["precision", "1/100"],
                                     ["valid", "N/A"]])


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

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path), exclude=None))

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

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path), exclude=None))

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

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path), exclude=None))

    # Create a table header. Expect 2 lines. First containing the column titles, second the separator.
    table = markdown_converter.markdown_create_table(["Header1", "Header2"], [["left", "center"]])
    lines = table.splitlines(keepends=True)
    line_index = 0
    line_index += _assert_table(lines, [["Header1", "Header2"]], [["left", "center"]])

def test_tc_markdown_list(record_property, tmp_path):
    # lobster-trace: SwTests.tc_markdown_list
    """
    The Markdown converter shall provide the functionality to create Markdown lists.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_list")

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path), exclude=None))

    # Create a Markdown list. Expect each item to be prefixed with a hyphen and space.
    markdown_list = markdown_converter.markdown_create_list(["Item1", "Item2"])
    assert markdown_list == "- Item1\n- Item2\n"

def test_tc_markdown_link(record_property, tmp_path):
    # lobster-trace: SwTests.tc_markdown_link
    """
    The Markdown converter shall provide the functionality to create Markdown links.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_markdown_link")

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path), exclude=None))

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

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path), exclude=None))

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
        fr"![Caption with special characters\!]({os.path.normpath(diagram_path)})" + "\n"

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

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path), exclude=None))

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

    markdown_converter = MarkdownConverter(Namespace(out=str(tmp_path), exclude=None))

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

def test_tc_markdown_single_doc_exclude(record_property, capsys, monkeypatch, tmp_path):
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
    output_file_name = "myReq.md"
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils",
        "--exclude", "./tests/utils/single_req_no_section.trlc",
        "--exclude", "./tests/utils/single_req_with_section.trlc",
        "--exclude", "./tests/utils/single_req_description_md.trlc",
        "--out", str(tmp_path),
        "markdown",
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
        line_index = 0
        line_index += _assert_heading(lines[line_index:], 1, "Specification")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_heading(lines[line_index:], 3, r"req\_id\_3")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_table(lines[line_index:],
                                    [["Attribute Name", "Attribute Value"]],
                                    [["description", "Test description"],
                                     ["link", r"[Requirements\.req\_id\_2](single_req_with_section.md#req_id_2)"],
                                     ["index", "N/A"],
                                     ["precision", "N/A"],
                                     ["valid", "False"]])

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

    # Mock program arguments to simulate running the script with inbuild Markdown converter.
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

    # Read the contents of the generated Markdown file and assert it is the expected valid Markdown.
    with open(tmp_path / "single_req_no_section.md", "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        line_index = 0
        line_index += _assert_heading(lines[line_index:], 1, "Specification")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_heading(lines[line_index:], 2, r"req\_id\_1")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_table(lines[line_index:],
                                    [["Attribute Name", "Attribute Value"]],
                                    [["description", "Test description"],
                                     ["link", "N/A"],
                                     ["index", "1"],
                                     ["precision", "N/A"],
                                     ["valid", "N/A"]])


    with open(tmp_path / "single_req_with_link.md", "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        line_index = 0
        line_index += _assert_heading(lines[line_index:], 1, "Specification")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_heading(lines[line_index:], 2, r"req\_id\_3")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_table(lines[line_index:],
                                    [["Attribute Name", "Attribute Value"]],
                                    [["description", "Test description"],
                                     ["link", r"[Requirements\.req\_id\_2](single_req_with_section.md#req_id_2)"],
                                     ["index", "N/A"],
                                     ["precision", "N/A"],
                                     ["valid", "False"]])

    with open(tmp_path / "single_req_with_section.md", "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        line_index = 0
        line_index += _assert_heading(lines[line_index:], 1, "Test section")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_heading(lines[line_index:], 2, r"req\_id\_2")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_table(lines[line_index:],
                                    [["Attribute Name", "Attribute Value"]],
                                    [["description", "Test description"],
                                     ["link", "N/A"],
                                     ["index", "N/A"],
                                     ["precision", "1/100"],
                                     ["valid", "N/A"]])

def test_tc_markdown_render_md(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_markdown_render_md
    """
    The software shall support rendering requirement attributes containing Markdown syntax.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_cli_exclude")

    # Mock program arguments to specify an output folder.
    output_file_name = "myReq.md"
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_md.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfg.json",
        "markdown",
        "--single-document",
        "--name", output_file_name
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    attribute_value = \
'''# Heading 1

## Heading 2

- Bullet point 1
- Bullet point 2
    - Sub bullet point 1
    - Sub bullet point 2

1. Numbered point 1
2. Numbered point 2
    1. Sub numbered point 1
    2. Sub numbered point 2

**Bold text**, *italic text* and __underlined text__.

```
Code block example
```

--- Divider ---

> Blockquote example

[Link to pyTRLCConverter](https://github.com/NewTec-GmbH/pyTRLCConverter)'''

    # Verify
    with open(os.path.join(tmp_path, output_file_name), "r", encoding='utf-8') as generated_md:
        lines = generated_md.readlines()
        line_index = 0
        line_index += _assert_heading(lines[line_index:], 1, "Specification")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_heading(lines[line_index:], 3, r"req\_id\_4")
        line_index += _assert_empty_line(lines[line_index:])
        line_index += _assert_table(lines[line_index:],
                                    [["Attribute Name", "Attribute Value"]],
                                    [["description", attribute_value],
                                     ["link", "N/A"],
                                     ["index", "N/A"],
                                     ["precision", "N/A"],
                                     ["valid", "N/A"]])
