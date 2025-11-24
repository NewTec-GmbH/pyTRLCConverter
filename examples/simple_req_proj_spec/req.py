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
from typing import Optional, Any

from pyTRLCConverter.base_converter import RecordsPolicy
from pyTRLCConverter.ret import Ret

from pyTRLCConverter.markdown_converter import MarkdownConverter
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************


class CustomMarkdownConverter(MarkdownConverter):
    """Custom Project specific Markdown Converter.
    """

    def __init__(self, args: Any) -> None:
        """
        Initialize the custom markdown converter.

        Args:
            args (Any): The parsed program arguments.
        """
        super().__init__(args)

        # Set project specific record handlers for the converter.
        self._set_project_record_handlers(
           {
               "Requirement": self._print_req
           }
        )
        self._record_policy = RecordsPolicy.RECORD_SKIP_UNDEFINED

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert into project extended markdown format."

    def _print_req(self, req: Record_Object, level: int, _translation: Optional[dict]) -> Ret:
        """Prints the requirement.

        Args:
            req (Record_Object): Requirement to print.
            level (int): Current level of the record object.
            _translation (Optional[dict]): Translation dictionary for the record object.
                                            If None, no translation is applied.


        Returns:
            Ret: Status
        """

        self._write_empty_line_on_demand()

        # Translation file is not used, therefore _translation is not needed.
        # Its translated here, just for example.
        attribute_translation = {
            "description": "Description"
        }

        return self._convert_record_object(req, level, attribute_translation)

# Functions ********************************************************************

# Main *************************************************************************
