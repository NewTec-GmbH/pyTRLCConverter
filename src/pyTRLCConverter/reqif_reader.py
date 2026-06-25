"""Reads a ReqIF file and provides a normalized model for the ReqIF import.

    The reader parses a .reqif or .reqifz file with the reqif library and exposes
    the datatypes, attribute definitions, spec-object types and spec-objects as
    convenient lookup structures together with helpers to extract attribute values.

    Author: Andreas Merkle (andreas.merkle@newtec.de)
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
import os
import re
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from typing import Any, Optional
from reqif.parser import ReqIFParser
from reqif.models.reqif_types import SpecObjectAttributeType
from pyTRLCConverter.logger import log_error, log_verbose

# Variables ********************************************************************

# ReqIF system attribute prefix used for the requirements exchange (ReqIF IG).
REQIF_SYSTEM_PREFIX = "ReqIF."

# Long name of the foreign identifier attribute written by the ReqIF export.
REQIF_FOREIGN_ID_LONG_NAME = "ReqIF.ForeignID"

# ReqIF system attributes whose full long name (including the prefix) must be preserved.
REQIF_MANDATORY_LONG_NAMES = frozenset({
    "ReqIF.Name",
    "ReqIF.Text",
    "ReqIF.Description",
})

# TRLC keywords which must not be used as identifiers.
TRLC_KEYWORDS = frozenset({
    "abs", "abstract", "and", "checks", "else", "elsif", "enum", "error",
    "exists", "extends", "false", "fatal", "final", "forall", "freeze", "if",
    "implies", "import", "in", "not", "null", "optional", "or", "package",
    "section", "separator", "then", "true", "tuple", "type", "warning", "xor",
})

# Matches a UUID (with optional leading underscore) used as an internal attachment reference.
_INTERNAL_UUID_RE = re.compile(
    r"^_?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

# Classes **********************************************************************


# pylint: disable-next=too-many-instance-attributes
class ReqifReader:
    """Parses a ReqIF file and provides a normalized model for the import."""

    def __init__(self) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Initializes the ReqIF reader.
        """
        self._bundle: Any = None
        self._content: Any = None
        self._datatype_map: dict[str, Any] = {}
        self._enum_info: dict[str, Any] = {}
        self._attr_def_map: dict[str, Any] = {}
        self._spec_object_map: dict[str, Any] = {}
        self._type_info: dict[str, Any] = {}
        self._type_id_to_trlc_name: dict[str, str] = {}

    def load(self, reqif_path: str) -> bool:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Parse the ReqIF file and build the lookup structures.

        A .reqifz archive is extracted transparently and its first .reqif file is used.

        Args:
            reqif_path (str): Path to a .reqif or .reqifz file.

        Returns:
            bool: True on success, False otherwise.
        """
        status = False

        try:
            with tempfile.TemporaryDirectory(prefix="pyTRLCConverter_reqif_import_") as tmpdir:
                reqif_files = self._resolve_reqif_path(reqif_path, tmpdir)

                if len(reqif_files) == 0:
                    log_error(f"No .reqif file found in '{reqif_path}'.")
                else:
                    if len(reqif_files) > 1:
                        log_verbose(f"Archive contains {len(reqif_files)} .reqif files; "
                                    f"using {os.path.basename(reqif_files[0])}.")

                    self._bundle = ReqIFParser.parse(reqif_files[0])
                    self._content = self._bundle.core_content.req_if_content
                    self._build_maps()
                    status = True

        except (OSError, zipfile.BadZipFile, ValueError) as exc:
            log_error(f"Failed to read ReqIF file '{reqif_path}': {exc}")

        return status

    @property
    def bundle(self) -> Any:
        """Returns the parsed ReqIF bundle.

        Returns:
            Any: The ReqIFBundle object.
        """
        return self._bundle

    @property
    def content(self) -> Any:
        """Returns the ReqIF content of the parsed bundle.

        Returns:
            Any: The ReqIFReqIFContent object.
        """
        return self._content

    @property
    def type_info(self) -> dict[str, Any]:
        """Returns the spec-object type metadata keyed by type identifier.

        Returns:
            dict[str, Any]: The type metadata.
        """
        return self._type_info

    @property
    def enum_info(self) -> dict[str, Any]:
        """Returns the enumeration datatype metadata keyed by datatype identifier.

        Returns:
            dict[str, Any]: The enumeration metadata.
        """
        return self._enum_info

    @property
    def spec_object_map(self) -> dict[str, Any]:
        """Returns the spec-objects keyed by identifier.

        Returns:
            dict[str, Any]: The spec-object map.
        """
        return self._spec_object_map

    @property
    def attr_def_map(self) -> dict[str, Any]:
        """Returns the attribute definitions keyed by identifier.

        Returns:
            dict[str, Any]: The attribute definition map.
        """
        return self._attr_def_map

    def _resolve_reqif_path(self, reqif_path: str, tmpdir: str) -> list[str]:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Return the .reqif file paths to process, extracting .reqifz archives first.

        Args:
            reqif_path (str): Path to a .reqif or .reqifz file.
            tmpdir (str): Temporary directory used when extracting .reqifz archives.

        Returns:
            list[str]: Sorted list of .reqif file paths.
        """
        paths = [reqif_path]

        if os.path.splitext(reqif_path)[1].lower() == ".reqifz":
            with zipfile.ZipFile(reqif_path, "r") as zf:
                zf.extractall(tmpdir)
            paths = sorted(
                os.path.join(tmpdir, name)
                for name in os.listdir(tmpdir)
                if name.lower().endswith(".reqif")
            )

        return paths

    def _build_maps(self) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Build all lookup structures from the parsed ReqIF content.
        """
        self._datatype_map = self._build_datatype_map()
        self._enum_info = self._collect_enum_info()
        self._attr_def_map = self._build_attr_def_map()
        self._spec_object_map = self._build_spec_object_map()
        self._type_info, self._type_id_to_trlc_name = self._collect_type_info()

        path_attr_def_ids = self._detect_path_attributes()
        for type_data in self._type_info.values():
            for attr in type_data["attrs"]:
                if attr["attr_def_id"] in path_attr_def_ids:
                    attr["is_path"] = True

    def _build_datatype_map(self) -> dict[str, Any]:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Build a mapping from datatype identifier to datatype object.

        Returns:
            dict[str, Any]: Datatype map keyed by identifier.
        """
        result: dict[str, Any] = {}

        for datatype in (getattr(self._content, "data_types", None) or []):
            identifier = getattr(datatype, "identifier", None)
            if identifier:
                result[identifier] = datatype

        return result

    def _collect_enum_info(self) -> dict[str, Any]:
        # lobster-trace: SwRequirements.sw_req_reqif_import_enum
        """Build metadata for all DATATYPE-DEFINITION-ENUMERATION entries.

        Returns:
            dict[str, Any]: Enum metadata keyed by datatype identifier. Each value holds
            the TRLC enum type name, the original long name and a literal map.
        """
        enum_info: dict[str, Any] = {}
        used_enum_names: set[str] = set()

        for dt_id, datatype in self._datatype_map.items():
            values = getattr(datatype, "values", None)

            if values is not None:
                long_name = getattr(datatype, "long_name", None) or dt_id
                trlc_name = unique_name(sanitize_identifier(long_name), used_enum_names)

                literals: dict[str, dict[str, str]] = {}
                used_lit_names: set[str] = set()
                for value in values:
                    lit_long_name = (
                        getattr(value, "long_name", None)
                        or str(getattr(value, "key", getattr(value, "identifier", "unknown")))
                    )
                    trlc_lit_name = unique_name(sanitize_identifier(lit_long_name), used_lit_names)
                    literals[getattr(value, "identifier", lit_long_name)] = {
                        "trlc_name": trlc_lit_name,
                        "long_name": lit_long_name,
                    }

                enum_info[dt_id] = {
                    "trlc_name": trlc_name,
                    "long_name": long_name,
                    "literals": literals,
                }

        return enum_info

    def _build_attr_def_map(self) -> dict[str, Any]:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Build a mapping from attribute-definition identifier to attribute definition.

        Returns:
            dict[str, Any]: Attribute definition map keyed by identifier.
        """
        result: dict[str, Any] = {}

        for spec_type in (getattr(self._content, "spec_types", None) or []):
            attrs = getattr(spec_type, "attribute_definitions", None) \
                or getattr(spec_type, "spec_attributes", None) or []
            for attr_def in attrs:
                identifier = getattr(attr_def, "identifier", None)
                if identifier:
                    result[identifier] = attr_def

        return result

    def _build_spec_object_map(self) -> dict[str, Any]:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Build a mapping from spec-object identifier to spec-object.

        Returns:
            dict[str, Any]: Spec-object map keyed by identifier.
        """
        result: dict[str, Any] = {}

        for obj in (getattr(self._content, "spec_objects", None) or []):
            identifier = getattr(obj, "identifier", None)
            if identifier:
                result[identifier] = obj

        return result

    def _collect_type_info(self) -> tuple[dict[str, Any], dict[str, str]]:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Analyse all SPEC-OBJECT-TYPEs and build metadata for the TRLC generation.

        Returns:
            tuple[dict[str, Any], dict[str, str]]: The type metadata keyed by type identifier
            and a mapping from type identifier to TRLC type name.
        """
        type_info: dict[str, Any] = {}
        type_id_to_trlc_name: dict[str, str] = {}
        used_type_names: set[str] = set()

        for spec_type in (getattr(self._content, "spec_types", None) or []):
            if hasattr(spec_type, "attribute_definitions"):
                type_identifier = getattr(spec_type, "identifier", None)
                long_name = getattr(spec_type, "long_name", None) or type_identifier or "Unknown"
                attr_definitions = getattr(spec_type, "attribute_definitions", None) or []
                trlc_type_name = unique_name(sanitize_identifier(long_name), used_type_names)
                is_section = len(attr_definitions) == 0

                used_attr_names: set[str] = set()
                attrs = [
                    self._build_attr_meta(attr_def, used_attr_names)
                    for attr_def in attr_definitions
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

    def _build_attr_meta(self, attr_def: Any, used_attr_names: set[str]) -> dict[str, Any]:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Build the metadata dict for one attribute definition.

        Args:
            attr_def (Any): The attribute definition to process.
            used_attr_names (set[str]): Set of already-taken attribute names; updated in place.

        Returns:
            dict[str, Any]: Attribute metadata.
        """
        attr_long_name = getattr(attr_def, "long_name", None) or attr_def.identifier
        datatype_ref = getattr(attr_def, "datatype_definition", None)
        datatype = self._datatype_map.get(datatype_ref) if datatype_ref else None
        attr_type = getattr(attr_def, "attribute_type", None)
        is_xhtml = attr_type == SpecObjectAttributeType.XHTML
        is_enum = attr_type == SpecObjectAttributeType.ENUMERATION
        trlc_base = (attr_long_name[len(REQIF_SYSTEM_PREFIX):]
                     if attr_long_name.startswith(REQIF_SYSTEM_PREFIX)
                     else attr_long_name)
        trlc_attr_name = unique_name(sanitize_identifier(trlc_base), used_attr_names)

        enum_trlc_name: Optional[str] = None
        is_multi_valued = False
        if is_enum and datatype_ref:
            enum_entry = self._enum_info.get(datatype_ref)
            if enum_entry:
                enum_trlc_name = enum_entry["trlc_name"]
            is_multi_valued = bool(getattr(attr_def, "multi_valued", False))

        return {
            "trlc_name": trlc_attr_name,
            "long_name": attr_long_name,
            "is_xhtml": is_xhtml,
            "is_path": False,
            "is_enum": is_enum,
            "enum_trlc_name": enum_trlc_name,
            "is_multi_valued": is_multi_valued,
            "datatype_ref": datatype_ref,
            "attr_def_id": attr_def.identifier,
            "datatype": datatype,
        }

    def _detect_path_attributes(self) -> set[str]:
        # lobster-trace: SwRequirements.sw_req_reqif_import_path
        """Scan spec-object XHTML attribute values and identify path-format candidates.

        An XHTML attribute whose value is a single ``<object>`` element with a plain local
        file reference becomes a path candidate. Other ``data`` URI schemes are not supported
        and a verbose warning is emitted instead.

        Returns:
            set[str]: Attribute-definition identifiers that should use the path format.
        """
        path_attr_ids: set[str] = set()
        warned_attr_ids: set[str] = set()

        for spec_obj in (getattr(self._content, "spec_objects", None) or []):
            for attr in (getattr(spec_obj, "attributes", None) or []):
                def_id = getattr(attr, "definition_ref", "")

                if getattr(attr, "attribute_type", None) == SpecObjectAttributeType.XHTML:
                    if def_id not in path_attr_ids and def_id not in warned_attr_ids:
                        self._classify_path_attribute(attr, def_id, path_attr_ids, warned_attr_ids)

        return path_attr_ids

    def _classify_path_attribute(self, attr: Any, def_id: str,
                                 path_attr_ids: set[str], warned_attr_ids: set[str]) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_path
        """Classify a single XHTML attribute as a path candidate or an unsupported reference.

        Args:
            attr (Any): The spec-object attribute.
            def_id (str): The attribute-definition identifier.
            path_attr_ids (set[str]): Set of path candidates; updated in place.
            warned_attr_ids (set[str]): Set of warned definitions; updated in place.
        """
        xhtml = getattr(attr, "value_stripped_xhtml", None) or getattr(attr, "value", None)
        xhtml_str = str(xhtml) if xhtml is not None else ""
        data_value = extract_object_data(xhtml_str) if xhtml_str.strip() else None

        if data_value is not None:
            attr_def = self._attr_def_map.get(def_id)
            attr_long_name = getattr(attr_def, "long_name", def_id) if attr_def else def_id

            if data_value.startswith("data:"):
                log_verbose(f"Attribute '{attr_long_name}' embeds a base64 file; using xhtml format.")
                warned_attr_ids.add(def_id)
            elif _INTERNAL_UUID_RE.match(data_value):
                log_verbose(f"Attribute '{attr_long_name}' references an internal attachment; "
                            "using xhtml format.")
                warned_attr_ids.add(def_id)
            elif "://" in data_value or data_value.startswith("urn:"):
                log_verbose(f"Attribute '{attr_long_name}' references a remote file; using xhtml format.")
                warned_attr_ids.add(def_id)
            else:
                path_attr_ids.add(def_id)

    def get_attr_value(self, attr: Any) -> tuple[str, bool]:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Extract the string representation of a spec-object attribute value.

        Args:
            attr (Any): The spec-object attribute.

        Returns:
            tuple[str, bool]: The string value and a flag indicating whether the source was XHTML.
        """
        attr_type = getattr(attr, "attribute_type", None)
        raw_value = getattr(attr, "value", None)
        is_xhtml = False

        if attr_type == SpecObjectAttributeType.XHTML:
            xhtml = getattr(attr, "value_stripped_xhtml", None) or raw_value
            xhtml_str = str(xhtml) if xhtml is not None else ""
            value = unwrap_xhtml_div(xhtml_str)
            is_xhtml = True
        elif attr_type == SpecObjectAttributeType.ENUMERATION:
            value = self.get_enum_attr_string(attr, raw_value)
        else:
            value = str(raw_value) if raw_value is not None else ""

        return value, is_xhtml

    def get_enum_attr_string(self, attr: Any, raw_value: Any) -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_import_enum
        """Resolve an enumeration attribute value to a comma-separated string of long-names.

        Args:
            attr (Any): The spec-object attribute.
            raw_value (Any): The raw value (identifier or list of identifiers).

        Returns:
            str: Comma-separated long names, or raw identifiers when the datatype is unknown.
        """
        attr_def = self._attr_def_map.get(getattr(attr, "definition_ref", ""))
        datatype_ref = getattr(attr_def, "datatype_definition", None) if attr_def else None
        datatype = self._datatype_map.get(datatype_ref) if datatype_ref else None

        if isinstance(raw_value, list):
            refs = raw_value
        elif raw_value:
            refs = [raw_value]
        else:
            refs = []

        if datatype is not None:
            values = getattr(datatype, "values", None) or []
            value_map = {
                value.identifier: (getattr(value, "long_name", None) or str(getattr(value, "key", value.identifier)))
                for value in values
            }
            names = [value_map.get(ref, ref) for ref in refs]
        else:
            names = [str(ref) for ref in refs]

        return ", ".join(names)

    def build_value_maps(self, spec_obj: Any) -> tuple[dict[str, str], dict[str, list[str]]]:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Build string-value and enum-reference maps for all attributes of a spec-object.

        Args:
            spec_obj (Any): The spec-object whose attributes to process.

        Returns:
            tuple[dict[str, str], dict[str, list[str]]]: A value map (attr-def id to string value
            for non-enum attributes) and an enum-reference map (attr-def id to list of refs).
        """
        value_map: dict[str, str] = {}
        enum_refs_map: dict[str, list[str]] = {}

        for attr in (getattr(spec_obj, "attributes", None) or []):
            def_id = getattr(attr, "definition_ref", "")

            if getattr(attr, "attribute_type", None) == SpecObjectAttributeType.ENUMERATION:
                raw = getattr(attr, "value", None)
                if raw is not None:
                    enum_refs_map[def_id] = raw if isinstance(raw, list) else [raw]
            else:
                value_str, _ = self.get_attr_value(attr)
                value_map[def_id] = value_str

        return value_map, enum_refs_map

    def get_object_name(self, spec_obj: Any, used_obj_names: set[str]) -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Derive a unique TRLC record object name for a spec-object.

        The foreign identifier attribute is preferred, then the sanitized long name,
        then a generic fallback.

        Args:
            spec_obj (Any): The spec-object whose name to derive.
            used_obj_names (set[str]): Set of already-taken names; updated in place.

        Returns:
            str: The unique TRLC record object name.
        """
        foreign_id: Optional[str] = None

        for attr in (getattr(spec_obj, "attributes", None) or []):
            if getattr(attr, "attribute_type", None) == SpecObjectAttributeType.STRING:
                attr_def = self._attr_def_map.get(getattr(attr, "definition_ref", ""))
                if attr_def and getattr(attr_def, "long_name", None) == REQIF_FOREIGN_ID_LONG_NAME:
                    raw = getattr(attr, "value", None)
                    if raw:
                        foreign_id = str(raw)
                    break

        if foreign_id:
            base = sanitize_identifier(foreign_id)
        else:
            long_name = getattr(spec_obj, "long_name", None) or ""
            base = sanitize_identifier(long_name) if long_name else "obj"

        return unique_name(base, used_obj_names)


# Functions ********************************************************************


def sanitize_identifier(name: str) -> str:
    # lobster-trace: SwRequirements.sw_req_reqif_import
    """Convert an arbitrary name to a valid TRLC identifier.

    Args:
        name (str): Arbitrary name string (e.g. a long name or identifier).

    Returns:
        str: A valid, non-empty TRLC identifier.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")

    if cleaned and cleaned[0].isdigit():
        cleaned = "x" + cleaned

    if not cleaned:
        cleaned = "unnamed"

    if cleaned in TRLC_KEYWORDS:
        cleaned = cleaned + "_"

    return cleaned


