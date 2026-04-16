"""Validate a .reqif or .reqifz file against the ReqIF v1.2 XSD schema.

Validation covers:
  1. Document structure — validated against the ReqIF v1.2 XSD (dtc-11-04-05.xsd).
  2. XHTML content — every ATTRIBUTE-VALUE-XHTML THE-VALUE element is checked for:
       - Root element is <div> in the XHTML namespace.
       - No bare text directly inside the root <div>.
       - All descendant elements use only allowed XHTML 1.0 Strict element names
         within the XHTML namespace.
  3. ReqIF Implementation Guideline (IG) rules not enforced by the XSD:
       - IG-001: REQ-IF-VERSION must be exactly "1.0" or "1.2".
       - IG-003: CREATION-TIME and every LAST-CHANGE must carry a UTC offset (e.g. +00:00).
       - IG-009: ATTRIBUTE-VALUE-STRING THE-VALUE must not be an empty string.
       - IG-010: ENUM-VALUE KEY integers must be unique within each
                 DATATYPE-DEFINITION-ENUMERATION.

Usage:
    python validate_reqif.py <file.reqif|file.reqifz>

Exit codes:
    0 - file is valid
    1 - file is invalid or an error occurred
"""

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
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from lxml import etree

# Variables ********************************************************************

_SCHEMA_PATH = Path(__file__).parent / "../../../doc/reqif/v1.2/dtc-11-04-05.xsd"

_REQIF_NS = "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"
_XHTML_NS = "http://www.w3.org/1999/xhtml"

# Allowed XHTML 1.0 Strict element local names (block + inline).
_XHTML_ALLOWED_ELEMENTS = frozenset([
    # Block
    "div", "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "dl", "dt", "dd",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td",
    "blockquote", "pre", "hr", "address",
    # Inline
    "a", "abbr", "acronym", "b", "bdo", "big", "br",
    "cite", "code", "dfn", "em", "i", "img", "kbd",
    "q", "samp", "small", "span", "strong", "sub", "sup",
    "tt", "var",
])

_XML_NAMESPACE_STUB = """\
<?xml version="1.0" encoding="UTF-8"?>
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            targetNamespace="http://www.w3.org/XML/1998/namespace"
            xmlns:xml="http://www.w3.org/XML/1998/namespace"
            elementFormDefault="qualified"
            attributeFormDefault="qualified">
  <xsd:attribute name="lang" type="xsd:language"/>
</xsd:schema>
"""

_XML_IMPORT_ORIGINAL = (
    '<xsd:import namespace="http://www.w3.org/XML/1998/namespace" '
    'schemaLocation="http://www.w3.org/2001/xml.xsd"/>'
)

_XHTML_IMPORT = (
    '<xsd:import namespace="http://www.w3.org/1999/xhtml" '
    'schemaLocation="http://www.omg.org/spec/ReqIF/20110402/driver.xsd"/>'
)

_XHTML_BLOCK_STRUCT = '<xsd:group ref="xhtml.BlkStruct.class"/>'

_XHTML_BLOCK_STRUCT_REPLACEMENT = (
    '<xsd:sequence>'
    '<xsd:any minOccurs="0" maxOccurs="unbounded" processContents="lax"/>'
    '</xsd:sequence>'
)

# Matches ISO 8601 datetimes that carry a timezone offset: Z or ±HH:MM at the end.
_TZ_PATTERN = re.compile(r"(Z|[+-]\d{2}:\d{2})$")

_UNKNOWN = "<unknown>"

# Classes **********************************************************************

# Functions ********************************************************************


