"""Markdown text helpers.
    Provides Markdown escaping and inline Markdown string builders.

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

# Variables ********************************************************************

# Classes **********************************************************************


class MarkdownText:
    """Utility class providing Markdown text escaping and inline element builders.
    """

    @staticmethod
    def escape(text: str) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_escape
        """
        Escapes the text to be used in a Markdown document.

        Args:
            text (str): Text to escape

        Returns:
            str: Escaped text
        """
        characters = ["\\", "`", "*", "_", "{", "}", "[", "]", "<", ">", "(", ")", "#", "+", "-", ".", "!", "|"]

        for character in characters:
            text = text.replace(character, "\\" + character)

        return text

    @staticmethod
    def lf2soft_return(text: str) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_soft_return
        """
        A single LF will be converted to backslash + LF.
        Use it for paragraphs, but not for headings or tables.

        Args:
            text (str): Text

        Returns:
            str: Handled text
        """
        return text.replace("\n", "\\\n")

    @staticmethod
    def link(text: str, url: str, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_link
        """
        Create a Markdown link.
        The text will be automatically escaped for Markdown if necessary.
        There will be no newline appended at the end.

        Args:
            text (str): Link text
            url (str): Link URL
            escape (bool): Escapes text (default: True).

        Returns:
            str: Markdown link
        """
        text_raw = text

        if escape is True:
            text_raw = MarkdownText.escape(text)

        return f"[{text_raw}]({url})"

    @staticmethod
    def colored_text(text: str, color: str, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_text_color
        """
        Create colored text in Markdown.
        The text will be automatically escaped for Markdown if necessary.
        There will be no newline appended at the end.

        Args:
            text (str): Text
            color (str): HTML color
            escape (bool): Escapes text (default: True).

        Returns:
            str: Colored text
        """
        text_raw = text

        if escape is True:
            text_raw = MarkdownText.escape(text)

        return f"<span style=\"{color}\">{text_raw}</span>"

# Functions ********************************************************************

# Main *************************************************************************
