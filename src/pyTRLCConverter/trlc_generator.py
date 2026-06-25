"""Generates TRLC source files and companion configuration from a ReqIF model.

    Used by the initial ReqIF import (bootstrap) to create a brand-new TRLC project
    from a ReqIF file: the type definitions (.rsl), the requirement instances (.trlc)
    and the companion render configuration, translation and identifier store files.

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
import json
import os
import re
from typing import Any, Optional
from pyTRLCConverter.logger import log_error, log_verbose
from pyTRLCConverter.reqif_reader import (
    ReqifReader,
    REQIF_SYSTEM_PREFIX,
    REQIF_MANDATORY_LONG_NAMES,
    extract_object_data,
    sanitize_identifier
)
from pyTRLCConverter.ret import Ret

# Variables ********************************************************************

# Default CSS values applied to GFM-rendered tables when GFM format is requested.
_GFM_TABLE_BORDER = "border: 1px solid black; border-collapse: collapse;"
_GFM_TABLE_HEADING_STYLE = "background-color: #c0c0c0;"

# Classes **********************************************************************


class TrlcGenerator:  # pylint: disable=too-few-public-methods
    """Generates TRLC source files and companion configuration from a ReqIF model."""

    def __init__(self, reader: ReqifReader, package_name: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        """Initializes the generator.

        Args:
            reader (ReqifReader): A loaded ReqIF reader.
            package_name (str): TRLC package name used for the generated files.
        """
        self._reader = reader
        self._package_name = package_name
        self._id_store: dict[str, str] = {}

    def generate(self, output_dir: str, gfm_format: bool = False) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        """Write all generated files to the output directory.

        Args:
            output_dir (str): Directory in which to write the generated files.
            gfm_format (bool): When True, emit GFM render-config entries for plain string attributes.

        Returns:
            Ret: Status.
        """
        result = Ret.OK

        try:
            os.makedirs(output_dir, exist_ok=True)

            rsl_path = os.path.join(output_dir, f"{self._package_name}.rsl")
            trlc_path = os.path.join(output_dir, f"{self._package_name}.trlc")
            cfg_path = os.path.join(output_dir, "renderCfg.json")
            trans_path = os.path.join(output_dir, "translation.json")

            self._write_rsl(rsl_path)
            self._write_trlc(trlc_path)
            self._write_render_config(cfg_path, gfm_format)
            self._write_translation(trans_path)
            self._seed_header_id()
            store_path = self._write_identifier_store(output_dir)

            log_verbose(f"Generated: {rsl_path}, {trlc_path}, {cfg_path}, {trans_path}, {store_path}")

        except (OSError, IOError) as exc:
            log_error(f"Failed to generate TRLC files: {exc}")
            result = Ret.ERROR

        return result

    def _write_rsl(self, rsl_path: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        # lobster-trace: SwRequirements.sw_req_reqif_import_enum
        """Write the .rsl file with enum and record type definitions.

        Args:
            rsl_path (str): Destination file path.
        """
        lines: list[str] = [f"package {self._package_name}", ""]

        for enum_data in self._reader.enum_info.values():
            lines.append(f'enum {enum_data["trlc_name"]} "{enum_data["long_name"]}" {{')
            max_lit_len = max((len(lit["trlc_name"]) for lit in enum_data["literals"].values()), default=0)
            for lit in enum_data["literals"].values():
                lines.append(f'    {lit["trlc_name"]:<{max_lit_len}}    "{lit["long_name"]}"')
            lines.append("}")
            lines.append("")

        for type_data in self._reader.type_info.values():
            if type_data["is_section"] is False:
                lines.append(f'type {type_data["trlc_name"]} "{type_data["long_name"]}" {{')
                max_attr_len = max((len(attr["trlc_name"]) for attr in type_data["attrs"]), default=0)
                for attr in type_data["attrs"]:
                    lines.append(self._format_rsl_attribute(attr, max_attr_len))
                lines.append("}")
                lines.append("")

        with open(rsl_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

    @staticmethod
    def _format_rsl_attribute(attr: dict[str, Any], max_attr_len: int) -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_import_enum
        """Return the RSL declaration line for a single attribute.

        Args:
            attr (dict[str, Any]): Attribute metadata.
            max_attr_len (int): Width used to align the attribute names.

        Returns:
            str: The RSL attribute declaration line.
        """
        if attr["is_enum"] and attr["enum_trlc_name"]:
            if attr["is_multi_valued"]:
                line = (f'    {attr["trlc_name"]:<{max_attr_len}}    optional    '
                        f'{attr["enum_trlc_name"]}    [0 .. *]')
            else:
                line = f'    {attr["trlc_name"]:<{max_attr_len}}    optional    {attr["enum_trlc_name"]}'
        else:
            line = f'    {attr["trlc_name"]:<{max_attr_len}}    optional    String'

        return line

    def _write_trlc(self, trlc_path: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        """Write the .trlc file with all requirement instances following the SPEC-HIERARCHY.

        Args:
            trlc_path (str): Destination file path.
        """
        lines: list[str] = [f"package {self._package_name}", ""]
        used_obj_names: set[str] = set()

        for spec in (getattr(self._reader.content, "specifications", None) or []):
            spec_title = getattr(spec, "long_name", None) or "Specification"
            safe_title = spec_title.replace('"', '\\"')
            lines.append(f'section "{safe_title}" {{')
            lines.append("")
            for hierarchy in (getattr(spec, "children", None) or []):
                self._write_hierarchy(lines, hierarchy, 1, used_obj_names)
            lines.append("}")
            lines.append("")

        with open(trlc_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

    def _write_hierarchy(self, lines: list[str], hierarchy: Any, indent: int,
                         used_obj_names: set[str]) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        """Recursively append TRLC lines for a SPEC-HIERARCHY node and its children.

        Args:
            lines (list[str]): Line buffer to append to.
            hierarchy (Any): The SPEC-HIERARCHY node.
            indent (int): Current indentation level.
            used_obj_names (set[str]): Set of already-taken object names; updated in place.
        """
        pad = "    " * indent
        spec_obj_ref = getattr(hierarchy, "spec_object", None)
        children = getattr(hierarchy, "children", None) or []
        spec_obj = self._reader.spec_object_map.get(spec_obj_ref) if spec_obj_ref else None
        type_ref = getattr(spec_obj, "spec_object_type", None) if spec_obj is not None else None
        type_data = self._reader.type_info.get(type_ref) if type_ref else None

        if spec_obj is None:
            for child in children:
                self._write_hierarchy(lines, child, indent, used_obj_names)
        elif type_data is None or type_data["is_section"]:
            safe_title = (getattr(hierarchy, "long_name", None)
                          or getattr(spec_obj, "long_name", None)
                          or "Section").replace('"', '\\"')
            lines.append(f'{pad}section "{safe_title}" {{')
            lines.append("")
            for child in children:
                self._write_hierarchy(lines, child, indent + 1, used_obj_names)
            lines.append(f"{pad}}}")
            lines.append("")
        else:
            obj_name = self._reader.get_object_name(spec_obj, used_obj_names)
            self._write_spec_object_instance(lines, spec_obj, indent, type_data, obj_name)
            self._seed_hierarchy_id(hierarchy, spec_obj, obj_name, bool(children))
            if children:
                safe_title = (getattr(spec_obj, "long_name", None) or obj_name).replace('"', '\\"')
                lines.append(f'{pad}section "{safe_title}" {{')
                lines.append("")
                for child in children:
                    self._write_hierarchy(lines, child, indent + 1, used_obj_names)
                lines.append(f"{pad}}}")
                lines.append("")

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def _write_spec_object_instance(self, lines: list[str], spec_obj: Any, indent: int,
                                    type_data: dict[str, Any], obj_name: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        # lobster-trace: SwRequirements.sw_req_reqif_import_identifier
        """Append TRLC lines for one record object instance and seed its identifier.

        Args:
            lines (list[str]): Line buffer to append to.
            spec_obj (Any): The spec-object to render.
            indent (int): Current indentation level.
            type_data (dict[str, Any]): Type metadata for this spec-object's type.
            obj_name (str): The unique TRLC object name for this instance.
        """
        pad = "    " * indent
        lines.append(f"{pad}{type_data['trlc_name']} {obj_name} {{")

        spec_obj_id = getattr(spec_obj, "identifier", None)
        if spec_obj_id:
            self._id_store[f"spec-object:{self._package_name}.{obj_name}"] = spec_obj_id

        value_map, enum_refs_map = self._reader.build_value_maps(spec_obj)

        for attr_meta in type_data["attrs"]:
            if attr_meta["is_enum"] and attr_meta["enum_trlc_name"] and attr_meta["datatype_ref"]:
                refs = enum_refs_map.get(attr_meta["attr_def_id"], [])
                formatted = self._format_enum_attr_value(attr_meta, refs)
                if formatted:
                    lines.append(f"{pad}    {attr_meta['trlc_name']} = {formatted}")
            else:
                value_str = value_map.get(attr_meta["attr_def_id"], "")
                if attr_meta["is_path"] and value_str:
                    extracted = extract_object_data(value_str)
                    if extracted is not None:
                        value_str = extracted
                self._append_string_attr(lines, pad, attr_meta["trlc_name"], value_str)

        lines.append(f"{pad}}}")
        lines.append("")

    def _format_enum_attr_value(self, attr_meta: dict[str, Any], enum_refs: list[str]) -> Optional[str]:
        # lobster-trace: SwRequirements.sw_req_reqif_import_enum
        """Return the TRLC value string for an enumeration attribute, or None if refs is empty.

        Args:
            attr_meta (dict[str, Any]): Attribute metadata.
            enum_refs (list[str]): List of raw ReqIF enum-value identifier strings.

        Returns:
            Optional[str]: A TRLC qualified enum-literal string (single or array form), or None.
        """
        formatted: Optional[str] = None

        if enum_refs:
            enum_entry = self._reader.enum_info.get(attr_meta["datatype_ref"], {})
            literals_map = enum_entry.get("literals", {})
            trlc_refs = [
                f"{self._package_name}.{attr_meta['enum_trlc_name']}."
                f"{literals_map.get(ref, {}).get('trlc_name') or sanitize_identifier(str(ref))}"
                for ref in enum_refs
            ]
            if attr_meta["is_multi_valued"] or len(trlc_refs) > 1:
                formatted = f"[{', '.join(trlc_refs)}]"
            else:
                formatted = trlc_refs[0]

        return formatted

    @staticmethod
    def _append_string_attr(lines: list[str], pad: str, attr_name: str, value_str: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        """Append a TRLC string attribute assignment to the line buffer.

        Args:
            lines (list[str]): Line buffer to append to.
            pad (str): Indentation prefix for the enclosing block.
            attr_name (str): TRLC attribute name.
            value_str (str): Raw string value to embed.
        """
        if value_str:
            trlc_lit = trlc_string(value_str)
            if "\n" in value_str:
                lines.append(f"{pad}    {attr_name} =")
                lines.append(trlc_lit)
            else:
                lines.append(f"{pad}    {attr_name} = {trlc_lit}")

    def _write_render_config(self, cfg_path: str, gfm_format: bool) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        # lobster-trace: SwRequirements.sw_req_reqif_import_xhtml
        # lobster-trace: SwRequirements.sw_req_reqif_import_path
        """Write the renderCfg.json for the round-trip conversion.

        Args:
            cfg_path (str): Destination file path.
            gfm_format (bool): When True, emit GFM entries for plain string attributes.
        """
        entries: list[dict[str, Any]] = []

        for type_data in self._reader.type_info.values():
            if type_data["is_section"] is False:
                trlc_type = type_data["trlc_name"]
                for attr in type_data["attrs"]:
                    entry = self._render_config_entry(trlc_type, attr, gfm_format)
                    if entry is not None:
                        entries.append(entry)

        with open(cfg_path, "w", encoding="utf-8") as fh:
            json.dump({"renderCfg": entries}, fh, indent=4, ensure_ascii=False)
            fh.write("\n")

    @staticmethod
    def _render_config_entry(trlc_type: str, attr: dict[str, Any],
                             gfm_format: bool) -> Optional[dict[str, Any]]:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        """Return a render-config entry for a single attribute, or None if not needed.

        Args:
            trlc_type (str): The TRLC type name.
            attr (dict[str, Any]): Attribute metadata.
            gfm_format (bool): When True, emit GFM entries for plain string attributes.

        Returns:
            Optional[dict[str, Any]]: The render-config entry, or None.
        """
        entry: Optional[dict[str, Any]] = None
        base = {"package": ".*", "type": re.escape(trlc_type), "attribute": re.escape(attr["trlc_name"])}

        if attr["is_path"]:
            entry = {**base, "format": "path"}
        elif attr["is_xhtml"]:
            entry = {**base, "format": "xhtml"}
        elif gfm_format and not attr["is_enum"]:
            entry = {
                **base,
                "format": "gfm",
                "tableOptions": {"border": _GFM_TABLE_BORDER, "headingStyle": _GFM_TABLE_HEADING_STYLE}
            }

        return entry

    def _write_translation(self, trans_path: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        """Write the translation.json mapping TRLC attribute names to ReqIF long names.

        Args:
            trans_path (str): Destination file path.
        """
        translation: dict[str, dict[str, str]] = {}

        for type_data in self._reader.type_info.values():
            if type_data["is_section"] is False:
                trlc_type = type_data["trlc_name"]
                attr_map: dict[str, str] = {}
                for attr in type_data["attrs"]:
                    long_name = self._translation_long_name(attr["long_name"])
                    if attr["trlc_name"] != long_name:
                        attr_map[attr["trlc_name"]] = long_name
                if attr_map:
                    translation[trlc_type] = attr_map

        with open(trans_path, "w", encoding="utf-8") as fh:
            json.dump(translation, fh, indent=4, ensure_ascii=False)
            fh.write("\n")

    @staticmethod
    def _translation_long_name(original: str) -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        """Return the long name to store in the translation for an attribute.

        The ReqIF system prefix is stripped except for the mandatory system attributes.

        Args:
            original (str): The original ReqIF long name.

        Returns:
            str: The long name to store in the translation.
        """
        if original.startswith(REQIF_SYSTEM_PREFIX) and original not in REQIF_MANDATORY_LONG_NAMES:
            long_name = original[len(REQIF_SYSTEM_PREFIX):]
        else:
            long_name = original

        return long_name

    def _seed_hierarchy_id(self, hierarchy: Any, spec_obj: Any, obj_name: str,
                           has_children: bool) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_identifier
        """Seed the SPEC-HIERARCHY identifier of a record node into the id store.

        Args:
            hierarchy (Any): The SPEC-HIERARCHY node being rendered.
            spec_obj (Any): The spec-object referenced by the node.
            obj_name (str): The unique TRLC object name written for the record.
            has_children (bool): Whether the node has child hierarchy nodes.
        """
        spec_obj_id = getattr(spec_obj, "identifier", None)
        hierarchy_id = getattr(hierarchy, "identifier", None)

        if spec_obj_id and hierarchy_id:
            long_name = (getattr(spec_obj, "long_name", None) or obj_name) if has_children else obj_name
            self._id_store[f"hierarchy:{spec_obj_id}:{long_name}"] = hierarchy_id

    def _seed_header_id(self) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_identifier
        """Seed the ReqIF header identifier into the id store.
        """
        header = getattr(self._reader.bundle, "req_if_header", None)
        header_id = getattr(header, "identifier", None) if header is not None else None

        if header_id:
            specifications = getattr(self._reader.content, "specifications", None) or []
            document_title = "Specification"
            if specifications:
                document_title = getattr(specifications[0], "long_name", None) or "Specification"
            self._id_store[f"req-if-header:{document_title}"] = header_id

    def _write_identifier_store(self, output_dir: str) -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_import_identifier
        """Write the id_store.json compatible with the converter's --id-store option.

        Args:
            output_dir (str): Directory in which to write id_store.json.

        Returns:
            str: The path of the written file.
        """
        store_path = os.path.join(output_dir, "id_store.json")
        data = {
            "version": 1,
            "next_id": self._compute_next_id(),
            "identifiers": self._id_store,
        }

        with open(store_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=4, sort_keys=True)
            fh.write("\n")

        return store_path

    def _compute_next_id(self) -> int:
        # lobster-trace: SwRequirements.sw_req_reqif_import_identifier
        """Return the next free identifier counter derived from the seeded identifiers.

        Returns:
            int: The next counter value (1 if no numeric suffix is found).
        """
        max_id = 0

        for value in self._id_store.values():
            match = re.search(r"-(\d+)$", value)
            if match:
                max_id = max(max_id, int(match.group(1)))

        return max_id + 1


# Functions ********************************************************************


def trlc_string(value: str) -> str:
    # lobster-trace: SwRequirements.sw_req_reqif_import_initial
    """Return a valid TRLC string literal that contains value exactly.

    Prefers the triple-single-quoted form, falls back to triple-double-quoted, and as a
    last resort sanitizes the value to avoid ambiguous delimiters.

    Args:
        value (str): The string content to embed.

    Returns:
        str: TRLC string literal including delimiters.
    """
    if "'''" not in value:
        literal = f"'''{value}'''"
    elif '"""' not in value:
        literal = f'"""{value}"""'
    else:
        literal = f"'''{value.replace(chr(39) * 3, chr(39) + ' ' + chr(39) * 2)}'''"

    return literal


# Main *************************************************************************