def _read_reqif_content(file_path: Path) -> tuple[str, str]:
    """Read the ReqIF XML content from a .reqif or .reqifz file.

    For .reqifz files the first .reqif entry inside the ZIP archive is extracted.

    Args:
        file_path (Path): Path to the input file.

    Returns:
        tuple[str, str]: A tuple of (xml_content, source_description) where
            source_description is a human-readable label for error messages.
    """
    suffix = file_path.suffix.lower()
    xml_content = ""
    source_description = str(file_path)

    if suffix == ".reqifz":
        with zipfile.ZipFile(file_path, "r") as zf:
            reqif_names = [n for n in zf.namelist() if n.lower().endswith(".reqif")]
            if not reqif_names:
                raise ValueError(f"No .reqif entry found inside {file_path}")
            source_description = f"{file_path}!{reqif_names[0]}"
            xml_content = zf.read(reqif_names[0]).decode("utf-8")
    else:
        xml_content = file_path.read_text(encoding="utf-8")

    return xml_content, source_description


def _build_patched_schema(tmp_dir: Path) -> etree.XMLSchema:
    """Build a patched lxml XMLSchema that resolves offline imports.

    The ReqIF XSD imports two external schemas that are not available offline:
    - http://www.w3.org/2001/xml.xsd  → replaced with a minimal local stub.
    - http://www.omg.org/spec/ReqIF/20110402/driver.xsd (XHTML) → removed;
      the xhtml.BlkStruct.class group reference is replaced with a lax wildcard.

    Args:
        tmp_dir (Path): Temporary directory for generated stub and patched XSD files.

    Returns:
        etree.XMLSchema: The compiled schema ready for validation.
    """
    xml_stub_path = tmp_dir / "xml.xsd"
    xml_stub_path.write_text(_XML_NAMESPACE_STUB, encoding="utf-8")

    xml_import_replacement = (
        '<xsd:import namespace="http://www.w3.org/XML/1998/namespace" '
        f'schemaLocation="{xml_stub_path.as_posix()}"/>'
    )

    schema_content = _SCHEMA_PATH.resolve().read_text(encoding="utf-8")
    schema_content = schema_content.replace(_XML_IMPORT_ORIGINAL, xml_import_replacement)
    schema_content = schema_content.replace(_XHTML_IMPORT, "")
    schema_content = schema_content.replace(_XHTML_BLOCK_STRUCT, _XHTML_BLOCK_STRUCT_REPLACEMENT)

    patched_path = tmp_dir / "dtc-11-04-05.patched.xsd"
    patched_path.write_text(schema_content, encoding="utf-8")

    return etree.XMLSchema(etree.parse(str(patched_path)))  # pylint: disable=c-extension-no-member


def _check_element_namespace(tag: str, location: str) -> str:
    """Check whether a single element tag is in the XHTML namespace and is an allowed element.

    Args:
        tag (str): Clark-notation element tag (e.g. ``{ns}local``).
        location (str): Human-readable location label for error messages.

    Returns:
        str: An error message string, or an empty string if the element is valid.
    """
    xhtml_prefix = f"{{{_XHTML_NS}}}"
    if tag.startswith(xhtml_prefix):
        local_name = tag[len(xhtml_prefix):]
        if local_name not in _XHTML_ALLOWED_ELEMENTS:
            return f"{location}: <{local_name}> is not an allowed XHTML 1.0 Strict element"
    else:
        return f"{location}: element <{tag}> is not in the XHTML namespace '{_XHTML_NS}'"

    return ""


def _check_bare_text(div_element: etree._Element, location: str) -> list[str]:  # pylint: disable=c-extension-no-member
    """Check that no bare text appears directly inside a <div> element.

    Bare text is text content that is not wrapped in a child block element.
    Both ``div.text`` (text before the first child) and ``child.tail`` (text
    after a child element but still inside the div) are checked.

    Args:
        div_element (etree._Element): The root ``<div>`` element to inspect.
        location (str): Human-readable location label for error messages.

    Returns:
        list[str]: List of error message strings (empty means no bare text).
    """
    errors = []

    if div_element.text and div_element.text.strip():
        errors.append(f"{location}: bare text directly inside <div> (wrap in a block element such as <p>)")

    for child in div_element:
        if child.tail and child.tail.strip():
            errors.append(f"{location}: bare text after <{child.tag}> inside <div> (wrap in a block element)")

    return errors


