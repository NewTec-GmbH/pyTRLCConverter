"""reStructuredText block elements.
    Each element renders itself into a reStructuredText string. Elements are
    collected by the RstDocument and rendered once when the output file is
    written.

    Author: Gabryel Reyes (gabryel.reyes@newtec.de)
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
from abc import ABC, abstractmethod
from typing import List
from pyTRLCConverter.logger import log_error
from pyTRLCConverter.rst.text import RstText

# Variables ********************************************************************

# Heading underline characters per heading level [1; 7].
_UNDERLINE_CHARS = ["=", "#", "~", "^", "\"", "+", "'"]

# Classes **********************************************************************

# pylint: disable-next=too-few-public-methods
class RstElement(ABC):
    """Abstract base class for reStructuredText block elements.
    """

    @abstractmethod
    def render(self) -> str:
        """Render the element into a reStructuredText string.

        Returns:
            str: Rendered reStructuredText
        """

# pylint: disable-next=too-few-public-methods
class RstHeading(RstElement):
    """reStructuredText heading block element with a label.
    """

    def __init__(self, text: str, level: int, file_name: str, escape: bool = True) -> None:
        """Initialize the heading element.

        Args:
            text (str): Heading text
            level (int): Heading level [1; 7]
            file_name (str): File name where the heading is found
            escape (bool): Escape the text (default: True).
        """
        self._text = text
        self._level = level
        self._file_name = file_name
        self._escape = escape

    def render(self) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_heading
        """Render the heading with a label.
        The text will be automatically escaped for reStructuredText if necessary.

        Returns:
            str: reStructuredText heading with a label
        """
        result = ""

        if 1 <= self._level <= 7:
            text_raw = self._text

            if self._escape is True:
                text_raw = RstText.escape(self._text)

            label = f"{self._file_name}-{text_raw.lower().replace(' ', '-')}"

            underline_char = _UNDERLINE_CHARS[self._level - 1]
            underline = underline_char * len(text_raw)

            result = f".. _{label}:\n\n{text_raw}\n{underline}\n"

        else:
            log_error(f"Invalid heading level {self._level} for {self._text}.")

        return result

# pylint: disable-next=too-few-public-methods
class RstAdmonition(RstElement):
    """reStructuredText admonition block element with a label.
    """

    def __init__(self, text: str, file_name: str, escape: bool = True) -> None:
        """Initialize the admonition element.

        Args:
            text (str): Admonition text
            file_name (str): File name where the admonition is found
            escape (bool): Escape the text (default: True).
        """
        self._text = text
        self._file_name = file_name
        self._escape = escape

    def render(self) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_admonition
        """Render the admonition with a label.
        The text will be automatically escaped for reStructuredText if necessary.

        Returns:
            str: reStructuredText admonition with a label
        """
        text_raw = self._text

        if self._escape is True:
            text_raw = RstText.escape(self._text)

        label = f"{self._file_name}-{text_raw.lower().replace(' ', '-')}"
        admonition_label = f".. admonition:: {text_raw}"

        return f".. _{label}:\n\n{admonition_label}\n"

# pylint: disable-next=too-few-public-methods
class RstTable(RstElement):
    """reStructuredText table block element in grid format.
    The column titles are escaped, the row values are taken as is. Multi-line
    cell values are supported.
    """

    def __init__(self, column_titles: List[str], rows: List[List[str]]) -> None:
        """Initialize the table element.

        Args:
            column_titles (List[str]): List of column titles.
            rows (List[List[str]]): List of row values.
        """
        self._column_titles = column_titles
        self._rows = rows

    def _calculate_widths(self) -> List[int]:
        # lobster-trace: SwRequirements.sw_req_rst_table
        """Calculate the maximum width of each column based on titles and row values.

        Returns:
            List[int]: Maximum width per column.
        """
        max_widths = [len(title) for title in self._column_titles]

        for row in self._rows:
            for idx, value in enumerate(row):
                for line in value.split('\n'):
                    max_widths[idx] = max(max_widths[idx], len(line))

        return max_widths

    @staticmethod
    def _render_head(column_titles: List[str], max_widths: List[int]) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_table
        """Render the table head. The titles are escaped for reStructuredText.

        Args:
            column_titles (List[str]): List of column titles.
            max_widths (List[int]): List of maximum widths for each column.

        Returns:
            str: Table head
        """
        escaped_titles = [RstText.escape(title) for title in column_titles]

        # Create the top border of the table.
        table_head = "    +" + "+".join(["-" * (width + 2) for width in max_widths]) + "+\n"

        # Create the title row.
        table_head += "    |"
        table_head += "|".join(
            [f" {title.ljust(max_widths[idx])} " for idx, title in enumerate(escaped_titles)]) + "|\n"

        # Create the separator row.
        table_head += "    +" + "+".join(["=" * (width + 2) for width in max_widths]) + "+\n"

        return table_head

    @staticmethod
    def _render_row(row_values: List[str], max_widths: List[int]) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_table
        """Render a table row. The values are taken as is. Multi-line values are supported.

        Args:
            row_values (List[str]): List of row values.
            max_widths (List[int]): List of maximum widths for each column.

        Returns:
            str: Table row
        """
        # Split each cell value into lines.
        split_values = [value.split('\n') for value in row_values]
        max_lines = max(len(lines) for lines in split_values)

        # Create the row with multi-line support.
        table_row = ""
        for line_idx in range(max_lines):
            table_row += "    |"
            for col_idx, lines in enumerate(split_values):
                if line_idx < len(lines):
                    table_row += f" {lines[line_idx].ljust(max_widths[col_idx])} "
                else:
                    table_row += " " * (max_widths[col_idx] + 2)
                table_row += "|"
            table_row += "\n"

        # Create the separator row.
        separator_row = "    +" + "+".join(["-" * (width + 2) for width in max_widths]) + "+\n"

        return table_row + separator_row

    def render(self) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_table
        """Render the table in grid format.

        Returns:
            str: reStructuredText table
        """
        max_widths = self._calculate_widths()

        result = RstTable._render_head(self._column_titles, max_widths)

        for row in self._rows:
            result += RstTable._render_row(row, max_widths)

        return result

# pylint: disable-next=too-few-public-methods
class RstBulletList(RstElement):
    """Unordered reStructuredText list block element.
    """

    def __init__(self, values: List[str], escape: bool = True) -> None:
        """Initialize the list element.

        Args:
            values (List[str]): List of list values.
            escape (bool): Escapes every list value (default: True).
        """
        self._values = values
        self._escape = escape

    def render(self) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_list
        """Render the unordered list.
        The values will be automatically escaped for reStructuredText if necessary.
        The last list value has no newline at the end.

        Returns:
            str: reStructuredText list
        """
        list_str = ""

        for idx, value_raw in enumerate(self._values):
            value = value_raw

            if self._escape is True:  # Escape the value if necessary.
                value = RstText.escape(value)

            list_str += f"* {value}"

            # The last list value must not have a newline at the end.
            if idx < len(self._values) - 1:
                list_str += "\n"

        return list_str

# pylint: disable-next=too-few-public-methods
class RstImage(RstElement):
    """reStructuredText image / diagram link block element.
    """

    def __init__(self, file_name: str, caption: str, escape: bool = True) -> None:
        """Initialize the image element.

        Args:
            file_name (str): Diagram file name
            caption (str): Diagram caption
            escape (bool): Escapes caption (default: True).
        """
        self._file_name = file_name
        self._caption = caption
        self._escape = escape

    def render(self) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_image
        """Render the diagram link.
        The caption will be automatically escaped for reStructuredText if necessary.

        Returns:
            str: reStructuredText diagram link
        """
        caption_raw = self._caption

        if self._escape is True:
            caption_raw = RstText.escape(self._caption)

        # Allowed are absolute and relative to source paths.
        file_name = os.path.normpath(self._file_name)

        result = f".. figure:: {file_name}\n    :alt: {caption_raw}\n"

        if caption_raw:
            result += f"\n    {caption_raw}\n"

        return result

# pylint: disable-next=too-few-public-methods
class RstRawText(RstElement):
    """Raw reStructuredText block element passed through unchanged.
    """

    def __init__(self, text: str) -> None:
        """Initialize the raw text element.

        Args:
            text (str): Raw reStructuredText
        """
        self._text = text

    def render(self) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_record
        """Render the raw text.

        Returns:
            str: Raw reStructuredText
        """
        return self._text

# Functions ********************************************************************

# Main *************************************************************************
