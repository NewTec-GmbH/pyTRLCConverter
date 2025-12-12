"""Project specific docx converter functions.

    Author: Norbert Schulz (norbert.schulz@newtec.de)
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
from typing import Any

# pylint: disable=import-error
from generic_rsl_docx_converter import GenericRslDocxConverter

# Variables ********************************************************************

# Classes **********************************************************************

# pylint: disable=too-few-public-methods
class ProjectDocxConverter(GenericRslDocxConverter):
    """Custom Project specific Docx format converter.
    """
    def __init__(self, args: Any) -> None:
        """
        Initialize the custom docx converter.

        Args:
            args (Any): The parsed program arguments.
        """
        super().__init__(args)

        # Set project specific record handlers for the converter.
        self._set_project_record_handlers(
           {
                "Info": self._convert_record_object_info,
                "Image": self._convert_record_object_image,
                "PlantUML": self._convert_record_object_plantuml
           }
        )

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert into project specific docx format."

# Functions ********************************************************************

# Main *************************************************************************
