"""Analyse a .reqif or .reqifz file and generate TRLC source files.

Reads a ReqIF file compliant with the ProSTEP ReqIF Implementation Guideline
and produces four files ready for use with pyTRLCConverter:

- <package>.rsl        TRLC type definitions (one ``type`` per SPEC-OBJECT-TYPE)
- <package>.trlc       TRLC requirement instances, following the SPEC-HIERARCHY
- renderCfg.json       Marks XHTML-typed attributes as ``gfm`` format
- translation.json     Maps sanitised TRLC attribute names back to their ReqIF LONG-NAMEs

Round-trip fidelity
-------------------
The generated TRLC files are intended so that a subsequent::

    pyTRLCConverter --source <dir> --renderCfg renderCfg.json \\
                    --translation translation.json reqif

run reproduces THE-VALUE content identical (or as close as possible) to the
analysed source.  The following constraints apply:

* XHTML-typed attributes are converted to GitHub Flavored Markdown.  Marko
  (used by pyTRLCConverter) re-renders the Markdown to XHTML.  Simple content
  (paragraphs, bold, italic, code, lists, links) round-trips cleanly.
  Complex XHTML (deeply nested tables, custom attributes) is approximated.
* Non-XHTML attributes (STRING, INTEGER, BOOLEAN, DATE) are stored as plain
  TRLC ``String`` values.  pyTRLCConverter wraps them in ``<p>…</p>``; the
  original attribute was a plain value, so the attribute type differs in the
  round-trip output, but the text content is preserved.
* SPEC-RELATIONs (record-to-record links) are not yet reverse-engineered to
  TRLC record references.  They are silently omitted.
* ENUMERATION datatypes become TRLC ``enum`` types in the RSL.  Attributes
  referencing an enumeration type are declared with the TRLC enum type and
  multi-valued enumerations use the ``[0 .. *]`` array syntax.  Attribute
  values in the TRLC file use the qualified enum-literal form
  ``<package>.<EnumType>.<literal>``.
"""

# MIT License
#
# Copyright (c) 2026 NewTec GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Imports **********************************************************************
import argparse
import html
import json
import os
import re
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from typing import Any, Optional

# pylint: disable=too-many-lines

# Variables ********************************************************************

_TRLC_KEYWORDS: frozenset[str] = frozenset({
    "abs", "abstract", "and", "checks", "else", "elsif", "enum", "error",
    "exists", "extends", "false", "fatal", "final", "forall", "freeze", "if",
    "implies", "import", "in", "not", "null", "optional", "or", "package",
    "section", "separator", "then", "true", "tuple", "type", "warning", "xor",
})

_REQIF_FOREIGN_ID_LONG_NAME: str = "ReqIF.ForeignID"

# Attribute LONG-NAMEs managed automatically by pyTRLCConverter — omit from RSL/TRLC.
# ReqIF.ForeignID is set from the TRLC record object name; including it would create
# a duplicate attribute definition in the round-trip output.
_SKIP_LONG_NAMES: frozenset[str] = frozenset({_REQIF_FOREIGN_ID_LONG_NAME})

# XHTML namespace URI as it appears in attribute values
_XHTML_NS: str = "http://www.w3.org/1999/xhtml"


# Classes **********************************************************************


class _WritingContext:  # pylint: disable=too-few-public-methods
    """Groups the read-only lookup structures passed to every TRLC writing function.

    Bundling these dicts into one object keeps the writing functions within
    pylint's argument-count limit without losing any information.
    """

    def __init__(self, type_info: dict[str, Any], attr_def_map: dict[str, Any],  # pylint: disable=too-many-arguments,too-many-positional-arguments
                 datatype_map: dict[str, Any], spec_object_map: dict[str, Any],
                 enum_info: dict[str, Any], package_name: str) -> None:
        """Initialise the writing context.

        Args:
            type_info:       Type metadata dict (see _collect_type_info).
            attr_def_map:    Attr-def identifier → SpecAttributeDefinition.
            datatype_map:    Datatype identifier → datatype object.
            spec_object_map: Spec-object identifier → ReqIFSpecObject.
            enum_info:       Enum metadata dict (see _collect_enum_info).
            package_name:    TRLC package name used for qualified enum-literal references.
        """
        self.type_info = type_info
        self.attr_def_map = attr_def_map
        self.datatype_map = datatype_map
        self.spec_object_map = spec_object_map
        self.enum_info = enum_info
        self.package_name = package_name


# Functions ********************************************************************


def _get_reqif_module() -> tuple[type, type]:
    """Import the reqif parser and SpecObjectAttributeType; exit with a helpful message if missing.

    Returns:
        Tuple of (ReqIFParser class, SpecObjectAttributeType enum).
    """
    try:
        from reqif.parser import ReqIFParser  # pylint: disable=import-outside-toplevel
        from reqif.models.reqif_types import SpecObjectAttributeType  # pylint: disable=import-outside-toplevel
        return ReqIFParser, SpecObjectAttributeType
    except ImportError:
        print("ERROR: 'reqif' package not found.  Install it with:  pip install reqif",
              file=sys.stderr)
        sys.exit(1)


