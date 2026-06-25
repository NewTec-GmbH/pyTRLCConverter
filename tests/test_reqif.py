"""Test the ReqIF conversion requirements."""

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
import json
import os
import zipfile
from pathlib import Path
from unittest.mock import patch
from pyTRLCConverter.__main__ import main
from pyTRLCConverter.reqif_converter import ReqifConverter
from tests.reqif_test_utils import (
    _parse_reqif,
    _find_spec_object_by_long_name,
    _find_attribute_by_identifier,
    _find_attribute_identifier,
    _assert_reqif_v12_compliance,
    _collect_identifiers,
)

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

def test_tc_reqif(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif
    """The software shall support the conversion into ReqIF format.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif")

    # Mock program arguments to convert a single TRLC file to ReqIF in single-document mode.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Check that the default ReqIF output file was created.
    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    assert os.path.exists(output_file) is True

    # Parse the output file and verify the expected spec-object is present.
    bundle = _parse_reqif(output_file)
    spec_object = _find_spec_object_by_long_name(bundle, "req_id_1")

    assert spec_object is not None

    # Verify ReqIF v1.2 XSD compliance of the generated file.
    _assert_reqif_v12_compliance(output_file, tmp_path)


def test_tc_reqif_section(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_section
    """The ReqIF converter shall convert a TRLC section into a SPEC-HIERARCHY node without creating a SPEC-OBJECT.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_section")

    # Mock program arguments to convert a TRLC file where a record precedes the section.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_with_prev_section.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # No warning expected: req_id_1 precedes "Test section".
    assert captured.err == ""

    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    # "Test section" must NOT appear as a SPEC-OBJECT; only records produce spec-objects.
    section_object = _find_spec_object_by_long_name(bundle, "Test section")
    preceding_record = _find_spec_object_by_long_name(bundle, "req_id_1")
    nested_record = _find_spec_object_by_long_name(bundle, "req_id_2")

    assert section_object is None
    assert preceding_record is not None
    assert nested_record is not None

    # "Test section" must appear as a SPEC-HIERARCHY node referencing the preceding record.
    specification = bundle.core_content.req_if_content.specifications[0]
    section_hierarchy = next(
        (h for h in specification.children if h.long_name == "Test section"), None
    )
    assert section_hierarchy is not None
    assert section_hierarchy.spec_object == preceding_record.identifier

    # req_id_2 must be nested inside the "Test section" hierarchy.
    assert section_hierarchy.children is not None
    assert section_hierarchy.children[0].long_name == "req_id_2"


def test_tc_reqif_single_doc_custom(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_single_doc_custom
    """The ReqIF output file name shall be customizable in single document mode.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_single_doc_custom")

    custom_name = "custom.reqif"

    # Mock program arguments specifying a custom output file name and top-level title.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document",
        "--name", custom_name,
        "--top-level", "My Specification"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Check that the custom-named output file was created and is a valid ReqIF document.
    output_file = os.path.join(tmp_path, custom_name)
    assert os.path.exists(output_file) is True

    bundle = _parse_reqif(output_file)
    assert bundle.core_content is not None


def test_tc_reqif_render_md(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_render_md
    """The software shall render CommonMark Markdown content to ReqIF XHTML.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_render_md")

    # Mock program arguments with a CommonMark render configuration.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_md.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfg.json",
        "reqif",
        "--single-document"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Parse the output file and locate the expected spec-object.
    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    spec_object = _find_spec_object_by_long_name(bundle, "req_id_md")
    assert spec_object is not None

    # Locate the description attribute definition and corresponding attribute value.
    description_identifier = _find_attribute_identifier(bundle, "description")
    assert description_identifier is not None

    description_attribute = _find_attribute_by_identifier(spec_object, description_identifier)
    assert description_attribute is not None
    # Verify that Markdown heading syntax was rendered to HTML inside the XHTML wrapper.
    assert "Heading 1</h1>" in description_attribute.value


def test_tc_reqif_render_gfm(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_render_gfm
    """The software shall render GitHub Flavored Markdown content to ReqIF XHTML.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_render_gfm")

    # Mock program arguments with a GFM render configuration.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_gfm.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfgGfm.json",
        "reqif",
        "--single-document"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Parse the output file and locate the expected spec-object.
    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    spec_object = _find_spec_object_by_long_name(bundle, "req_id_gfm")
    assert spec_object is not None

    # Locate the description attribute definition and corresponding attribute value.
    description_identifier = _find_attribute_identifier(bundle, "description")
    assert description_identifier is not None

    description_attribute = _find_attribute_by_identifier(spec_object, description_identifier)
    assert description_attribute is not None
    # Verify that GFM strikethrough syntax was rendered to <del> HTML inside the XHTML wrapper.
    assert "I am strikethrough.</del>" in description_attribute.value


def test_tc_reqif_render_gfm_table_options(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_render_table_options
    """The software shall apply table border and heading style options when rendering GFM to ReqIF XHTML.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_render_table_options")

    # Mock program arguments with a GFM render configuration that includes table options.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_gfm.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfgGfmTableOptions.json",
        "reqif",
        "--single-document"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Parse the output file and locate the expected spec-object.
    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    spec_object = _find_spec_object_by_long_name(bundle, "req_id_gfm")
    assert spec_object is not None

    description_identifier = _find_attribute_identifier(bundle, "description")
    assert description_identifier is not None

    description_attribute = _find_attribute_by_identifier(spec_object, description_identifier)
    assert description_attribute is not None

    # Verify that the table border style was applied to the <table> element.
    assert 'style="border: 1px solid black; border-collapse: collapse;"' in description_attribute.value

    # Verify that the heading style was applied to the <th> cells.
    assert 'style="background-color: #c0c0c0;"' in description_attribute.value


def test_tc_reqif_render_xhtml(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_render_xhtml
    """The software shall pass XHTML content through to ReqIF XHTML without modification.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_render_xhtml")

    # Mock program arguments with an XHTML render configuration.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_xhtml.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfgXhtml.json",
        "reqif",
        "--single-document"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # Check that no errors were reported.
    assert captured.err == ""

    # Parse the output file and locate the expected spec-object.
    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    spec_object = _find_spec_object_by_long_name(bundle, "req_id_xhtml")
    assert spec_object is not None

    # Locate the description attribute definition and corresponding attribute value.
    description_identifier = _find_attribute_identifier(bundle, "description")
    assert description_identifier is not None

    description_attribute = _find_attribute_by_identifier(spec_object, description_identifier)
    assert description_attribute is not None
    # Verify that the XHTML content is passed through unchanged inside the wrapper.
    # Note: the reqif library re-serialises the parsed XML with explicit xmlns attributes on each
    # element, so closing tags like </strong> are still present verbatim in the value.
    assert "bold</strong>" in description_attribute.value
    assert "italic</em>" in description_attribute.value


def test_tc_reqif_render_path(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_render_path
    """The software shall render a path attribute as XHTML <object> and copy the referenced file.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_render_path")

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req_with_path.rsl",
        "--source", "./tests/utils/single_req_with_path.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfgPath.json",
        "reqif",
        "--single-document"
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    spec_object = _find_spec_object_by_long_name(bundle, "req_path")
    assert spec_object is not None

    file_path_identifier = _find_attribute_identifier(bundle, "file_path")
    assert file_path_identifier is not None

    file_path_attribute = _find_attribute_by_identifier(spec_object, file_path_identifier)
    assert file_path_attribute is not None
    # Verify the XHTML <object> element with MIME type and local file reference.
    assert "<object" in file_path_attribute.value
    assert 'data="attachment.txt"' in file_path_attribute.value
    assert 'type="text/plain"' in file_path_attribute.value

    # Verify the referenced file was copied to the output folder.
    assert os.path.isfile(os.path.join(tmp_path, "attachment.txt"))


def test_tc_reqif_render_path_reqifz(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_render_path_reqifz
    """The external file referenced by a path format attribute shall be bundled in the .reqifz archive.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_render_path_reqifz")

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req_with_path.rsl",
        "--source", "./tests/utils/single_req_with_path.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfgPath.json",
        "reqif",
        "--single-document",
        "--reqifz"
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    doc_name = os.path.splitext(ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)[0]
    reqifz_file = os.path.join(tmp_path, doc_name + ".reqifz")
    assert os.path.isfile(reqifz_file)

    with zipfile.ZipFile(reqifz_file, "r") as zf:
        names = zf.namelist()
        # The archive must contain the .reqif and the copied external file.
        assert doc_name + ".reqif" in names
        assert "attachment.txt" in names


def test_tc_reqif_reqifz(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_reqifz
    """The ReqIF converter shall produce a .reqifz ZIP archive when --reqifz is given.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_reqifz")

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document",
        "--reqifz"
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    # A subfolder named after the document is created; the .reqif lives inside it.
    doc_name = os.path.splitext(ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)[0]
    subfolder = os.path.join(tmp_path, doc_name)
    assert os.path.isdir(subfolder), f"Expected document subfolder not found: {subfolder}"
    assert os.path.isfile(os.path.join(subfolder, doc_name + ".reqif"))

    # The .reqifz in the output folder bundles all files from the subfolder.
    reqifz_file = os.path.join(tmp_path, doc_name + ".reqifz")
    assert os.path.isfile(reqifz_file), f"Expected .reqifz not found: {reqifz_file}"

    with zipfile.ZipFile(reqifz_file, "r") as zf:
        names = zf.namelist()
        assert len(names) == 1
        assert names[0] == doc_name + ".reqif"
        reqif_content = zf.read(names[0]).decode("utf-8")

    assert "REQ-IF" in reqif_content


def test_tc_reqif_reqifz_multiple_doc(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_reqifz
    """In multiple document mode each document produces its own .reqifz archive.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_reqifz")

    # Two separate TRLC source files — multiple-document mode (no --single-document).
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--source", "./tests/utils/single_req_with_section.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--reqifz"
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    for doc_name in ("single_req_no_section", "single_req_with_section"):
        # Each document gets its own subfolder and .reqifz in the output folder.
        subfolder = os.path.join(tmp_path, doc_name)
        assert os.path.isdir(subfolder), f"Expected subfolder not found: {subfolder}"
        assert os.path.isfile(os.path.join(subfolder, doc_name + ".reqif"))

        reqifz_file = os.path.join(tmp_path, doc_name + ".reqifz")
        assert os.path.isfile(reqifz_file), f"Expected .reqifz not found: {reqifz_file}"

        with zipfile.ZipFile(reqifz_file, "r") as zf:
            names = zf.namelist()
            assert len(names) == 1
            assert names[0] == doc_name + ".reqif"


def test_tc_reqif_render_plantuml(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_render_plantuml
    """A plantuml fenced code block in a Markdown attribute shall be rendered as an XHTML <object>
    referencing a generated SVG file copied to the output folder.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_render_plantuml")

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_md.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfg.json",
        "reqif",
        "--single-document"
    ])

    # Mock PlantUML so the test does not depend on Java or a PlantUML server being
    # available in the test environment.
    svg_payload = (
        b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>'
    )
    with patch("pyTRLCConverter.marko.md2reqif_renderer.PlantUML.generate_to_bytes",
               return_value=svg_payload):
        main()

    captured = capsys.readouterr()
    assert captured.err == ""

    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    spec_object = _find_spec_object_by_long_name(bundle, "req_id_md")
    assert spec_object is not None

    description_identifier = _find_attribute_identifier(bundle, "description")
    assert description_identifier is not None

    description_attribute = _find_attribute_by_identifier(spec_object, description_identifier)
    assert description_attribute is not None

    # The XHTML must reference the generated SVG via an <object> element.
    assert 'type="image/svg+xml"' in description_attribute.value
    assert '<object' in description_attribute.value

    # Exactly one SVG file must have been copied to the output folder. Its
    # local name is content-addressed, so we just verify any plantuml_*.svg
    # exists and is referenced from the XHTML.
    svg_files = [name for name in os.listdir(tmp_path)
                 if name.startswith("plantuml_") and name.endswith(".svg")]
    assert len(svg_files) == 1
    assert f'data="{svg_files[0]}"' in description_attribute.value

    # And the file on disk must contain the mocked SVG payload.
    with open(os.path.join(tmp_path, svg_files[0]), "rb") as svg_file:
        assert svg_file.read() == svg_payload


def test_tc_reqif_render_plantuml_error(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_render_plantuml_error
    """If PlantUML is not available, a plantuml fenced code block shall be replaced by a
    [PlantUML error: ...] paragraph instead of failing the conversion.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_render_plantuml_error")

    # Ensure PlantUML is not configured for this test run.
    monkeypatch.delenv("PLANTUML", raising=False)

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_description_md.trlc",
        "--out", str(tmp_path),
        "--renderCfg", "./tests/utils/renderCfg.json",
        "reqif",
        "--single-document"
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    spec_object = _find_spec_object_by_long_name(bundle, "req_id_md")
    assert spec_object is not None

    description_identifier = _find_attribute_identifier(bundle, "description")
    assert description_identifier is not None

    description_attribute = _find_attribute_by_identifier(spec_object, description_identifier)
    assert description_attribute is not None

    # The plantuml block must be replaced by a [PlantUML error: ...] paragraph.
    assert "[PlantUML error:" in description_attribute.value
    # And no SVG file may have been written to the output folder.
    svg_files = [name for name in os.listdir(tmp_path)
                 if name.startswith("plantuml_") and name.endswith(".svg")]
    assert len(svg_files) == 0


def test_tc_reqif_identifier_store_init(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_identifier_store_init
    """On the initial conversion the identifier store file is created with the generated identifiers.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_identifier_store_init")

    id_store_file = os.path.join(tmp_path, "ids.json")

    # The identifier store file does not exist yet (initial conversion).
    assert os.path.exists(id_store_file) is False

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document",
        "--id-store", id_store_file
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    # The identifier store file has been created.
    assert os.path.exists(id_store_file) is True

    with open(id_store_file, "r", encoding="utf-8") as fd:
        data = json.load(fd)

    # It stores the generated spec-object identifier keyed by the record's stable logical key.
    assert "spec-object:Requirements.req_id_1" in data["identifiers"]

    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)
    spec_object = _find_spec_object_by_long_name(bundle, "req_id_1")

    assert spec_object is not None
    # The stored identifier matches the one used in the generated ReqIF output.
    assert data["identifiers"]["spec-object:Requirements.req_id_1"] == spec_object.identifier


def test_tc_reqif_identifier_immutable(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_identifier_immutable
    """The identifiers of the ReqIF Identifiable elements stay immutable across consecutive exports.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_identifier_immutable")

    id_store_file = os.path.join(tmp_path, "ids.json")
    argv = [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/multi_req_with_link.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document",
        "--id-store", id_store_file
    ]
    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)

    # First export generates and stores the identifiers.
    monkeypatch.setattr("sys.argv", argv)
    main()
    assert capsys.readouterr().err == ""
    first_identifiers = _collect_identifiers(_parse_reqif(output_file))

    # Second export reuses the stored identifiers.
    monkeypatch.setattr("sys.argv", argv)
    main()
    assert capsys.readouterr().err == ""
    second_identifiers = _collect_identifiers(_parse_reqif(output_file))

    # Sanity check that the elements under test were actually present.
    assert len(first_identifiers["spec_objects"]) == 2
    assert len(first_identifiers["spec_relations"]) == 2

    # All identifiers of the Identifiable elements remain unchanged.
    assert first_identifiers == second_identifiers


def test_tc_reqif_identifier_store_reuse(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_identifier_store_reuse
    """Stored identifiers are reused for known elements while new elements get new identifiers.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_identifier_store_reuse")

    id_store_file = os.path.join(tmp_path, "ids.json")
    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)

    # First conversion with the base file set (only req_id_1).
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/id_store_base.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document",
        "--id-store", id_store_file
    ])
    main()
    assert capsys.readouterr().err == ""

    base_req_1 = _find_spec_object_by_long_name(_parse_reqif(output_file), "req_id_1")
    assert base_req_1 is not None

    with open(id_store_file, "r", encoding="utf-8") as fd:
        data_base = json.load(fd)
    # The new element is not part of the store yet.
    assert "spec-object:Requirements.req_id_2" not in data_base["identifiers"]

    # Second conversion with the extended file set (req_id_1 and the new req_id_2).
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/id_store_extended.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document",
        "--id-store", id_store_file
    ])
    main()
    assert capsys.readouterr().err == ""

    extended_bundle = _parse_reqif(output_file)
    extended_req_1 = _find_spec_object_by_long_name(extended_bundle, "req_id_1")
    extended_req_2 = _find_spec_object_by_long_name(extended_bundle, "req_id_2")

    # The already known element keeps its identifier.
    assert extended_req_1 is not None
    assert extended_req_1.identifier == base_req_1.identifier

    # The new element gets a new, different identifier.
    assert extended_req_2 is not None
    assert extended_req_2.identifier != base_req_1.identifier

    with open(id_store_file, "r", encoding="utf-8") as fd:
        data_extended = json.load(fd)

    # The new element has been added to the store while the known one is preserved.
    assert data_extended["identifiers"]["spec-object:Requirements.req_id_1"] == base_req_1.identifier
    assert "spec-object:Requirements.req_id_2" in data_extended["identifiers"]
    assert data_extended["identifiers"]["spec-object:Requirements.req_id_2"] == extended_req_2.identifier


def test_tc_reqif_export_map(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_export_map
    """A TRLC attribute configured in the export mapping is excluded from the ReqIF output.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_export_map")

    # Export mapping which excludes the 'index' attribute of the Requirement type.
    export_map_file = os.path.join(tmp_path, "export_map.json")
    with open(export_map_file, "w", encoding="utf-8") as fd:
        json.dump(
            {"exclude": [{"package": ".*", "type": "Requirement", "attribute": "index"}]},
            fd
        )

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/single_req_no_section.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document",
        "--export-map", export_map_file
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)
    spec_object = _find_spec_object_by_long_name(bundle, "req_id_1")
    assert spec_object is not None

    # The non-excluded 'description' attribute is still present.
    description_identifier = _find_attribute_identifier(bundle, "description")
    assert description_identifier is not None
    assert _find_attribute_by_identifier(spec_object, description_identifier) is not None

    # The excluded 'index' attribute is not part of the output at all.
    assert _find_attribute_identifier(bundle, "index") is None

    _assert_reqif_v12_compliance(output_file, tmp_path)

# Main *************************************************************************