def _check_descendant_tags(div_element: etree._Element, expected_tag: str, location: str) -> list[str]:  # pylint: disable=c-extension-no-member
    """Check that every descendant element uses an allowed XHTML 1.0 Strict tag.

    Args:
        div_element (etree._Element): The root ``<div>`` element whose descendants are checked.
        expected_tag (str): Clark-notation tag of the root div (skipped during iteration).
        location (str): Human-readable location label for error messages.

    Returns:
        list[str]: List of error message strings (empty means all tags are valid).
    """
    errors = []

    for element in div_element.iter():
        tag = element.tag
        if not isinstance(tag, str) or tag == expected_tag:
            continue
        error = _check_element_namespace(tag, location)
        if error:
            errors.append(error)

    return errors


def _validate_xhtml_element(div_element: etree._Element, location: str) -> list[str]:  # pylint: disable=c-extension-no-member
    """Validate one XHTML root element from an ATTRIBUTE-VALUE-XHTML THE-VALUE.

    Checks performed:
    - Root element is <div> in the XHTML namespace.
    - No bare text directly inside the root <div>.
    - All descendant elements are in the XHTML namespace and use only
      allowed XHTML 1.0 Strict element names.

    Args:
        div_element (etree._Element): The first child of a THE-VALUE element.
        location (str): Human-readable location label for error messages.

    Returns:
        list[str]: List of error message strings (empty means valid).
    """
    errors = []
    expected_tag = f"{{{_XHTML_NS}}}div"

    if div_element.tag != expected_tag:
        errors.append(
            f"{location}: THE-VALUE root must be <div xmlns='{_XHTML_NS}'>, "
            f"got <{div_element.tag}>"
        )
    else:
        errors.extend(_check_bare_text(div_element, location))
        errors.extend(_check_descendant_tags(div_element, expected_tag, location))

    return errors


def _validate_xhtml_content(document: etree._Element) -> list[str]:  # pylint: disable=c-extension-no-member
    """Find and validate all ATTRIBUTE-VALUE-XHTML THE-VALUE elements in the document.

    Args:
        document (etree._Element): The root element of the parsed ReqIF document.

    Returns:
        list[str]: List of error message strings (empty means all XHTML values are valid).
    """
    errors = []
    spec_object_tag = f"{{{_REQIF_NS}}}SPEC-OBJECT"
    av_xhtml_tag = f"{{{_REQIF_NS}}}ATTRIBUTE-VALUE-XHTML"
    the_value_tag = f"{{{_REQIF_NS}}}THE-VALUE"

    for spec_obj in document.iter(spec_object_tag):
        long_name = spec_obj.get("LONG-NAME", _UNKNOWN)
        for av_xhtml in spec_obj.iter(av_xhtml_tag):
            def_ref = av_xhtml.get("definition_ref", "")
            location = f"SPEC-OBJECT '{long_name}'" + (f" attr '{def_ref}'" if def_ref else "")
            for the_value in av_xhtml.findall(the_value_tag):
                children = list(the_value)
                if not children:
                    errors.append(f"{location}: THE-VALUE is empty (expected <div> child)")
                    continue
                errors.extend(_validate_xhtml_element(children[0], location))

    return errors


def _validate_ig001_version(document: etree._Element) -> list[str]:  # pylint: disable=c-extension-no-member
    """Check that REQ-IF-VERSION is exactly '1.0' or '1.2' (IG-001).

    Args:
        document (etree._Element): The root element of the parsed ReqIF document.

    Returns:
        list[str]: List of error message strings (empty means valid).
    """
    errors = []
    version_tag = f"{{{_REQIF_NS}}}REQ-IF-VERSION"

    for version_el in document.iter(version_tag):
        version_text = (version_el.text or "").strip()
        if version_text not in ("1.0", "1.2"):
            errors.append(f"IG-001: REQ-IF-VERSION must be '1.0' or '1.2', got '{version_text}'")

    return errors