def _resolve_reqif_path(reqif_path: str, tmpdir: str) -> list[str]:
    """Return .reqif file paths to process, extracting .reqifz archives first.

    Args:
        reqif_path: Path to a .reqif or .reqifz file.
        tmpdir:     Temporary directory used when extracting .reqifz archives.

    Returns:
        Sorted list of absolute .reqif file paths.
    """
    if os.path.splitext(reqif_path)[1].lower() == ".reqifz":
        with zipfile.ZipFile(reqif_path, "r") as zf:
            zf.extractall(tmpdir)
        paths = sorted(
            os.path.join(tmpdir, n)
            for n in os.listdir(tmpdir)
            if n.lower().endswith(".reqif")
        )
        if not paths:
            print("ERROR: No .reqif file found inside the .reqifz archive.", file=sys.stderr)
            sys.exit(1)
        return paths
    return [reqif_path]


def _parse_bundle(reqif_path: str) -> Any:
    """Parse the ReqIF file and return the bundle.  Handles .reqifz archives transparently.

    Args:
        reqif_path: Path to a .reqif or .reqifz file.

    Returns:
        A ReqIFBundle object produced by ReqIFParser.parse().
    """
    reqif_parser = _get_reqif_module()[0]
    with tempfile.TemporaryDirectory() as tmpdir:
        reqif_files = _resolve_reqif_path(reqif_path, tmpdir)
        actual_path = reqif_files[0]
        if len(reqif_files) > 1:
            print(f"INFO: Archive contains {len(reqif_files)} .reqif files; "
                  f"using: {os.path.basename(actual_path)}")
        return reqif_parser.parse(actual_path)


def _collect_enum_info(datatype_map: dict[str, Any]) -> dict[str, Any]:
    """Build metadata for all DATATYPE-DEFINITION-ENUMERATION entries.

    Args:
        datatype_map: Mapping from datatype identifier to datatype object.

    Returns:
        Dict keyed by datatype identifier.  Each value contains:
        ``trlc_name`` (TRLC enum type name), ``long_name`` (original LONG-NAME),
        and ``literals`` (dict mapping value-identifier to
        ``{"trlc_name": str, "long_name": str}``).
    """
    enum_info: dict[str, Any] = {}
    used_enum_names: set[str] = set()

    for dt_id, dt in datatype_map.items():
        values = getattr(dt, "values", None)
        if values is None:
            continue  # Not an enumeration type

        long_name: str = getattr(dt, "long_name", None) or dt_id
        trlc_name = _unique_name(_sanitize_identifier(long_name), used_enum_names)

        literals: dict[str, dict[str, str]] = {}
        used_lit_names: set[str] = set()
        for v in values:
            lit_long_name: str = (
                getattr(v, "long_name", None)
                or str(getattr(v, "key", getattr(v, "identifier", "unknown")))
            )
            trlc_lit_name = _unique_name(_sanitize_identifier(lit_long_name), used_lit_names)
            literals[getattr(v, "identifier", lit_long_name)] = {
                "trlc_name": trlc_lit_name,
                "long_name": lit_long_name,
            }

        enum_info[dt_id] = {
            "trlc_name": trlc_name,
            "long_name": long_name,
            "literals": literals,
        }

    return enum_info


def _build_datatype_map(content: Any) -> dict[str, Any]:
    """Build a mapping from datatype identifier to datatype object.

    Args:
        content: ReqIFReqIFContent from a parsed bundle.

    Returns:
        Dict keyed by identifier string.
    """
    result: dict[str, Any] = {}
    for dt in (getattr(content, "data_types", None) or []):
        ident: str | None = getattr(dt, "identifier", None)
        if ident:
            result[ident] = dt
    return result


def _build_attr_def_map(content: Any) -> dict[str, Any]:
    """Build a mapping from attribute-definition identifier to SpecAttributeDefinition.

    Collects definitions from all spec types (attribute_definitions and spec_attributes).

    Args:
        content: ReqIFReqIFContent from a parsed bundle.

    Returns:
        Dict keyed by attribute-definition identifier string.
    """
    result: dict[str, Any] = {}
    for spec_type in (getattr(content, "spec_types", None) or []):
        attrs = getattr(spec_type, "attribute_definitions", None) \
             or getattr(spec_type, "spec_attributes", None) or []
        for attr_def in attrs:
            ident: str | None = getattr(attr_def, "identifier", None)
            if ident:
                result[ident] = attr_def
    return result


def _build_spec_object_map(content: Any) -> dict[str, Any]:
    """Build a mapping from spec-object identifier to ReqIFSpecObject.

    Args:
        content: ReqIFReqIFContent from a parsed bundle.

    Returns:
        Dict keyed by identifier string.
    """
    result: dict[str, Any] = {}
    for obj in (getattr(content, "spec_objects", None) or []):
        ident: str | None = getattr(obj, "identifier", None)
        if ident:
            result[ident] = obj
    return result


