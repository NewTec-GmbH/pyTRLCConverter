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
import os
from pathlib import Path
from lxml import etree
from reqif.parser import ReqIFParser
from pyTRLCConverter.__main__ import main
from pyTRLCConverter.reqif_converter import ReqifConverter

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

def _parse_reqif(file_name: str):
    # lobster-exclude: Utility function for other test code.
    """Parse a ReqIF file and return the bundle.

    Args:
        file_name (str): Path to the ReqIF file.

    Returns:
        ReqIFBundle: The parsed ReqIF bundle.
    """
    parser = ReqIFParser()
    return parser.parse(file_name)


def _find_spec_object_by_long_name(bundle, long_name: str):
    # lobster-exclude: Utility function for other test code.
    """Find a spec-object in the bundle by its long-name.

    Args:
        bundle: The parsed ReqIF bundle.
        long_name (str): The long-name to search for.

    Returns:
        ReqIFSpecObject: The matching spec-object, or None if not found.
    """
    assert bundle.core_content is not None
    assert bundle.core_content.req_if_content is not None
    assert bundle.core_content.req_if_content.spec_objects is not None

    for spec_object in bundle.core_content.req_if_content.spec_objects:
        if spec_object.long_name == long_name:
            return spec_object

    return None


def _find_attribute_by_identifier(spec_object, identifier: str):
    # lobster-exclude: Utility function for other test code.
    """Find an attribute on a spec-object by its definition reference identifier.

    Args:
        spec_object: The spec-object to search.
        identifier (str): The attribute definition identifier to look for.

    Returns:
        SpecObjectAttribute: The matching attribute, or None if not found.
    """
    for attribute in spec_object.attributes:
        if attribute.definition_ref == identifier:
            return attribute
    return None


def _find_attribute_identifier(bundle, long_name: str):
    # lobster-exclude: Utility function for other test code.
    """Find the identifier of an attribute definition by its long-name.

    Args:
        bundle: The parsed ReqIF bundle.
        long_name (str): The long-name of the attribute definition to find.

    Returns:
        str: The attribute definition identifier, or None if not found.
    """
    assert bundle.core_content is not None
    assert bundle.core_content.req_if_content is not None
    assert bundle.core_content.req_if_content.spec_types is not None

    for spec_type in bundle.core_content.req_if_content.spec_types:
        if hasattr(spec_type, "attribute_definitions"):
            attribute_definitions = spec_type.attribute_definitions
            if attribute_definitions is None:
                continue
            for definition in attribute_definitions:
                if definition.long_name == long_name:
                    return definition.identifier

    return None


def _find_any_attribute_identifier(bundle, long_names: list[str]):
    # lobster-exclude: Utility function for other test code.
    """Find the first matching attribute definition identifier from a list of long-names.

    Args:
        bundle: The parsed ReqIF bundle.
        long_names (list[str]): Candidate attribute long-names in priority order.

    Returns:
        str: The first matching attribute definition identifier, or None if not found.
    """
    for long_name in long_names:
        identifier = _find_attribute_identifier(bundle, long_name)
        if identifier is not None:
            return identifier

    return None


def _find_spec_type_by_long_name(bundle, long_name: str):
    # lobster-exclude: Utility function for other test code.
    """Find a spec-type in the bundle by its long-name.

    Args:
        bundle: The parsed ReqIF bundle.
        long_name (str): The long-name of the spec-type to find.

    Returns:
        ReqIFSpecType: The matching spec-type, or None if not found.
    """
    assert bundle.core_content is not None
    assert bundle.core_content.req_if_content is not None
    assert bundle.core_content.req_if_content.spec_types is not None

    for spec_type in bundle.core_content.req_if_content.spec_types:
        if spec_type.long_name == long_name:
            return spec_type

    return None


