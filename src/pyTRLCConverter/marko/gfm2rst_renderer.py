"""reStructuredText renderer for Marko.
    It is used to convert GitHub Flavored Markdown AST to reStructuredText format.

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

from __future__ import annotations
from typing import TYPE_CHECKING, Any, cast
from pyTRLCConverter.marko.md2rst_renderer import Md2RstRenderer

if TYPE_CHECKING:
    from . import block, inline

# Variables ********************************************************************

# Classes **********************************************************************

# pylint: disable-next=too-many-public-methods
class Gfm2RstRenderer(Md2RstRenderer):
    # lobster-trace: SwRequirements.sw_req_rst_render_gfm
    """
    Renderer for reStructuredText output.
    It is used to convert GitHub Flavored Markdown to reStructuredText format.
    """

    # Inherit all CommonMark rendering behavior from Md2RstRenderer and override only GFM additions.

    def render_list_item(self, element: block.ListItem, marker="-") -> str:
        """
        Renders a list item element.

        Args:
            element (block.ListItem): The list item element to render.
            marker (str, optional): The marker to use for the list item. Defaults to "*".

        Returns:
            str: The rendered list item as a string.
        """
        indent = 2
        content = self.render_children(element)

        # GitHub Flavored Markdown task-list items expose a "checked" flag in the paragraph node.
        # Prefix the rendered item text to preserve the task state in reStructuredText output.
        if 0 < len(element.children):
            first_child = element.children[0]
            checked = getattr(first_child, "checked", None)
            if checked is True:
                content = "[x] " + content.lstrip()
            elif checked is False:
                content = "[ ] " + content.lstrip()

        return f"{' ' * indent * (self._list_indent_level - 1)}{marker} {content}"

    def render_table(self, element: Any) -> str:
        """Renders a GitHub Flavored Markdown table as a reStructuredText grid table.

        Args:
            element (Any): The GFM table element.

        Returns:
            str: The rendered grid table as a string.
        """
        if not element.children:
            return ""

        header_row = element.children[0]
        body_rows = element.children[1:]

        header_values = [self.render_children(cell).strip() for cell in header_row.children]
        row_values = []

        for row in body_rows:
            row_values.append([self.render_children(cell).strip() for cell in row.children])

        return self._rst_create_grid_table(header_values, row_values)

    def render_table_row(self, element: Any) -> str:
        """Renders a GitHub Flavored Markdown table row.

        Args:
            element (Any): The table row element.

        Returns:
            str: The rendered row as a string.
        """
        return " | ".join(self.render_children(cell).strip() for cell in element.children)

    def render_table_cell(self, element: Any) -> str:
        """Renders a GitHub Flavored Markdown table cell.

        Args:
            element (Any): The table cell element.

        Returns:
            str: The rendered table cell as a string.
        """
        return self.render_children(element)

    def render_strikethrough(self, element: Any) -> str:
        """Renders a GitHub Flavored Markdown strikethrough element.

        Args:
            element (Any): The strikethrough element.

        Returns:
            str: The rendered strikethrough text.
        """
        return f"~~{self.render_children(element)}~~"

    def render_url(self, element: Any) -> str:
        """Renders a GitHub Flavored Markdown URL element.

        Args:
            element (Any): The URL element.

        Returns:
            str: The rendered URL as an RST link.
        """
        return self.render_link(cast("inline.Link", element))

    @staticmethod
    def _rst_table_append_border(char: str, max_widths: list[int]) -> str:
        """
        Appends a table border line for the grid table.

        Args:
            char (str): The character to use for the border line.
            max_widths (list[int]): The maximum widths of the table columns.

        Returns:
            str: The rendered border line as a string.
        """
        return "+" + "+".join(char * (width + 2) for width in max_widths) + "+\n"

    @staticmethod
    def _rst_table_append_row(values: list[str], max_widths: list[int]) -> str:
        """
        Appends a table row for the grid table.

        Args:
            values (list[str]): The values for the row.
            max_widths (list[int]): The maximum widths of the table columns.

        Returns:
            str: The rendered row as a string.
        """
        padded = [f" {value.ljust(max_widths[index])} " for index, value in enumerate(values)]

        return "|" + "|".join(padded) + "|\n"

    @staticmethod
    def _rst_create_grid_table(headers: list[str], rows: list[list[str]]) -> str:
        """Create a reStructuredText grid table.

        Args:
            headers (list[str]): Header row values.
            rows (list[list[str]]): Body row values.

        Returns:
            str: The rendered grid table including trailing newline.
        """
        if len(headers) == 0:
            return ""

        max_widths = [len(value) for value in headers]

        for row in rows:
            for index, value in enumerate(row):
                max_widths[index] = max(max_widths[index], len(value))

        table = ""
        table += Gfm2RstRenderer._rst_table_append_border("-", max_widths)
        table += Gfm2RstRenderer._rst_table_append_row(headers, max_widths)
        table += Gfm2RstRenderer._rst_table_append_border("=", max_widths)

        for row in rows:
            table += Gfm2RstRenderer._rst_table_append_row(row, max_widths)
            table += Gfm2RstRenderer._rst_table_append_border("-", max_widths)

        table += "\n"

        return table

# Functions ********************************************************************

# Main *************************************************************************