def _sanitize_identifier(name: str) -> str:
    """Convert a ReqIF name to a valid TRLC identifier.

    Replaces any character that is not alphanumeric or underscore with ``_``,
    strips leading digits/underscores, and appends ``_`` when the result is a
    TRLC keyword.

    Args:
        name: Arbitrary name string (e.g. a LONG-NAME or IDENTIFIER).

    Returns:
        Valid TRLC identifier, never empty.
    """
    # Replace invalid chars with underscore, collapse consecutive underscores
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")

    # Must start with a letter
    if cleaned and cleaned[0].isdigit():
        cleaned = "x" + cleaned

    if not cleaned:
        cleaned = "unnamed"

    # Avoid TRLC keywords
    if cleaned in _TRLC_KEYWORDS:
        cleaned = cleaned + "_"

    return cleaned


def _unique_name(base: str, used: set[str]) -> str:
    """Return a name derived from base that is not already in used, then register it.

    Args:
        base: Preferred name.
        used: Set of already-taken names.  The chosen name is added to this set.

    Returns:
        A unique name string.
    """
    candidate = base
    counter = 1
    while candidate in used:
        candidate = f"{base}_{counter}"
        counter += 1
    used.add(candidate)
    return candidate


def _strip_ns(tag: str) -> str:
    """Strip the XML namespace URI (``{...}``) from an element tag.

    Args:
        tag: Element tag string, possibly with a ``{namespace}`` prefix.

    Returns:
        Tag name without namespace.
    """
    return tag.split("}")[-1] if "}" in tag else tag


def _element_to_md(elem: ET.Element, _list_type: str = "") -> str:  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
    """Recursively convert an XML element to GitHub Flavored Markdown text.

    Only the most common XHTML elements produced by ReqIF tools are handled.
    Unknown elements fall back to rendering their text content.

    Args:
        elem:       XML element to convert.
        _list_type: ``"ul"`` or ``"ol"`` when rendering inside a list, empty otherwise.

    Returns:
        Markdown string for the element and all its descendants.
    """
    tag = _strip_ns(elem.tag)
    text = html.escape(elem.text or "", quote=False)
    tail = html.escape(elem.tail or "", quote=False)

    child_content = "".join(_element_to_md(child, _list_type) for child in elem)

    if tag in ("div", "span", "body", "html"):
        result = text + child_content
    elif tag == "p":
        inner = (text + child_content).strip()
        result = inner + "\n\n"
    elif tag in ("strong", "b"):
        result = f"**{text}{child_content}**"
    elif tag in ("em", "i"):
        result = f"*{text}{child_content}*"
    elif tag == "code" and _list_type == "pre":
        result = text + child_content
    elif tag == "code":
        result = f"`{text}{child_content}`"
    elif tag == "pre":
        inner_elem = list(elem)
        if inner_elem and _strip_ns(inner_elem[0].tag) == "code":
            code_text = inner_elem[0].text or ""
            result = f"```\n{code_text}\n```\n\n"
        else:
            result = f"```\n{text}{child_content}\n```\n\n"
    elif tag == "br":
        result = "  \n"
    elif tag == "a":
        href = elem.get("href", "")
        inner = (text + child_content).strip()
        result = f"[{inner}]({href})"
    elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(tag[1])
        inner = (text + child_content).strip()
        result = "#" * level + " " + inner + "\n\n"
    elif tag == "ul":
        items = "".join(_element_to_md(child, "ul") for child in elem)
        result = items + "\n"
    elif tag == "ol":
        parts = []
        for idx, child in enumerate(elem, start=1):
            item_md = _element_to_md(child, "ol")
            # Replace leading "- " (from li handler) with numbered prefix
            item_md = re.sub(r"^- ", f"{idx}. ", item_md)
            parts.append(item_md)
        result = "".join(parts) + "\n"
    elif tag == "li":
        inner = (text + child_content).strip()
        result = f"- {inner}\n"
    elif tag == "table":
        result = _table_to_md(elem)
    elif tag in ("thead", "tbody", "tfoot"):
        result = text + child_content
    else:
        # Unknown element: render its text content
        result = text + child_content

    return result + tail


def _table_to_md(table_elem: ET.Element) -> str:
    """Convert an XHTML table element to a GFM pipe table.

    Args:
        table_elem: The ``<table>`` XML element.

    Returns:
        GFM Markdown table string, or plain text if the table has no rows.
    """
    rows: list[list[str]] = []
    for child in table_elem.iter():
        tag = _strip_ns(child.tag)
        if tag == "tr":
            cells: list[str] = []
            for cell in child:
                cell_tag = _strip_ns(cell.tag)
                if cell_tag in ("td", "th"):
                    cell_text = "".join(cell.itertext()).strip().replace("|", "\\|")
                    cells.append(cell_text)
            if cells:
                rows.append(cells)

    if not rows:
        return ""

    col_count = max(len(r) for r in rows)
    # Pad rows to equal column count
    padded = [r + [""] * (col_count - len(r)) for r in rows]

    header = "| " + " | ".join(padded[0]) + " |"
    separator = "| " + " | ".join("---" for _ in range(col_count)) + " |"
    body = "\n".join("| " + " | ".join(row) + " |" for row in padded[1:])

    parts = [header, separator]
    if body:
        parts.append(body)
    parts.append("\n")
    return "\n".join(parts)


