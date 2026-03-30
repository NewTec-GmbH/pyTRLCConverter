"""List all SpecTypes and their attributes from a .reqif or .reqifz file.

Reads a ReqIF file and generates a Markdown report that shows:
- All SpecTypes (SpecObjectTypes, SpecRelationTypes, SpecificationTypes)
- Their attribute definitions (name, data type, system vs. custom)
- Attributes shared across all SpecObjectTypes
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
import os
import sys
import tempfile
import zipfile
from typing import Any

# Variables ********************************************************************

SYSTEM_ATTR_PREFIX: str = "ReqIF."


# Functions ********************************************************************

def _get_reqif_module() -> tuple[type, type, type, type]:
    """Import reqif classes; exit with a helpful message if the package is not installed.

    Returns:
        Tuple of (ReqIFParser, ReqIFSpecObjectType, ReqIFSpecRelationType,
        ReqIFSpecificationType) classes.
    """
    try:
        from reqif.parser import ReqIFParser  # pylint: disable=import-outside-toplevel
        from reqif.models.reqif_spec_object_type import ReqIFSpecObjectType  # pylint: disable=import-outside-toplevel
        from reqif.models.reqif_spec_relation_type import ReqIFSpecRelationType  # pylint: disable=import-outside-toplevel
        from reqif.models.reqif_specification_type import ReqIFSpecificationType  # pylint: disable=import-outside-toplevel
        return ReqIFParser, ReqIFSpecObjectType, ReqIFSpecRelationType, ReqIFSpecificationType
    except ImportError:
        print("ERROR: 'reqif' package not found. Install it with: pip install reqif", file=sys.stderr)
        sys.exit(1)


def _is_system_attribute(long_name: str) -> bool:
    """Return True if the attribute name is a ReqIF system attribute (prefixed with 'ReqIF.').

    Args:
        long_name: The LONG-NAME of the attribute definition.

    Returns:
        True if the attribute is a system attribute, False otherwise.
    """
    return long_name.startswith(SYSTEM_ATTR_PREFIX)


def _datatype_label(attr: Any, datatype_map: dict[str, Any]) -> str:
    """Return a human-readable datatype label for an attribute definition.

    Combines the attribute type enum name with the datatype's LONG-NAME when available,
    e.g. ``XHTML (XHTML)`` or ``STRING (String)``.

    Args:
        attr:         A ``SpecAttributeDefinition`` object from the reqif library.
        datatype_map: Mapping from datatype identifier to datatype object.

    Returns:
        A human-readable string describing the data type.
    """
    attr_type = getattr(attr, "attribute_type", None)
    datatype_ref = getattr(attr, "datatype_definition", None)

    type_name: str = attr_type.name if attr_type is not None else "UNKNOWN"

    if datatype_ref and datatype_ref in datatype_map:
        dt = datatype_map[datatype_ref]
        dt_name: str = getattr(dt, "long_name", None) or datatype_ref
        return f"{type_name} ({dt_name})"

    return type_name


def _collect_attributes(spec_type: Any) -> list[Any]:
    """Return the list of attribute definitions for a spec type, or an empty list.

    Handles both ``attribute_definitions`` (SpecObjectType / SpecRelationType) and
    ``spec_attributes`` (SpecificationType) field names used by the reqif library.

    Args:
        spec_type: A spec type object from the reqif library.

    Returns:
        List of attribute definition objects, possibly empty.
    """
    attrs: list[Any] | None = getattr(spec_type, "attribute_definitions", None)
    if attrs is None:
        attrs = getattr(spec_type, "spec_attributes", None)
    return attrs or []


def _build_datatype_map(content: Any) -> dict[str, Any]:
    """Build a dict mapping datatype identifier to datatype object.

    Args:
        content: The ``ReqIFReqIFContent`` object from a parsed ReqIF bundle.

    Returns:
        Dictionary keyed by datatype identifier string.
    """
    datatype_map: dict[str, Any] = {}
    data_types: list[Any] = getattr(content, "data_types", None) or []
    for dt in data_types:
        identifier: str | None = getattr(dt, "identifier", None)
        if identifier:
            datatype_map[identifier] = dt
    return datatype_map


def _find_common_attributes(spec_object_types: list[Any]) -> list[str]:
    """Return attribute LONG-NAMEs that appear in every SpecObjectType.

    Only meaningful when there are at least two SpecObjectTypes; returns an empty
    list otherwise.

    Args:
        spec_object_types: List of ``ReqIFSpecObjectType`` objects.

    Returns:
        Sorted list of attribute long-names shared by all SpecObjectTypes.
    """
    if len(spec_object_types) < 2:
        return []

    name_sets: list[set[str]] = []
    for sot in spec_object_types:
        attrs = _collect_attributes(sot)
        name_sets.append({getattr(a, "long_name", "") for a in attrs})

    common_names: set[str] = name_sets[0]
    for s in name_sets[1:]:
        common_names = common_names & s

    return sorted(common_names)


def _write_spec_type_section(out: list[str], spec_type: Any, kind_label: str,
                              common_names: set[str], datatype_map: dict[str, Any]) -> None:
    """Append Markdown lines for one SpecType to the output list.

    Writes a level-3 heading with the type's LONG-NAME and IDENTIFIER, followed by
    an attribute table (or a note when no attributes are defined).

    Args:
        out:          List of Markdown lines to append to.
        spec_type:    A spec type object from the reqif library.
        kind_label:   Human-readable category label, e.g. ``"SpecObjectType"``.
        common_names: Set of attribute long-names shared by all SpecObjectTypes;
                      used to mark the *Shared* column.
        datatype_map: Mapping from datatype identifier to datatype object.

    Returns:
        None
    """
    long_name: str = getattr(spec_type, "long_name", "") or ""
    identifier: str = getattr(spec_type, "identifier", "") or ""
    attrs: list[Any] = _collect_attributes(spec_type)

    out.append(f"### {long_name}")
    out.append("")
    out.append(f"- **Kind:** {kind_label}")
    out.append(f"- **Identifier:** `{identifier}`")
    out.append("")

    if not attrs:
        out.append("_No attributes defined._")
        out.append("")
        return

    out.append("| Attribute Name | Data Type | System Attr | Shared |")
    out.append("| --- | --- | :---: | :---: |")

    for attr in attrs:
        name: str = getattr(attr, "long_name", "") or ""
        dtype: str = _datatype_label(attr, datatype_map)
        system_marker: str = "yes" if _is_system_attribute(name) else ""
        shared_marker: str = "yes" if name in common_names else ""
        out.append(f"| {name} | {dtype} | {system_marker} | {shared_marker} |")

    out.append("")


def _resolve_reqif_path(reqif_path: str, tmpdir: str) -> list[str]:
    """Return a list of .reqif file paths to process.

    For .reqifz archives the contents are extracted into ``tmpdir`` first.
    Exits with an error if a .reqifz archive contains no .reqif files.

    Args:
        reqif_path: Path to a .reqif or .reqifz file.
        tmpdir:     Temporary directory used for extraction of .reqifz archives.

    Returns:
        Sorted list of absolute paths to .reqif files ready for parsing.
    """
    ext: str = os.path.splitext(reqif_path)[1].lower()
    if ext == ".reqifz":
        with zipfile.ZipFile(reqif_path, "r") as zf:
            zf.extractall(tmpdir)
        paths: list[str] = [
            os.path.join(tmpdir, name)
            for name in os.listdir(tmpdir)
            if name.lower().endswith(".reqif")
        ]
        if not paths:
            print("ERROR: No .reqif file found inside the .reqifz archive.", file=sys.stderr)
            sys.exit(1)
        return sorted(paths)
    return [reqif_path]


def _write_summary_section(out: list[str], spec_object_types: list[Any],
                            spec_relation_types: list[Any], specification_types: list[Any],
                            datatype_map: dict[str, Any]) -> None:
    """Append the Summary table to the output list.

    Args:
        out:                  List of Markdown lines to append to.
        spec_object_types:    All parsed SpecObjectType objects.
        spec_relation_types:  All parsed SpecRelationType objects.
        specification_types:  All parsed SpecificationType objects.
        datatype_map:         Mapping from datatype identifier to datatype object.

    Returns:
        None
    """
    out.append("## Summary")
    out.append("")
    out.append("| Category | Count |")
    out.append("| --- | --- |")
    out.append(f"| SpecObjectTypes | {len(spec_object_types)} |")
    out.append(f"| SpecRelationTypes | {len(spec_relation_types)} |")
    out.append(f"| SpecificationTypes | {len(specification_types)} |")
    out.append(f"| Data types | {len(datatype_map)} |")
    out.append("")


def _write_enum_values_section(out: list[str], data_types: list[Any]) -> None:
    """Append enumeration value tables for all enumeration data types.

    For each data type that has enum values, appends a level-3 subsection
    with a table listing the key and long name of every enum literal.
    The section is omitted entirely when no enumeration types are found.

    Args:
        out:        List of Markdown lines to append to.
        data_types: List of data type objects from the reqif library.

    Returns:
        None
    """
    enum_types: list[Any] = [dt for dt in data_types if getattr(dt, "values", None)]
    if not enum_types:
        return

    out.append("### Enumeration Values")
    out.append("")

    for dt in enum_types:
        dt_name: str = getattr(dt, "long_name", "") or ""
        out.append(f"#### {dt_name}")
        out.append("")
        out.append("| Key | Long Name |")
        out.append("| --- | --- |")
        for val in dt.values:
            key: str = str(getattr(val, "key", "") or "")
            long_name: str = getattr(val, "long_name", "") or ""
            out.append(f"| {key} | {long_name} |")
        out.append("")


def _write_datatypes_section(out: list[str], content: Any) -> None:
    """Append the Data Types section to the output list.

    Args:
        out:     List of Markdown lines to append to.
        content: The ``ReqIFReqIFContent`` object from a parsed ReqIF bundle.

    Returns:
        None
    """
    out.append("## Data Types")
    out.append("")
    data_types: list[Any] = getattr(content, "data_types", None) or []
    if data_types:
        out.append("| Name | Identifier | Kind |")
        out.append("| --- | --- | --- |")
        for dt in data_types:
            dt_name: str = getattr(dt, "long_name", "") or ""
            dt_id: str = getattr(dt, "identifier", "") or ""
            dt_kind: str = type(dt).__name__
            out.append(f"| {dt_name} | `{dt_id}` | {dt_kind} |")
        out.append("")
        _write_enum_values_section(out, data_types)
    else:
        out.append("_No data types defined._")
        out.append("")


def _write_shared_attributes_section(out: list[str], common_names: set[str]) -> None:
    """Append the shared-attributes section to the output list.

    The section is omitted entirely when ``common_names`` is empty.

    Args:
        out:          List of Markdown lines to append to.
        common_names: Set of attribute long-names shared by all SpecObjectTypes.

    Returns:
        None
    """
    if not common_names:
        return

    out.append("## Attributes Shared by All SpecObjectTypes")
    out.append("")
    out.append("> These attributes appear in **every** SpecObjectType defined in this file.")
    out.append("")
    out.append("| Attribute Name | System Attr |")
    out.append("| --- | :---: |")
    for name in sorted(common_names):
        system_marker: str = "yes" if _is_system_attribute(name) else ""
        out.append(f"| {name} | {system_marker} |")
    out.append("")


def _write_spec_types_group(out: list[str], spec_types: list[Any],
                             kind_label: str, common_names: set[str],
                             datatype_map: dict[str, Any]) -> None:
    """Append a top-level section for a group of SpecTypes to the output list.

    The level-2 heading is derived from ``kind_label`` by appending an ``s``,
    e.g. ``"SpecObjectType"`` → ``"## SpecObjectTypes"``.

    Args:
        out:          List of Markdown lines to append to.
        spec_types:   List of spec type objects belonging to this group.
        kind_label:   Human-readable category label passed to each type's subsection.
        common_names: Set of attribute long-names used to mark the *Shared* column.
        datatype_map: Mapping from datatype identifier to datatype object.

    Returns:
        None
    """
    heading: str = f"## {kind_label}s"
    out.append(heading)
    out.append("")
    if spec_types:
        for spec_type in spec_types:
            _write_spec_type_section(out, spec_type, kind_label, common_names, datatype_map)
    else:
        out.append(f"_No {kind_label}s defined._")
        out.append("")


def _parse_bundle(reqif_path: str) -> Any:
    """Parse the ReqIF file (or the first file inside a .reqifz archive) and return the bundle.

    Args:
        reqif_path: Path to a .reqif or .reqifz file.

    Returns:
        A ``ReqIFBundle`` object produced by ``ReqIFParser.parse()``.
    """
    reqif_parser = _get_reqif_module()[0]
    with tempfile.TemporaryDirectory() as tmpdir:
        reqif_files: list[str] = _resolve_reqif_path(reqif_path, tmpdir)
        actual_path: str = reqif_files[0]
        if len(reqif_files) > 1:
            print(
                f"INFO: Archive contains {len(reqif_files)} .reqif files; "
                f"reporting on: {os.path.basename(actual_path)}"
            )
        return reqif_parser.parse(actual_path)


def generate_report(reqif_path: str) -> str:
    """Parse the ReqIF file and return a Markdown report string.

    Analyses all SpecTypes (SpecObjectTypes, SpecRelationTypes, SpecificationTypes)
    and their attribute definitions, then formats the result as a Markdown document.

    Args:
        reqif_path: Path to a .reqif or .reqifz file.

    Returns:
        The complete Markdown report as a single string.
    """
    _, spec_object_type_cls, spec_relation_type_cls, specification_type_cls = _get_reqif_module()

    bundle = _parse_bundle(reqif_path)
    content: Any = bundle.core_content.req_if_content
    datatype_map: dict[str, Any] = _build_datatype_map(content)
    spec_types: list[Any] = getattr(content, "spec_types", None) or []

    spec_object_types: list[Any] = [s for s in spec_types if isinstance(s, spec_object_type_cls)]
    spec_relation_types: list[Any] = [s for s in spec_types if isinstance(s, spec_relation_type_cls)]
    specification_types: list[Any] = [s for s in spec_types if isinstance(s, specification_type_cls)]
    common_names: set[str] = set(_find_common_attributes(spec_object_types))

    out: list[str] = []
    out.append(f"# ReqIF Type Overview: {os.path.basename(reqif_path)}")
    out.append("")

    _write_summary_section(out, spec_object_types, spec_relation_types,
                           specification_types, datatype_map)
    _write_datatypes_section(out, content)
    _write_shared_attributes_section(out, common_names)
    _write_spec_types_group(out, spec_object_types, "SpecObjectType", common_names, datatype_map)
    _write_spec_types_group(out, spec_relation_types, "SpecRelationType", set(), datatype_map)
    _write_spec_types_group(out, specification_types, "SpecificationType", set(), datatype_map)

    return "\n".join(out)


def _parse_args() -> argparse.Namespace:
    """Parse and return command-line arguments.

    Returns:
        Parsed argument namespace with ``input`` and ``output`` attributes.
    """
    parser = argparse.ArgumentParser(
        description="Generate a Markdown overview of types and attributes in a ReqIF file."
    )
    parser.add_argument(
        "input",
        metavar="INPUT",
        help="Path to the .reqif or .reqifz file to analyse."
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT",
        default=None,
        help="Path for the generated Markdown file. "
             "Defaults to <input-basename>_types.md next to the input file."
    )
    return parser.parse_args()


# Main *************************************************************************

def main() -> None:
    """Entry point: parse arguments, generate the report, and write it to disk.

    Returns:
        None
    """
    args: argparse.Namespace = _parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    ext: str = os.path.splitext(args.input)[1].lower()
    if ext not in (".reqif", ".reqifz"):
        print(f"WARNING: Unexpected file extension '{ext}'. Expected .reqif or .reqifz.")

    if args.output:
        output_path: str = args.output
    else:
        basename: str = os.path.splitext(os.path.basename(args.input))[0]
        output_path = os.path.join(os.path.dirname(args.input), f"{basename}_types.md")

    report: str = generate_report(args.input)

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(report)

    print(f"Report written to: {output_path}")


if __name__ == "__main__":
    main()