def _find_spec_relation_type_by_long_name(bundle, long_name: str):
    # lobster-exclude: Utility function for other test code.
    """Find a spec-relation type in the bundle by its long-name.

    Args:
        bundle: The parsed ReqIF bundle.
        long_name (str): The long-name of the spec-relation type to find.

    Returns:
        ReqIFSpecRelationType: The matching spec-relation type, or None if not found.
    """
    return _find_spec_type_by_long_name(bundle, long_name)


def _assert_reqif_v12_compliance(reqif_file: str, tmp_path: Path):
    # lobster-exclude: Utility function for other test code.
    """Validate a generated ReqIF file against the ReqIF v1.2 XSD.

    Args:
        reqif_file (str): Path to generated ReqIF file.
        tmp_path (Path): Temporary path used for patched schema material.
    """
    schema_source = Path("./doc/reqif/v1.2/dtc-11-04-05.xsd")
    assert schema_source.exists() is True

    xml_schema_stub = tmp_path / "xml.xsd"
    xml_schema_stub.write_text(
        """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<xsd:schema xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\"
            targetNamespace=\"http://www.w3.org/XML/1998/namespace\"
            xmlns:xml=\"http://www.w3.org/XML/1998/namespace\"
            elementFormDefault=\"qualified\"
            attributeFormDefault=\"qualified\">
  <xsd:attribute name=\"lang\" type=\"xsd:language\"/>
</xsd:schema>
""",
        encoding="utf-8"
    )

    patched_schema_content = schema_source.read_text(encoding="utf-8")
    xml_import = (
        '<xsd:import namespace="http://www.w3.org/XML/1998/namespace" '
        'schemaLocation="http://www.w3.org/2001/xml.xsd"/>'
    )
    xml_schema_path = str(xml_schema_stub).replace("\\", "/")
    xml_import_replacement = (
        '<xsd:import namespace="http://www.w3.org/XML/1998/namespace" '
        f'schemaLocation="{xml_schema_path}"/>'
    )
    patched_schema_content = patched_schema_content.replace(
        xml_import,
        xml_import_replacement
    )
    xhtml_import = (
        '<xsd:import namespace="http://www.w3.org/1999/xhtml" '
        'schemaLocation="http://www.omg.org/spec/ReqIF/20110402/driver.xsd"/>'
    )
    patched_schema_content = patched_schema_content.replace(xhtml_import, "")
    patched_schema_content = patched_schema_content.replace(
        '<xsd:group ref="xhtml.BlkStruct.class"/>',
        '<xsd:sequence><xsd:any minOccurs="0" maxOccurs="unbounded" processContents="lax"/></xsd:sequence>'
    )

    patched_schema_file = tmp_path / "dtc-11-04-05.patched.xsd"
    patched_schema_file.write_text(patched_schema_content, encoding="utf-8")

    schema = etree.XMLSchema(etree.parse(str(patched_schema_file)))  # pylint: disable=c-extension-no-member
    reqif_document = etree.parse(reqif_file)  # pylint: disable=c-extension-no-member

    assert schema.validate(reqif_document) is True, str(schema.error_log)


def test_tc_reqif(record_property, capsys, monkeypatch, tmp_path):
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


def test_tc_reqif_section(record_property, capsys, monkeypatch, tmp_path):
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


def test_tc_reqif_single_doc_custom(record_property, capsys, monkeypatch, tmp_path):
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


def test_tc_reqif_render_md(record_property, capsys, monkeypatch, tmp_path):
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


def test_tc_reqif_render_gfm(record_property, capsys, monkeypatch, tmp_path):
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


def test_tc_reqif_render_xhtml(record_property, capsys, monkeypatch, tmp_path):
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


def test_tc_reqif_render_path(record_property, capsys, monkeypatch, tmp_path):
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