def _xhtml_to_markdown(xhtml_value: Optional[str]) -> str:
    """Convert an XHTML string (as stored in a ReqIF XHTML attribute value) to Markdown.

    Strips the outer ``<div xmlns="...">`` wrapper and recursively converts
    the inner XHTML to GitHub Flavored Markdown.  Falls back to extracting
    plain text if the XML cannot be parsed.

    Args:
        xhtml_value: XHTML string, possibly ``None``.

    Returns:
        Markdown string, stripped of leading/trailing whitespace.
    """
    if not xhtml_value:
        return ""

    # Use value_stripped_xhtml-style input if caller already stripped namespace
    xml_input = xhtml_value.strip()

    # Wrap in a root element so partial XHTML (e.g. bare <p>…</p>) parses cleanly
    try:
        # Register the XHTML namespace to avoid "ns0:" prefixes in output
        ET.register_namespace("", _XHTML_NS)
        root = ET.fromstring(xml_input)
        md = _element_to_md(root).strip()
    except ET.ParseError:
        # Fallback: extract all text with a simple regex
        md = re.sub(r"<[^>]+>", " ", xhtml_value)
        md = re.sub(r"\s+", " ", md).strip()

    return md


def _get_enum_value_names(value_refs: list[str], datatype: Any) -> str:
    """Return a human-readable string for a list of enum value identifier references.

    Args:
        value_refs: List of ENUM-VALUE identifier strings as stored in the attribute value.
        datatype:   The ReqIFDataTypeDefinitionEnumeration object.

    Returns:
        Comma-separated LONG-NAMEs of the referenced enum values.
    """
    values = getattr(datatype, "values", None) or []
    value_map: dict[str, str] = {
        v.identifier: (getattr(v, "long_name", None) or str(getattr(v, "key", v.identifier)))
        for v in values
    }
    names = [value_map.get(ref, ref) for ref in value_refs]
    return ", ".join(names)


def _get_attr_value(attr: Any, datatype_map: dict[str, Any],
                    attr_def_map: dict[str, Any]) -> tuple[str, bool]:
    """Extract the string representation of a spec-object attribute value.

    For XHTML attributes the value is converted to Markdown.
    For ENUMERATION attributes the enum long-names are returned.
    For all other types the raw string value is used.

    Args:
        attr:         SpecObjectAttribute object.
        datatype_map: Mapping from datatype identifier to datatype object.
        attr_def_map: Mapping from attribute-definition identifier to SpecAttributeDefinition.

    Returns:
        Tuple of (string value, is_xhtml) where is_xhtml indicates the source was XHTML.
    """
    _, SpecObjectAttributeType = _get_reqif_module()

    attr_type = getattr(attr, "attribute_type", None)
    raw_value = getattr(attr, "value", None)

    if attr_type == SpecObjectAttributeType.XHTML:
        # Prefer namespace-stripped value for simpler parsing
        stripped = getattr(attr, "value_stripped_xhtml", None) or raw_value
        return _xhtml_to_markdown(stripped), True

    if attr_type == SpecObjectAttributeType.ENUMERATION:
        attr_def = attr_def_map.get(getattr(attr, "definition_ref", ""))
        datatype_ref = getattr(attr_def, "datatype_definition", None) if attr_def else None
        datatype = datatype_map.get(datatype_ref) if datatype_ref else None
        refs = raw_value if isinstance(raw_value, list) else ([raw_value] if raw_value else [])
        if datatype:
            return _get_enum_value_names(refs, datatype), False
        return ", ".join(str(r) for r in refs), False

    return str(raw_value) if raw_value is not None else "", False


def _trlc_string(value: str) -> str:
    """Return a valid TRLC string literal that contains value exactly.

    Prefers triple-single-quoted form (no escaping required).  Falls back to
    triple-double-quoted if the value contains ``'''``.  As a last resort,
    replaces ``'''`` occurrences to avoid ambiguity.

    Args:
        value: The string content to embed.

    Returns:
        TRLC string literal including delimiters.
    """
    if "'''" not in value:
        return f"'''{value}'''"
    if '"""' not in value:
        return f'"""{value}"""'
    # Both delimiters present — sanitise the value (extremely rare)
    safe = value.replace("'''", "' ''")
    return f"'''{safe}'''"


