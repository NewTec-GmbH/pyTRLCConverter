"""Applies in-place edits to TRLC source files using character offsets.

    The patcher collects replacement and insertion edits per physical file and applies them
    in a single pass from the highest offset to the lowest, so earlier offsets stay valid.
    This keeps every byte that is not edited unchanged, preserving comments and formatting.

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
from typing import Optional
from pyTRLCConverter.logger import log_error
from pyTRLCConverter.ret import Ret

# Variables ********************************************************************

# Classes **********************************************************************


class TrlcSourcePatcher:
    """Collects and applies in-place edits to one TRLC source file."""

    def __init__(self, file_name: str, content: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Initializes the patcher with the file name and its current content.

        Args:
            file_name (str): Path to the TRLC source file.
            content (str): The current content of the file.
        """
        self._file_name = file_name
        self._content = content
        self._edits: list[dict] = []

    def replace(self, start_pos: int, end_pos: int, replacement: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Schedule a replacement of the inclusive character span with the replacement text.

        Args:
            start_pos (int): Inclusive start offset of the span to replace.
            end_pos (int): Inclusive end offset of the span to replace.
            replacement (str): The replacement text.
        """
        self._edits.append({"pos": start_pos, "end": end_pos + 1, "text": replacement})

    def insert(self, insert_at: int, text: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Schedule an insertion of text at the given offset.

        Args:
            insert_at (int): The offset at which to insert.
            text (str): The text to insert.
        """
        self._edits.append({"pos": insert_at, "end": insert_at, "text": text})

    def has_edits(self) -> bool:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Return whether any edits have been scheduled.

        Returns:
            bool: True if at least one edit is scheduled, otherwise False.
        """
        return len(self._edits) > 0

    def apply(self) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Apply all scheduled edits and write the file.

        Edits are applied from the highest start offset to the lowest so that the offsets of
        the remaining edits stay valid.

        Returns:
            Ret: Status.
        """
        result = Ret.OK
        content = self._content

        for edit in sorted(self._edits, key=lambda item: item["pos"], reverse=True):
            content = content[:edit["pos"]] + edit["text"] + content[edit["end"]:]

        try:
            with open(self._file_name, "w", encoding="utf-8") as fd:
                fd.write(content)
        except (OSError, IOError) as exc:
            log_error(f"Failed to write TRLC file '{self._file_name}': {exc}")
            result = Ret.ERROR

        return result


# Functions ********************************************************************


def find_block_close(content: str, name_start_pos: int) -> Optional[int]:
    # lobster-trace: SwRequirements.sw_req_reqif_import_merge
    """Return the offset of the closing brace of the record block starting at the given name.

    The search begins at the record name offset, locates the opening brace and balances
    braces until the matching closing brace, ignoring braces inside string literals.

    Args:
        content (str): The full TRLC file content.
        name_start_pos (int): Offset of the record name token.

    Returns:
        Optional[int]: Offset of the matching closing brace, or None if not found.
    """
    close_pos: Optional[int] = None
    depth = 0
    index = content.find("{", name_start_pos)

    if index != -1:
        pos = index
        in_string = False
        delimiter = ""

        while pos < len(content) and close_pos is None:
            char = content[pos]

            if in_string is True:
                if content.startswith(delimiter, pos):
                    in_string = False
                    pos += len(delimiter) - 1
            elif content.startswith("'''", pos):
                in_string = True
                delimiter = "'''"
                pos += 2
            elif content.startswith('"""', pos):
                in_string = True
                delimiter = '"""'
                pos += 2
            elif char in ('"', "'"):
                in_string = True
                delimiter = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    close_pos = pos

            pos += 1

    return close_pos


def line_indent(content: str, pos: int) -> str:
    # lobster-trace: SwRequirements.sw_req_reqif_import_merge
    """Return the leading whitespace of the line that contains the given offset.

    Args:
        content (str): The full TRLC file content.
        pos (int): An offset within the line.

    Returns:
        str: The leading whitespace of the line.
    """
    line_start = content.rfind("\n", 0, pos) + 1
    indent_end = line_start

    while indent_end < len(content) and content[indent_end] in (" ", "\t"):
        indent_end += 1

    return content[line_start:indent_end]


# Main *************************************************************************