def test_tc_reqif_render_path_reqifz(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_reqif_render_path_reqifz
    """The external file referenced by a path format attribute shall be bundled in the .reqifz archive.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_render_path_reqifz")

    import zipfile  # pylint: disable=import-outside-toplevel

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


# pylint: disable=too-many-locals, too-many-statements
def test_tc_reqif_type_specific_spec_object_types(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_reqif
    # lobster-trace: SwTests.tc_reqif_section
    """The ReqIF converter shall emit one spec-object type per TRLC record type (no Section type).

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif")
    record_property("lobster-trace", "SwTests.tc_reqif_section")

    # mock_type_nested_sections.trlc has all sections before any record, so warnings are expected
    # for "System" and "Functional". "Non-Functional" follows sw_req_1 and uses it as reference.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req_mixed_types.rsl",
        "--source", "./tests/utils/multi_type_nested_sections.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document"
    ])

    # Expect the program to run without any exceptions.
    main()

    # Capture stdout and stderr.
    captured = capsys.readouterr()
    # "System" is the very first section without a preceding record; it becomes the
    # specification title silently. "Functional" is the second such section and warns.
    assert "Warning: Section 'System'" not in captured.err
    assert "Warning: Section 'Functional'" in captured.err

    # Parse the output file for type and hierarchy assertions.
    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    # No Section SPEC-OBJECT-TYPE; only TRLC record types produce types.
    section_type = _find_spec_type_by_long_name(bundle, "Section")
    sw_req_type = _find_spec_type_by_long_name(bundle, "SwReq")
    sw_req_non_func_type = _find_spec_type_by_long_name(bundle, "SwReqNonFunc")

    assert section_type is None
    assert sw_req_type is not None
    assert sw_req_non_func_type is not None

    # Verify that type-specific schemas only contain their own field definitions.
    sw_req_attributes = getattr(sw_req_type, "attribute_definitions", [])
    sw_req_non_func_attributes = getattr(sw_req_non_func_type, "attribute_definitions", [])

    sw_req_attribute_names = {definition.long_name for definition in sw_req_attributes}
    sw_req_non_func_attribute_names = {definition.long_name for definition in sw_req_non_func_attributes}

    assert "description" in sw_req_attribute_names
    assert "verification" in sw_req_attribute_names
    assert len(sw_req_attribute_names) == 3
    assert "ReqIF.ForeignID" in sw_req_attribute_names

    assert "constraint" in sw_req_non_func_attribute_names
    assert "rationale" in sw_req_non_func_attribute_names
    assert len(sw_req_non_func_attribute_names) == 3
    assert "ReqIF.ForeignID" in sw_req_non_func_attribute_names

    # Only records produce SPEC-OBJECTs; section names must not appear.
    functional_record = _find_spec_object_by_long_name(bundle, "sw_req_1")
    non_functional_record = _find_spec_object_by_long_name(bundle, "sw_req_nf_1")

    assert _find_spec_object_by_long_name(bundle, "System") is None
    assert _find_spec_object_by_long_name(bundle, "Functional") is None
    assert _find_spec_object_by_long_name(bundle, "Non-Functional") is None
    assert functional_record is not None
    assert non_functional_record is not None

    assert functional_record.spec_object_type == sw_req_type.identifier
    assert non_functional_record.spec_object_type == sw_req_non_func_type.identifier

    # "Non-Functional" section follows sw_req_1 in document order, so its hierarchy node
    # references sw_req_1's spec-object. sw_req_nf_1 is nested inside it.
    specification = bundle.core_content.req_if_content.specifications[0]
    assert specification.children is not None
    # "System" was the first section without a preceding record; it becomes the spec title.
    assert specification.long_name == "System"

    non_functional_hierarchy = next(
        (h for h in specification.children if h.long_name == "Non-Functional"), None
    )
    assert non_functional_hierarchy is not None
    assert non_functional_hierarchy.spec_object == functional_record.identifier
    assert non_functional_hierarchy.children is not None
    assert non_functional_hierarchy.children[0].long_name == "sw_req_nf_1"


