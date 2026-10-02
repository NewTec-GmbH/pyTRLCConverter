"""Markdown block elements.
    Each element renders itself into a Markdown string. Elements are collected
    by the MarkdownDocument and rendered once when the output file is written.

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
from abc import ABC, abstractmethod
from typing import List
from pyTRLCConverter.logger import log_error
from pyTRLCConverter.markdown.text import MarkdownText

# Variables ********************************************************************

# Classes **********************************************************************

# pylint: disable-next=too-few-public-methods
class MarkdownElement(ABC):
    """Abstract base class for Markdown block elements.
    """

    @abstractmethod
    def render(self) -> str:
        """Render the element into a Markdown string.

        Returns:
            str: Rendered Markdown
        """

# pylint: disable-next=too-few-public-methods
class Heading(MarkdownElement):
    """Markdown heading block element.
    """

    def __init__(self, text: str, level: int, escape: bool = True) -> None:
        """Initialize the heading element.

        Args:
            text (str): Heading text
            level (int): Heading level [1; inf]
            escape (bool): Escape the text (default: True).
        """
        self._text = text
        self._level = level
        self._escape = escape

    def render(self) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_heading
        """Render the heading.
        The text will be automatically escaped for Markdown if necessary.

        Returns:
            str: Markdown heading
        """
        result = ""

        if 1 <= self._level:
            text_raw = self._text

            if self._escape is True:
                text_raw = MarkdownText.escape(self._text)

            result = f"{'#' * self._level} {text_raw}\n"

        else:
            log_error(f"Invalid heading level {self._level} for {self._text}.")

        return result

# pylint: disable-next=too-few-public-methods
class Table(MarkdownElement):
    """Markdown table block element.
    Rendered as HTML to support multi-line cells and other complex content.
    """

    def __init__(self, column_titles: List[str], rows: List[List[str]]) -> None:
        """Initialize the table element.

        Args:
            column_titles (List[str]): List of column titles.
            rows (List[List[str]]): List of row values.
        """
        self._column_titles = column_titles
        self._rows = rows

    def render(self) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_table
        """Render the table in HTML format.

        Returns:
            str: Markdown table
        """
        table = "<table>\n"
        table += "<thead>\n"
        table += "<tr>\n"

        for column_title in self._column_titles:
            table += f"<th>{column_title}</th>\n"

        table += "</tr>\n"
        table += "</thead>\n"
        table += "<tbody>\n"

        for row_values in self._rows:
            table += "<tr>\n"

            for cell_value in row_values:
                # To allow Markdown content inside table cells, a blank line is required
                # before and after the cell content.
                # See https://spec.commonmark.org/0.31.2/#html-blocks
                table += "<td>\n"
                table += "\n"
                table += f"{cell_value}\n"
                table += "\n"
                table += "</td>\n"

            table += "</tr>\n"

        table += "</tbody>\n"
        table += "</table>\n"

        return table

# pylint: disable-next=too-few-public-methods
class BulletList(MarkdownElement):
    """Unordered Markdown list block element.
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
        # lobster-trace: SwRequirements.sw_req_markdown_list
        """Render the unordered list.
        The values will be automatically escaped for Markdown if necessary.

        Returns:
            str: Markdown list
        """
        list_str = ""

        for value_raw in self._values:
            value = value_raw

            if self._escape is True:  # Escape the value if necessary.
                value = MarkdownText.escape(value)

            list_str += f"- {value}\n"

        return list_str

# pylint: disable-next=too-few-public-methods
class Image(MarkdownElement):
    """Markdown image / diagram link block element.
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
        # lobster-trace: SwRequirements.sw_req_markdown_image
        """Render the image link.
        The caption will be automatically escaped for Markdown if necessary.

        Returns:
            str: Markdown diagram link
        """
        caption_raw = self._caption

        if self._escape is True:
            caption_raw = MarkdownText.escape(self._caption)

        # Allowed are absolute and relative to source paths.
        file_name = os.path.normpath(self._file_name)

        return f"![{caption_raw}]({file_name})\n"

# pylint: disable-next=too-few-public-methods
class RawText(MarkdownElement):
    """Raw Markdown text block element passed through unchanged.
    """

    def __init__(self, text: str) -> None:
        """Initialize the raw text element.

        Args:
            text (str): Raw Markdown text
        """
        self._text = text

    def render(self) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """Render the raw text.

        Returns:
            str: Raw Markdown text
        """
        return self._text

# Functions ********************************************************************

# Main *************************************************************************
