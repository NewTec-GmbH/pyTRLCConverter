"""Merges a ReqIF model into existing TRLC files in place.

    Matched records are identified via the identifier store (the ReqIF identifier is mapped
    back to the stable logical key the export used). For each matched record the attribute
    values are updated in place: set string fields are spliced and previously unset optional
    string fields get a new line. Everything that is not edited stays byte-identical, so
    comments, formatting and attributes that are not part of the exchange are preserved.

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
from typing import Any, Optional
from trlc.ast import String_Literal, Implicit_Null
from pyTRLCConverter.import_config import ImportConfig
from pyTRLCConverter.logger import log_verbose
from pyTRLCConverter.reqif_identifier_store import ReqifIdentifierStore
from pyTRLCConverter.reqif_reader import ReqifReader
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_generator import trlc_string
from pyTRLCConverter.trlc_helper import get_file_dict_from_symbols, is_item_record
from pyTRLCConverter.trlc_source_patcher import TrlcSourcePatcher, find_block_close, line_indent

# Variables ********************************************************************

# Classes **********************************************************************


class ReqifMerger:  # pylint: disable=too-few-public-methods
    """Merges a ReqIF model into existing TRLC files in place."""

    def __init__(self, reader: ReqifReader, id_store: ReqifIdentifierStore,
                 import_config: ImportConfig) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Initializes the merger.

        Args:
            reader (ReqifReader): The loaded ReqIF reader.
            id_store (ReqifIdentifierStore): The loaded identifier store (reverse-mapping anchor).
            import_config (ImportConfig): The import configuration (translation and render config).
        """
        self._reader = reader
        self._reverse_map = id_store.get_reverse_map()
        self._import_config = import_config
        self._records: dict[tuple, Any] = {}
        self._patchers: dict[str, TrlcSourcePatcher] = {}
        self._summary = {"updated": 0, "inserted": 0, "orphan": 0, "unmatched_reqif": 0}

    def merge(self, symbols: Any) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Merge the ReqIF model into the existing TRLC files.

        Args:
            symbols (Any): The parsed TRLC symbol table.

        Returns:
            Ret: Status.
        """
        self._index_records(symbols)
        matched = self._merge_existing()
        self._warn_orphans(matched)

        return self._apply()

    def _index_records(self, symbols: Any) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Index all existing TRLC records and create a patcher per source file.

        Args:
            symbols (Any): The parsed TRLC symbol table.
        """
        file_dict = get_file_dict_from_symbols(symbols)

        for items in file_dict.values():
            for item in items:
                if is_item_record(item):
                    record = item[0]
                    self._records[(record.n_package.name, record.name)] = record
                    file_name = record.location.file_name
                    if file_name not in self._patchers:
                        self._patchers[file_name] = TrlcSourcePatcher(
                            file_name, record.location.lexer.content)

    def _merge_existing(self) -> set:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Merge every ReqIF spec-object that maps to an existing TRLC record.

        Returns:
            set: The set of matched TRLC record keys (package, name).
        """
        matched: set = set()

        for spec_obj in (getattr(self._reader.content, "spec_objects", None) or []):
            identifier = getattr(spec_obj, "identifier", None)
            key = self._reverse_map.get(identifier) if identifier else None
            record = self._record_for_key(key)

            if record is not None:
                matched.add((record.n_package.name, record.name))
                self._merge_record(spec_obj, record)
            else:
                self._summary["unmatched_reqif"] += 1
                log_verbose(f"ReqIF object '{getattr(spec_obj, 'long_name', '?')}' has no matching "
                            "TRLC record; not inserted.")

        return matched

    def _record_for_key(self, key: Optional[str]) -> Optional[Any]:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Return the TRLC record for a spec-object logical key, or None.

        Args:
            key (Optional[str]): The logical key from the identifier store.

        Returns:
            Optional[Any]: The matching TRLC record object, or None.
        """
        record = None

        if key is not None and key.startswith("spec-object:"):
            rest = key[len("spec-object:"):]
            if "." in rest:
                package, name = rest.rsplit(".", 1)
                record = self._records.get((package, name))

        return record

    def _merge_record(self, spec_obj: Any, record: Any) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Schedule edits to update the TRLC record fields from the matched spec-object.

        Args:
            spec_obj (Any): The matched ReqIF spec-object.
            record (Any): The TRLC record object to update.
        """
        long_name_values = self._long_name_values(spec_obj)
        type_name = record.n_typ.name
        package = record.n_package.name
        patcher = self._patchers[record.location.file_name]

        for field_name in record.field:
            reqif_long_name = self._import_config.reqif_long_name(type_name, field_name)

            if reqif_long_name in long_name_values:
                value, is_xhtml = long_name_values[reqif_long_name]
                desired = self._import_config.desired_value(
                    package, type_name, field_name, value, is_xhtml)
                if desired is not None:
                    self._apply_field(patcher, record, field_name, desired)

    def _long_name_values(self, spec_obj: Any) -> dict:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Return a mapping from ReqIF attribute long name to its (value, is_xhtml) tuple.

        Args:
            spec_obj (Any): The ReqIF spec-object.

        Returns:
            dict: Mapping from long name to a (value, is_xhtml) tuple.
        """
        result: dict = {}

        for attr in (getattr(spec_obj, "attributes", None) or []):
            attr_def = self._reader.attr_def_map.get(getattr(attr, "definition_ref", ""))
            long_name = getattr(attr_def, "long_name", None) if attr_def else None
            if long_name is not None:
                result[long_name] = self._reader.get_attr_value(attr)

        return result

    def _apply_field(self, patcher: TrlcSourcePatcher, record: Any, field_name: str,
                     desired: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Schedule an edit for a single record field if its value changed.

        A set string field is spliced; a previously unset optional string field gets a new line
        inserted before the record's closing brace. Other value kinds are preserved.

        Args:
            patcher (TrlcSourcePatcher): The patcher for the record's file.
            record (Any): The TRLC record object.
            field_name (str): The TRLC field name.
            desired (str): The desired TRLC value.
        """
        field_value = record.field[field_name]
        content = record.location.lexer.content

        if isinstance(field_value, String_Literal):
            if field_value.value != desired:
                patcher.replace(field_value.location.start_pos, field_value.location.end_pos,
                                trlc_string(desired))
                self._summary["updated"] += 1
        elif isinstance(field_value, Implicit_Null) and len(desired) > 0:
            close_pos = find_block_close(content, record.location.start_pos)
            if close_pos is not None:
                indent = line_indent(content, close_pos)
                brace_line_start = content.rfind("\n", 0, close_pos) + 1
                new_line = f"{indent}    {field_name} = {trlc_string(desired)}\n"
                patcher.insert(brace_line_start, new_line)
                self._summary["inserted"] += 1

    def _warn_orphans(self, matched: set) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Report TRLC records that have no matching ReqIF object (kept unchanged).

        Args:
            matched (set): The set of matched TRLC record keys (package, name).
        """
        for package, name in self._records:
            if (package, name) not in matched:
                self._summary["orphan"] += 1
                log_verbose(f"TRLC record '{package}.{name}' has no matching ReqIF object; "
                            "kept unchanged.")

    def _apply(self) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Apply all scheduled edits to the affected files.

        Returns:
            Ret: Status.
        """
        result = Ret.OK

        for patcher in self._patchers.values():
            if patcher.has_edits() is True:
                if patcher.apply() != Ret.OK:
                    result = Ret.ERROR

        log_verbose(f"Merge summary: updated={self._summary['updated']}, "
                    f"inserted={self._summary['inserted']}, orphan={self._summary['orphan']}, "
                    f"unmatched_reqif={self._summary['unmatched_reqif']}.")

        return result


# Functions ********************************************************************

# Main *************************************************************************
