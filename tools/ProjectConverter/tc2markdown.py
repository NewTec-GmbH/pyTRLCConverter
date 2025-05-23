"""Project specific Markdown converter functions.

    Author: Andreas Merkle (andreas.merkle@newtec.de)
"""

# pyTRLCConverter - A tool to convert TRLC files to specific formats.
# Copyright (c) 2024 - 2025 NewTec GmbH
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

# pylint: disable=import-error
from generic_rsl_markdown_converter import GenericRslMarkdownConverter

# Variables ********************************************************************

# Classes **********************************************************************

# pylint: disable=too-few-public-methods
class TestCaseMarkdownConverter(GenericRslMarkdownConverter):
    """Custom Project specific Markdown converter for test cases.
    """
    def __init__(self, args: any) -> None:
        """
        Initialize the custom Markdown converter.

        Args:
            args (any): The parsed program arguments.
        """
        super().__init__(args)

        # Set project specific record handlers for the converter.
        self._set_project_record_handlers(
           {
                "Image": self._print_image,
                "Info": self._print_info,
                "PlantUML": self._print_plantuml
           }
        )

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert test case definitions into project extended Markdown format."

# Functions ********************************************************************

# Main *************************************************************************