def _build_attr_meta(attr_def: Any, datatype_map: dict[str, Any],  # pylint: disable=too-many-arguments,too-many-positional-arguments
                     spec_obj_attr_type: Any, used_attr_names: set[str],
                     enum_info: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Build the metadata dict for one attribute definition, or None if it should be skipped.

    Args:
        attr_def:           SpecAttributeDefinition to process.
        datatype_map:       Datatype identifier → datatype object.
        spec_obj_attr_type: The SpecObjectAttributeType enum class.
        used_attr_names:    Set of already-taken attribute names; updated in place.
        enum_info:          Enum metadata dict (see _collect_enum_info).

    Returns:
        Metadata dict with keys ``trlc_name``, ``long_name``, ``is_xhtml``,
        ``is_enum``, ``enum_trlc_name``, ``is_multi_valued``, ``datatype_ref``,
        ``attr_def_id``, ``datatype``, or None when the attribute is skipped.
    """
    attr_long_name = getattr(attr_def, "long_name", None) or attr_def.identifier
    if attr_long_name in _SKIP_LONG_NAMES:
        return None

    datatype_ref = getattr(attr_def, "datatype_definition", None)
    datatype = datatype_map.get(datatype_ref) if datatype_ref else None
    attr_type = getattr(attr_def, "attribute_type", None)
    is_xhtml = attr_type == spec_obj_attr_type.XHTML
    is_enum = attr_type == spec_obj_attr_type.ENUMERATION
    trlc_attr_name = _unique_name(_sanitize_identifier(attr_long_name), used_attr_names)

    enum_trlc_name: Optional[str] = None
    is_multi_valued = False
    if is_enum and datatype_ref:
        enum_entry = enum_info.get(datatype_ref)
        if enum_entry:
            enum_trlc_name = enum_entry["trlc_name"]
        is_multi_valued = bool(getattr(attr_def, "multi_valued", False))

    return {
        "trlc_name": trlc_attr_name,
        "long_name": attr_long_name,
        "is_xhtml": is_xhtml,
        "is_enum": is_enum,
        "enum_trlc_name": enum_trlc_name,
        "is_multi_valued": is_multi_valued,
        "datatype_ref": datatype_ref,
        "attr_def_id": attr_def.identifier,
        "datatype": datatype,
    }


def _collect_type_info(content: Any, datatype_map: dict[str, Any],
                       enum_info: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Analyse all SPEC-OBJECT-TYPEs and build metadata for RSL/TRLC generation.

    Returns two dicts:
    - type_info keyed by SPEC-OBJECT-TYPE **identifier**, each value is a dict with:
        ``trlc_name``, ``long_name``, ``is_section``, ``attrs`` list.
      Each entry in ``attrs`` has: ``trlc_name``, ``long_name``, ``is_xhtml``,
      ``is_enum``, ``enum_trlc_name``, ``is_multi_valued``, ``datatype_ref``.
    - type_id_to_trlc_name keyed by SPEC-OBJECT-TYPE identifier → trlc type name.

    Args:
        content:      ReqIFReqIFContent from the parsed bundle.
        datatype_map: Mapping from datatype identifier to datatype object.
        enum_info:    Enum metadata dict (see _collect_enum_info).

    Returns:
        Tuple of (type_info dict, type_id_to_trlc_name dict).
    """
    _, spec_obj_attr_type = _get_reqif_module()

    type_info: dict[str, Any] = {}
    type_id_to_trlc_name: dict[str, str] = {}
    used_type_names: set[str] = set()

    for spec_type in (getattr(content, "spec_types", None) or []):
        if not hasattr(spec_type, "attribute_definitions"):
            continue

        type_identifier = getattr(spec_type, "identifier", None)
        long_name = getattr(spec_type, "long_name", None) or type_identifier or "Unknown"
        attr_definitions = getattr(spec_type, "attribute_definitions", None) or []
        trlc_type_name = _unique_name(_sanitize_identifier(long_name), used_type_names)
        is_section = len(attr_definitions) == 0

        used_attr_names: set[str] = set()
        attrs = [
            meta
            for attr_def in attr_definitions
            for meta in [_build_attr_meta(
                attr_def, datatype_map, spec_obj_attr_type, used_attr_names, enum_info
            )]
            if meta is not None
        ]

        if type_identifier:
            type_info[type_identifier] = {
                "trlc_name": trlc_type_name,
                "long_name": long_name,
                "is_section": is_section,
                "attrs": attrs,
            }
            type_id_to_trlc_name[type_identifier] = trlc_type_name

    return type_info, type_id_to_trlc_name


def _get_object_name(spec_obj: Any, attr_def_map: dict[str, Any],
                     used_obj_names: set[str]) -> str:
    """Derive a TRLC record object name for a spec object.

    Preference order:
    1. Value of the ``ReqIF.ForeignID`` STRING attribute (set by pyTRLCConverter).
    2. Sanitised LONG-NAME of the spec object.
    3. Fallback ``obj_N`` counter.

    Args:
        spec_obj:       ReqIFSpecObject whose name to derive.
        attr_def_map:   Mapping from attr-def identifier to SpecAttributeDefinition.
        used_obj_names: Set of already-taken names; chosen name is registered here.

    Returns:
        Unique TRLC record object identifier string.
    """
    _, SpecObjectAttributeType = _get_reqif_module()
    foreign_id: Optional[str] = None

    for attr in (getattr(spec_obj, "attributes", None) or []):
        if getattr(attr, "attribute_type", None) != SpecObjectAttributeType.STRING:
            continue
        attr_def = attr_def_map.get(getattr(attr, "definition_ref", ""))
        if attr_def and getattr(attr_def, "long_name", None) == _REQIF_FOREIGN_ID_LONG_NAME:
            raw = getattr(attr, "value", None)
            if raw:
                foreign_id = str(raw)
            break

    if foreign_id:
        base = _sanitize_identifier(foreign_id)
    else:
        long_name = getattr(spec_obj, "long_name", None) or ""
        base = _sanitize_identifier(long_name) if long_name else "obj"

    return _unique_name(base, used_obj_names)


def _write_rsl(rsl_path: str, package_name: str, type_info: dict[str, Any],
               enum_info: dict[str, Any]) -> None:
    """Write a TRLC .rsl file containing enum and record type definitions.

    Enumeration datatypes are written as TRLC ``enum`` blocks before record
    types.  Attributes backed by an enumeration are declared with the TRLC
    enum type (single or ``[0 .. *]`` array); all other attributes are
    declared ``optional String``.

    Args:
        rsl_path:     Destination file path.
        package_name: TRLC package name.
        type_info:    Type metadata as returned by ``_collect_type_info``.
        enum_info:    Enum metadata as returned by ``_collect_enum_info``.

    Returns:
        None
    """
    lines: list[str] = []
    lines.append(f"package {package_name}")
    lines.append("")

    for enum_data in enum_info.values():
        lines.append(f'enum {enum_data["trlc_name"]} "{enum_data["long_name"]}" {{')
        for lit in enum_data["literals"].values():
            lines.append(f'    {lit["trlc_name"]}    "{lit["long_name"]}"')
        lines.append("}")
        lines.append("")

    for type_data in type_info.values():
        if type_data["is_section"]:
            continue

        lines.append(f'type {type_data["trlc_name"]} "{type_data["long_name"]}" {{')

        for attr in type_data["attrs"]:
            if attr["is_enum"] and attr["enum_trlc_name"]:
                if attr["is_multi_valued"]:
                    lines.append(
                        f'    {attr["trlc_name"]}    optional    {attr["enum_trlc_name"]}    [0 .. *]'
                    )
                else:
                    lines.append(f'    {attr["trlc_name"]}    optional    {attr["enum_trlc_name"]}')
            else:
                lines.append(f'    {attr["trlc_name"]}    optional    String')

        lines.append("}")
        lines.append("")

    with open(rsl_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _build_value_maps(spec_obj: Any, datatype_map: dict[str, Any],
                      attr_def_map: dict[str, Any]) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Build string-value and enum-reference maps for all attributes of a spec object.

    Args:
        spec_obj:     ReqIFSpecObject whose attributes to process.
        datatype_map: Datatype identifier → datatype object.
        attr_def_map: Attr-def identifier → SpecAttributeDefinition.

    Returns:
        Tuple of (value_map, enum_refs_map).
        ``value_map`` maps attribute-definition identifier → string value for non-enum attrs.
        ``enum_refs_map`` maps attribute-definition identifier → list of enum-value refs.
    """
    _, spec_obj_attr_type = _get_reqif_module()
    value_map: dict[str, str] = {}
    enum_refs_map: dict[str, list[str]] = {}

    for attr in (getattr(spec_obj, "attributes", None) or []):
        def_id = getattr(attr, "definition_ref", "")
        if getattr(attr, "attribute_type", None) == spec_obj_attr_type.ENUMERATION:
            raw = getattr(attr, "value", None)
            if raw is not None:
                enum_refs_map[def_id] = raw if isinstance(raw, list) else [raw]
        else:
            value_str, _ = _get_attr_value(attr, datatype_map, attr_def_map)
            value_map[def_id] = value_str

    return value_map, enum_refs_map


def _format_enum_attr_value(attr_meta: dict[str, Any], enum_refs: list[str],
                            ctx: "_WritingContext") -> Optional[str]:
    """Return the TRLC value string for an enumeration attribute, or None if refs is empty.

    Args:
        attr_meta:  Attribute metadata dict (from ``_build_attr_meta``).
        enum_refs:  List of raw ReqIF enum-value identifier strings.
        ctx:        Shared writing context providing ``enum_info`` and ``package_name``.

    Returns:
        A TRLC qualified enum-literal string (single or array form), or None.
    """
    if not enum_refs:
        return None
    enum_entry = ctx.enum_info.get(attr_meta["datatype_ref"], {})
    literals_map = enum_entry.get("literals", {})
    trlc_refs = [
        f"{ctx.package_name}.{attr_meta['enum_trlc_name']}."
        f"{literals_map.get(ref, {}).get('trlc_name') or _sanitize_identifier(str(ref))}"
        for ref in enum_refs
    ]
    if attr_meta["is_multi_valued"] or len(trlc_refs) > 1:
        return f"[{', '.join(trlc_refs)}]"
    return trlc_refs[0]


def _write_spec_object_instance(lines: list[str], spec_obj: Any, indent: int,  # pylint: disable=too-many-arguments,too-many-positional-arguments
                                 type_data: dict[str, Any],
                                 ctx: _WritingContext,
                                 obj_name: str) -> None:
    """Append TRLC lines for one record object instance.

    Args:
        lines:     Line buffer to append to.
        spec_obj:  ReqIFSpecObject to render.
        indent:    Current indentation level (number of 4-space steps).
        type_data: Type metadata entry for this spec object's type.
        ctx:       Shared lookup context.
        obj_name:  The unique TRLC object name for this instance.

    Returns:
        None
    """
    pad = "    " * indent
    lines.append(f"{pad}{type_data['trlc_name']} {obj_name} {{")

    value_map, enum_refs_map = _build_value_maps(spec_obj, ctx.datatype_map, ctx.attr_def_map)

    for attr_meta in type_data["attrs"]:
        if attr_meta["is_enum"] and attr_meta["enum_trlc_name"] and attr_meta["datatype_ref"]:
            refs = enum_refs_map.get(attr_meta["attr_def_id"], [])
            formatted = _format_enum_attr_value(attr_meta, refs, ctx)
            if formatted:
                lines.append(f"{pad}    {attr_meta['trlc_name']} = {formatted}")
        else:
            value_str = value_map.get(attr_meta["attr_def_id"], "")
            if value_str:
                lines.append(f"{pad}    {attr_meta['trlc_name']} = {_trlc_string(value_str)}")

    lines.append(f"{pad}}}")
    lines.append("")


def _write_hierarchy(lines: list[str], hierarchy: Any, indent: int,
                     ctx: _WritingContext, used_obj_names: set[str]) -> None:
    """Recursively append TRLC lines for a SPEC-HIERARCHY node and its children.

    Section-type spec objects generate ``section "..." { }`` blocks.
    All other spec objects generate typed record instances.

    Args:
        lines:          Line buffer to append to.
        hierarchy:      ReqIFSpecHierarchy node.
        indent:         Current indentation level.
        ctx:            Shared lookup context.
        used_obj_names: Set of already-taken object names; updated in place.

    Returns:
        None
    """
    pad = "    " * indent
    spec_obj_ref = getattr(hierarchy, "spec_object", None)
    children = getattr(hierarchy, "children", None) or []

    if not spec_obj_ref:
        for child in children:
            _write_hierarchy(lines, child, indent, ctx, used_obj_names)
        return

    spec_obj = ctx.spec_object_map.get(spec_obj_ref)
    if spec_obj is None:
        for child in children:
            _write_hierarchy(lines, child, indent, ctx, used_obj_names)
        return

    type_ref = getattr(spec_obj, "spec_object_type", None)
    type_data = ctx.type_info.get(type_ref) if type_ref else None

    if type_data is None or type_data["is_section"]:
        safe_title = (getattr(hierarchy, "long_name", None)
                      or getattr(spec_obj, "long_name", None)
                      or "Section").replace('"', '\\"')
        lines.append(f'{pad}section "{safe_title}" {{')
        lines.append("")
        for child in children:
            _write_hierarchy(lines, child, indent + 1, ctx, used_obj_names)
        lines.append(f"{pad}}}")
        lines.append("")
        return

    obj_name = _get_object_name(spec_obj, ctx.attr_def_map, used_obj_names)
    _write_spec_object_instance(lines, spec_obj, indent, type_data, ctx, obj_name)

    if children:
        safe_title = (getattr(spec_obj, "long_name", None) or obj_name).replace('"', '\\"')
        lines.append(f'{pad}section "{safe_title}" {{')
        lines.append("")
        for child in children:
            _write_hierarchy(lines, child, indent + 1, ctx, used_obj_names)
        lines.append(f"{pad}}}")
        lines.append("")


def _write_trlc(trlc_path: str, package_name: str, content: Any,
                ctx: _WritingContext) -> None:
    """Write a TRLC .trlc file with all requirement instances.

    Walks every SPECIFICATION's SPEC-HIERARCHY tree and emits TRLC sections
    and record instances in order.

    Args:
        trlc_path:    Destination file path.
        package_name: TRLC package name.
        content:      ReqIFReqIFContent from the parsed bundle.
        ctx:          Shared lookup context.

    Returns:
        None
    """
    lines: list[str] = []
    lines.append(f"package {package_name}")
    lines.append("")

    used_obj_names: set[str] = set()
    for spec in (getattr(content, "specifications", None) or []):
        spec_title = getattr(spec, "long_name", None) or "Specification"
        safe_title = spec_title.replace('"', '\\"')
        lines.append(f'section "{safe_title}" {{')
        lines.append("")
        for hierarchy in (getattr(spec, "children", None) or []):
            _write_hierarchy(lines, hierarchy, 1, ctx, used_obj_names)
        lines.append("}")
        lines.append("")

    with open(trlc_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _write_render_config(cfg_path: str, package_name: str,
                         type_info: dict[str, Any]) -> None:
    """Write a renderCfg.json marking all XHTML-sourced attributes as ``gfm``.

    Args:
        cfg_path:     Destination file path.
        package_name: TRLC package name used as the ``package`` pattern.
        type_info:    Type metadata as returned by ``_collect_type_info``.

    Returns:
        None
    """
    entries: list[dict[str, str]] = []
    for type_data in type_info.values():
        if type_data["is_section"]:
            continue
        for attr in type_data["attrs"]:
            if attr["is_xhtml"]:
                entries.append({
                    "package": package_name,
                    "type": type_data["trlc_name"],
                    "attribute": attr["trlc_name"],
                    "format": "gfm",
                })

    config = {"renderCfg": entries}
    with open(cfg_path, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=4, ensure_ascii=False)
        fh.write("\n")


def _write_translation(trans_path: str, type_info: dict[str, Any]) -> None:
    """Write a translation.json mapping TRLC attribute names to ReqIF LONG-NAMEs.

    The translation enables pyTRLCConverter to restore the original ReqIF
    attribute LONG-NAME on output so identifiers match the source file.

    Args:
        trans_path: Destination file path.
        type_info:  Type metadata as returned by ``_collect_type_info``.

    Returns:
        None
    """
    translation: dict[str, dict[str, str]] = {}
    for type_data in type_info.values():
        if type_data["is_section"]:
            continue
        trlc_type = type_data["trlc_name"]
        attr_map: dict[str, str] = {}
        for attr in type_data["attrs"]:
            if attr["trlc_name"] != attr["long_name"]:
                attr_map[attr["trlc_name"]] = attr["long_name"]
        if attr_map:
            translation[trlc_type] = attr_map

    with open(trans_path, "w", encoding="utf-8") as fh:
        json.dump(translation, fh, indent=4, ensure_ascii=False)
        fh.write("\n")


def generate_output(reqif_path: str, output_dir: str, package_name: str) -> None:
    """Parse the ReqIF file and write all four output files to output_dir.

    Args:
        reqif_path:   Path to the .reqif or .reqifz file to analyse.
        output_dir:   Directory in which to write the generated files.
        package_name: TRLC package name used for .rsl, .trlc, and renderCfg entries.

    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)

    print(f"Parsing: {reqif_path}")
    bundle = _parse_bundle(reqif_path)
    content: Any = bundle.core_content.req_if_content

    datatype_map = _build_datatype_map(content)
    enum_info = _collect_enum_info(datatype_map)
    attr_def_map = _build_attr_def_map(content)
    spec_object_map = _build_spec_object_map(content)

    type_info, _ = _collect_type_info(content, datatype_map, enum_info)
    ctx = _WritingContext(type_info, attr_def_map, datatype_map, spec_object_map,
                          enum_info, package_name)

    rsl_path = os.path.join(output_dir, f"{package_name}.rsl")
    trlc_path = os.path.join(output_dir, f"{package_name}.trlc")
    cfg_path = os.path.join(output_dir, "renderCfg.json")
    trans_path = os.path.join(output_dir, "translation.json")

    _write_rsl(rsl_path, package_name, type_info, enum_info)
    print(f"Written: {rsl_path}")

    _write_trlc(trlc_path, package_name, content, ctx)
    print(f"Written: {trlc_path}")

    _write_render_config(cfg_path, package_name, type_info)
    print(f"Written: {cfg_path}")

    _write_translation(trans_path, type_info)
    print(f"Written: {trans_path}")


def _parse_args() -> argparse.Namespace:
    """Parse and return command-line arguments.

    Returns:
        Parsed argument namespace with ``input``, ``output``, and ``package`` attributes.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Analyse a .reqif or .reqifz file and generate TRLC type definitions, "
            "requirement instances, a render configuration, and a translation file."
        )
    )
    parser.add_argument(
        "input",
        metavar="INPUT",
        help="Path to the .reqif or .reqifz file to analyse.",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT_DIR",
        default=None,
        help="Directory for the generated files.  Defaults to <input-basename>_trlc/ "
             "next to the input file.",
    )
    parser.add_argument(
        "-p", "--package",
        metavar="PACKAGE",
        default=None,
        help="TRLC package name.  Defaults to the sanitised input file basename.",
    )
    return parser.parse_args()


# Main *************************************************************************

def main() -> None:
    """Entry point: parse arguments, generate all four output files, and report paths.

    Returns:
        None
    """
    args = _parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(args.input)[1].lower()
    if ext not in (".reqif", ".reqifz"):
        print(f"WARNING: Unexpected file extension '{ext}'.  Expected .reqif or .reqifz.")

    basename = os.path.splitext(os.path.basename(args.input))[0]

    package_name = args.package or _sanitize_identifier(basename)
    output_dir = args.output or os.path.join(os.path.dirname(args.input),
                                              f"{basename}_trlc")

    generate_output(args.input, output_dir, package_name)


if __name__ == "__main__":
    main()