def _validate_ig003_timestamps(document: etree._Element) -> list[str]:  # pylint: disable=c-extension-no-member
    """Check that CREATION-TIME and every LAST-CHANGE carry a UTC offset (IG-003).

    An ISO 8601 datetime without a timezone offset (e.g. 2026-01-01T00:00:00) is
    rejected; the value must end with Z or ±HH:MM (e.g. 2026-01-01T00:00:00+00:00).

    Args:
        document (etree._Element): The root element of the parsed ReqIF document.

    Returns:
        list[str]: List of error message strings (empty means valid).
    """
    errors = []
    creation_time_tag = f"{{{_REQIF_NS}}}CREATION-TIME"

    for el in document.iter(creation_time_tag):
        text = (el.text or "").strip()
        if text and not _TZ_PATTERN.search(text):
            errors.append(f"IG-003: CREATION-TIME '{text}' has no UTC offset (use e.g. +00:00 or Z)")

    for el in document.iter():
        last_change = el.get("LAST-CHANGE")
        if last_change and not _TZ_PATTERN.search(last_change):
            identifier = el.get("IDENTIFIER", el.tag)
            errors.append(
                f"IG-003: LAST-CHANGE '{last_change}' on '{identifier}' has no UTC offset"
            )

    return errors


def _validate_ig009_empty_strings(document: etree._Element) -> list[str]:  # pylint: disable=c-extension-no-member
    """Check that no ATTRIBUTE-VALUE-STRING carries an empty THE-VALUE (IG-009).

    The IG requires that empty attribute values are omitted rather than emitted
    as empty strings.

    Args:
        document (etree._Element): The root element of the parsed ReqIF document.

    Returns:
        list[str]: List of error message strings (empty means valid).
    """
    errors = []
    av_string_tag = f"{{{_REQIF_NS}}}ATTRIBUTE-VALUE-STRING"
    spec_object_tag = f"{{{_REQIF_NS}}}SPEC-OBJECT"

    for el in document.iter(av_string_tag):
        if el.get("THE-VALUE") != "":
            continue
        parent = el.getparent()
        while parent is not None and parent.tag != spec_object_tag:
            parent = parent.getparent()
        obj_name = parent.get("LONG-NAME", _UNKNOWN) if parent is not None else _UNKNOWN
        errors.append(
            f"IG-009: ATTRIBUTE-VALUE-STRING with empty THE-VALUE in SPEC-OBJECT '{obj_name}' "
            f"(omit the attribute instead)"
        )

    return errors


def _validate_ig010_enum_keys(document: etree._Element) -> list[str]:  # pylint: disable=c-extension-no-member
    """Check that ENUM-VALUE KEY integers are unique within each DATATYPE-DEFINITION-ENUMERATION (IG-010).

    Args:
        document (etree._Element): The root element of the parsed ReqIF document.

    Returns:
        list[str]: List of error message strings (empty means valid).
    """
    errors = []
    datatype_tag = f"{{{_REQIF_NS}}}DATATYPE-DEFINITION-ENUMERATION"
    enum_value_tag = f"{{{_REQIF_NS}}}ENUM-VALUE"
    embedded_value_tag = f"{{{_REQIF_NS}}}EMBEDDED-VALUE"

    for datatype in document.iter(datatype_tag):
        long_name = datatype.get("LONG-NAME", _UNKNOWN)
        seen_keys: set[str] = set()
        for enum_value in datatype.iter(enum_value_tag):
            for embedded in enum_value.iter(embedded_value_tag):
                key = embedded.get("KEY")
                if key is None:
                    continue
                if key in seen_keys:
                    errors.append(
                        f"IG-010: duplicate ENUM-VALUE KEY '{key}' "
                        f"in DATATYPE-DEFINITION-ENUMERATION '{long_name}'"
                    )
                else:
                    seen_keys.add(key)

    return errors


