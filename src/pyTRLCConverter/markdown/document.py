"""Markdown document container.
    Collects Markdown block elements and renders them into a single string.
    Consecutive blocks are separated by a single blank line, the first block
    has no leading blank line and the document ends with a single newline.

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
from typing import List
from pyTRLCConverter.markdown.element import MarkdownElement

# Variables ********************************************************************

# Classes **********************************************************************


class MarkdownDocument:
    """In-memory Markdown document built from block elements.
    """

    def __init__(self) -> None:
        """Initialize an empty Markdown document.
        """
        self._elements: List[MarkdownElement] = []

    def add(self, element: MarkdownElement) -> None:
        # lobster-trace: SwRequirements.sw_req_markdown
        """Append a block element to the document.

        Args:
            element (MarkdownElement): Block element to append.
        """
        self._elements.append(element)

    def is_empty(self) -> bool:
        # lobster-trace: SwRequirements.sw_req_markdown
        """Return whether the document has no elements yet.

        Returns:
            bool: True if no element has been added, otherwise False.
        """
        return len(self._elements) == 0

    def render(self) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown
        """Render the whole document.
        Blocks are separated by a single blank line, the first block has no
        leading blank line and the document ends with a single newline.

        Returns:
            str: Rendered Markdown document
        """
        return "\n".join(element.render() for element in self._elements)

# Functions ********************************************************************

# Main *************************************************************************