def unique_name(base: str, used: set[str]) -> str:
    # lobster-trace: SwRequirements.sw_req_reqif_import
    """Return a name derived from base that is not already used, then register it.

    Args:
        base (str): Preferred name.
        used (set[str]): Set of already-taken names; the chosen name is added to it.

    Returns:
        str: A unique name.
    """
    candidate = base
    counter = 1

    while candidate in used:
        candidate = f"{base}_{counter}"
        counter += 1

    used.add(candidate)

    return candidate


def extract_object_data(xhtml_str: str) -> Optional[str]:
    # lobster-trace: SwRequirements.sw_req_reqif_import_path
    """Return the data attribute of the first object element in an XHTML string.

    Args:
        xhtml_str (str): XHTML string, possibly containing an outer div wrapper.

    Returns:
        Optional[str]: The data attribute value, or None if no object element is found.
    """
    result = None
    stripped = xhtml_str.strip()

    try:
        root = ET.fromstring(f"<root>{stripped}</root>")
    except ET.ParseError:
        root = None

    if root is not None:
        for elem in root.iter():
            local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if local.lower() == "object":
                result = elem.get("data")
                break

    return result


def unwrap_xhtml_div(xhtml_str: str) -> str:
    # lobster-trace: SwRequirements.sw_req_reqif_import_xhtml
    """Strip the outer div wrapper from a namespace-stripped XHTML string.

    The ReqIF export wraps XHTML content in a div; storing that div in TRLC would cause
    the converter to add a second wrapper on the round-trip. The inner content is returned
    so the converter can re-wrap it correctly.

    Args:
        xhtml_str (str): Namespace-stripped XHTML string.

    Returns:
        str: The inner content of the div, or the original string on any error.
    """
    result = xhtml_str
    stripped = xhtml_str.strip()
    root = None

    if stripped.startswith("<div"):
        try:
            root = ET.fromstring(stripped)
        except ET.ParseError:
            root = None

    if root is not None and root.tag == "div":
        inner_parts = []
        if root.text:
            inner_parts.append(root.text)
        for child in root:
            inner_parts.append(ET.tostring(child, encoding="unicode"))
            if child.tail:
                inner_parts.append(child.tail)
        result = "".join(inner_parts)

    return result


# Main *************************************************************************