def _validate_ig_rules(document: etree._Element) -> list[str]:  # pylint: disable=c-extension-no-member
    """Run all ReqIF Implementation Guideline checks that the XSD cannot enforce.

    Checks performed:
    - IG-001: REQ-IF-VERSION is "1.0" or "1.2"
    - IG-003: CREATION-TIME and LAST-CHANGE carry a UTC offset
    - IG-009: ATTRIBUTE-VALUE-STRING THE-VALUE is not an empty string
    - IG-010: ENUM-VALUE KEY integers are unique per DATATYPE-DEFINITION-ENUMERATION

    Args:
        document (etree._Element): The root element of the parsed ReqIF document.

    Returns:
        list[str]: Combined list of all IG error messages (empty means all rules pass).
    """
    errors = []
    errors.extend(_validate_ig001_version(document))
    errors.extend(_validate_ig003_timestamps(document))
    errors.extend(_validate_ig009_empty_strings(document))
    errors.extend(_validate_ig010_enum_keys(document))
    return errors


def _run_content_checks(document: etree._Element, source_description: str) -> bool:  # pylint: disable=c-extension-no-member
    """Run XHTML and IG checks on a schema-valid ReqIF document.

    Both checks always run so all errors are reported in one pass.
    Results are printed to stdout (VALID) or stderr (INVALID).

    Args:
        document (etree._Element): The root element of a schema-valid ReqIF document.
        source_description (str): Human-readable label used in printed messages.

    Returns:
        bool: True if both XHTML and IG checks pass, False otherwise.
    """
    xhtml_errors = _validate_xhtml_content(document)
    ig_errors = _validate_ig_rules(document)
    is_valid = not xhtml_errors and not ig_errors

    if xhtml_errors:
        print(f"INVALID (xhtml): {source_description}", file=sys.stderr)
        for error in xhtml_errors:
            print(f"  {error}", file=sys.stderr)

    if ig_errors:
        print(f"INVALID (ig): {source_description}", file=sys.stderr)
        for error in ig_errors:
            print(f"  {error}", file=sys.stderr)

    if is_valid:
        print(f"VALID: {source_description}")

    return is_valid


def validate(input_path: Path) -> bool:
    """Validate a .reqif or .reqifz file against the ReqIF v1.2 XSD, XHTML rules, and IG rules.

    Validation results are printed to stdout. Errors are printed to stderr.
    Schema errors stop further checks. XHTML and IG checks both run when schema passes.

    Args:
        input_path (Path): Path to the .reqif or .reqifz file to validate.

    Returns:
        bool: True if the file is valid, False otherwise.
    """
    if not input_path.exists():
        print(f"ERROR: file not found: {input_path}", file=sys.stderr)
        return False

    schema_resolved = _SCHEMA_PATH.resolve()
    if not schema_resolved.exists():
        print(f"ERROR: ReqIF XSD schema not found at {schema_resolved}", file=sys.stderr)
        return False

    is_valid = False

    try:
        xml_content, source_description = _read_reqif_content(input_path)

        with tempfile.TemporaryDirectory() as tmp_dir:
            schema = _build_patched_schema(Path(tmp_dir))
            document = etree.fromstring(xml_content.encode("utf-8"))  # pylint: disable=c-extension-no-member
            is_valid = schema.validate(document)

            if not is_valid:
                print(f"INVALID (schema): {source_description}", file=sys.stderr)
                for error in schema.error_log:
                    print(f"  line {error.line}: {error.message}", file=sys.stderr)
            else:
                is_valid = _run_content_checks(document, source_description)

    except (OSError, ValueError, zipfile.BadZipFile, etree.XMLSyntaxError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        is_valid = False

    return is_valid


# Main *************************************************************************

def main() -> None:
    """Entry point for the validate_reqif script.

    Reads the input file path from the command line, runs validation, and exits
    with code 0 on success or 1 on failure.
    """
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(__file__).name} <file.reqif|file.reqifz>", file=sys.stderr)
        sys.exit(1)

    result = validate(Path(sys.argv[1]))
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
