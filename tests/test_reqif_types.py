"""Test the ReqIF conversion requirements for types, relations, and enumerations."""

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
from reqif.models.reqif_types import SpecObjectAttributeType
from pyTRLCConverter.__main__ import main
from pyTRLCConverter.reqif_converter import ReqifConverter
from tests.reqif_test_utils import (
    _parse_reqif,
    _find_spec_object_by_long_name,
    _find_attribute_by_identifier,
    _find_attribute_identifier,
    _find_any_attribute_identifier,
    _find_spec_type_by_long_name,
    _find_spec_relation_type_by_long_name,
    _find_datatype_by_long_name,
    _assert_reqif_v12_compliance,
)

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

# pylint: disable=too-many-locals, too-many-statements
def test_tc_reqif_type_specific_spec_object_types(record_property, capsys, monkeypatch, tmp_path: Path):
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


def test_tc_reqif_record_reference_relation(record_property, capsys, monkeypatch, tmp_path: Path):
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


def test_tc_reqif_record_reference_array_relation(record_property, capsys, monkeypatch, tmp_path: Path):
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


def test_tc_reqif_enum(record_property, capsys, monkeypatch, tmp_path: Path):
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


def test_tc_reqif_enum_null(record_property, capsys, monkeypatch, tmp_path: Path):
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
    for attribute in spec_object.attributes:
        assert attribute.attribute_type != SpecObjectAttributeType.ENUMERATION

    # Verify ReqIF XSD compliance.
    _assert_reqif_v12_compliance(output_file, tmp_path)

# Main *************************************************************************
