"""Shared helper utilities for the ReqIF converter test suite."""

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
from pathlib import Path
from lxml import etree
from reqif.parser import ReqIFParser

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

# Main *************************************************************************