def test_tc_reqif_record_reference_relation(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_reqif_relation
    """The ReqIF converter shall emit record references as ReqIF spec-relations.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_relation")

    # Mock program arguments to convert records that reference each other.
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req.rsl",
        "--source", "./tests/utils/multi_req_with_link.trlc",
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

    # Parse the output file and verify that the link field became a ReqIF relation type.
    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    requirement_type = _find_spec_type_by_long_name(bundle, "Requirement")
    link_relation_type = _find_spec_relation_type_by_long_name(bundle, "link")

    assert requirement_type is not None
    assert link_relation_type is not None

    requirement_attribute_names = {
        definition.long_name
        for definition in getattr(requirement_type, "attribute_definitions", [])
    }
    assert "ReqIF.ForeignID" in requirement_attribute_names
    assert "link" not in requirement_attribute_names

    req_5 = _find_spec_object_by_long_name(bundle, "req_id_5")
    req_6 = _find_spec_object_by_long_name(bundle, "req_id_6")

    assert req_5 is not None
    assert req_6 is not None

    id_identifier = _find_any_attribute_identifier(bundle, ["ReqIF.ForeignID", "ID", "External ID"])
    assert id_identifier is not None

    req_5_id_attribute = _find_attribute_by_identifier(req_5, id_identifier)
    req_6_id_attribute = _find_attribute_by_identifier(req_6, id_identifier)

    assert req_5_id_attribute is not None
    assert req_6_id_attribute is not None
    assert req_5_id_attribute.value == "req_id_5"
    assert req_6_id_attribute.value == "req_id_6"

    assert bundle.core_content is not None
    assert bundle.core_content.req_if_content is not None
    assert bundle.core_content.req_if_content.spec_relations is not None

    relations = bundle.core_content.req_if_content.spec_relations
    assert len(relations) == 2

    relation_pairs = {
        (relation.source, relation.target, relation.relation_type_ref)
        for relation in relations
    }
    expected_relation_pairs = {
        (req_5.identifier, req_6.identifier, link_relation_type.identifier),
        (req_6.identifier, req_5.identifier, link_relation_type.identifier)
    }

    assert relation_pairs == expected_relation_pairs


def test_tc_reqif_record_reference_array_relation(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_reqif_relation
    """The ReqIF converter shall emit one spec-relation per element of a record-reference array.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_relation")

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req_array_refs.rsl",
        "--source", "./tests/utils/array_ref_records.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document"
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    test_case_type = _find_spec_type_by_long_name(bundle, "TestCase")
    verifies_relation_type = _find_spec_relation_type_by_long_name(bundle, "verifies")

    assert test_case_type is not None
    assert verifies_relation_type is not None

    test_case_attribute_names = {
        definition.long_name
        for definition in getattr(test_case_type, "attribute_definitions", [])
    }
    assert "description" in test_case_attribute_names
    assert len(test_case_attribute_names) == 2
    assert "ReqIF.ForeignID" in test_case_attribute_names

    tc_array = _find_spec_object_by_long_name(bundle, "tc_array")
    req_a = _find_spec_object_by_long_name(bundle, "req_a")
    req_b = _find_spec_object_by_long_name(bundle, "req_b")

    assert tc_array is not None
    assert req_a is not None
    assert req_b is not None

    assert bundle.core_content is not None
    assert bundle.core_content.req_if_content is not None
    assert bundle.core_content.req_if_content.spec_relations is not None

    relation_pairs = {
        (relation.source, relation.target, relation.relation_type_ref)
        for relation in bundle.core_content.req_if_content.spec_relations
    }

    assert relation_pairs == {
        (tc_array.identifier, req_a.identifier, verifies_relation_type.identifier),
        (tc_array.identifier, req_b.identifier, verifies_relation_type.identifier)
    }

def _find_datatype_by_long_name(bundle, long_name: str):
    # lobster-exclude: Utility function for other test code.
    """Find a datatype definition in the bundle by its long-name.

    Args:
        bundle: The parsed ReqIF bundle.
        long_name (str): The long-name to search for.

    Returns:
        The matching datatype definition, or None if not found.
    """
    assert bundle.core_content is not None
    assert bundle.core_content.req_if_content is not None
    assert bundle.core_content.req_if_content.data_types is not None

    for datatype in bundle.core_content.req_if_content.data_types:
        if datatype.long_name == long_name:
            return datatype

    return None


def test_tc_reqif_enum(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_reqif_enum
    """The ReqIF converter shall convert a TRLC enumeration attribute to DATATYPE-DEFINITION-ENUMERATION.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_enum")

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req_enum.rsl",
        "--source", "./tests/utils/single_req_with_enum.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document"
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    # Verify the enumeration datatype is present with the correct long-name.
    status_datatype = _find_datatype_by_long_name(bundle, "Status")
    assert status_datatype is not None
    assert status_datatype.values is not None
    assert len(status_datatype.values) == 3

    # Verify ENUM-VALUE keys are 0-based consecutive integers in RSL declaration order.
    expected_literals = [("Draft", "0"), ("Approved", "1"), ("Rejected", "2")]
    for enum_value, (expected_name, expected_key) in zip(status_datatype.values, expected_literals):
        assert enum_value.long_name == expected_name
        assert enum_value.key == expected_key

    # Verify the spec-object has an ATTRIBUTE-VALUE-ENUMERATION referencing the correct ENUM-VALUE.
    spec_object = _find_spec_object_by_long_name(bundle, "req_enum_1")
    assert spec_object is not None

    status_def_identifier = _find_attribute_identifier(bundle, "status")
    assert status_def_identifier is not None

    status_attribute = _find_attribute_by_identifier(spec_object, status_def_identifier)
    assert status_attribute is not None

    # The value must reference the ENUM-VALUE for "Approved" (key=1).
    approved_value = next(v for v in status_datatype.values if v.long_name == "Approved")
    assert approved_value.identifier in status_attribute.value

    # Verify ReqIF XSD compliance.
    _assert_reqif_v12_compliance(output_file, tmp_path)


def test_tc_reqif_enum_null(record_property, capsys, monkeypatch, tmp_path):
    # lobster-trace: SwTests.tc_reqif_enum_null
    """An optional TRLC enumeration attribute with null value shall be omitted from the spec-object.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_enum_null")

    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--source", "./tests/utils/req_enum.rsl",
        "--source", "./tests/utils/single_req_with_enum_null.trlc",
        "--out", str(tmp_path),
        "reqif",
        "--single-document"
    ])

    main()

    captured = capsys.readouterr()
    assert captured.err == ""

    output_file = os.path.join(tmp_path, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)
    bundle = _parse_reqif(output_file)

    spec_object = _find_spec_object_by_long_name(bundle, "req_enum_null_1")
    assert spec_object is not None

    # Verify no ATTRIBUTE-VALUE-ENUMERATION is present for the null status field.
    from reqif.models.reqif_types import SpecObjectAttributeType  # pylint: disable=import-outside-toplevel
    for attribute in spec_object.attributes:
        assert attribute.attribute_type != SpecObjectAttributeType.ENUMERATION

    # Verify ReqIF XSD compliance.
    _assert_reqif_v12_compliance(output_file, tmp_path)


def test_tc_reqif_reqifz(record_property, capsys, monkeypatch, tmp_path):
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

    import zipfile  # pylint: disable=import-outside-toplevel
    with zipfile.ZipFile(reqifz_file, "r") as zf:
        names = zf.namelist()
        assert len(names) == 1
        assert names[0] == doc_name + ".reqif"
        reqif_content = zf.read(names[0]).decode("utf-8")

    assert "REQ-IF" in reqif_content


def test_tc_reqif_reqifz_multiple_doc(record_property, capsys, monkeypatch, tmp_path):
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

    import zipfile  # pylint: disable=import-outside-toplevel
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


# Main *************************************************************************
