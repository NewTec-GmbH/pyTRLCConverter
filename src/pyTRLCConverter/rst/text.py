"""reStructuredText text helpers.
    Provides reStructuredText escaping and inline reStructuredText string builders.

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

# Variables ********************************************************************

# Classes **********************************************************************


class RstText:
    """Utility class providing reStructuredText escaping and inline element builders.
    """

    @staticmethod
    def escape(text: str) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_escape
        """
        Escapes the text to be used in a reStructuredText document.

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
    def link(text: str, target: str, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_link
        """
        Create a reStructuredText cross-reference.
        The text will be automatically escaped for reStructuredText if necessary.
        There will be no newline appended at the end.

        Args:
            text (str): Link text
            target (str): Cross-reference target
            escape (bool): Escapes text (default: True).

        Returns:
            str: reStructuredText cross-reference
        """
        text_raw = text

        if escape is True:
            text_raw = RstText.escape(text)

        return f":ref:`{text_raw} <{target}>`"

    @staticmethod
    def role(text: str, role: str, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_role
        """
        Create role text in reStructuredText.
        The text will be automatically escaped for reStructuredText if necessary.
        There will be no newline appended at the end.

        Args:
            text (str): Text
            role (str): Role
            escape (bool): Escapes text (default: True).

        Returns:
            str: Text with role
        """
        text_raw = text

        if escape is True:
            text_raw = RstText.escape(text)

        return f":{role}:`{text_raw}`"

# Functions ********************************************************************

# Main *************************************************************************
