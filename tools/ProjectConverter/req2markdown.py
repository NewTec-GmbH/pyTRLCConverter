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
from pyTRLCConverter.base_converter import RecordsPolicy
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import Record_Object

# pylint: disable=wrong-import-order
from generic_rsl_markdown_converter import GenericRslMarkdownConverter

# Variables ********************************************************************

# Classes **********************************************************************


class ProjectMarkDownConverter(GenericRslMarkdownConverter):
    """Custom Project specific Markdown Converter.
    """

    def __init__(self, args: any) -> None:
        """
        Initialize the custom markdown converter.
        """
        super().__init__(args)

        # Set project specific record handlers for the converter.
        self._set_project_record_handlers(
           [
                ("Image", self._print_image),
                ("Info", self._print_info),
                ("PlantUML", self._print_plantuml),
                ("SwReq", self._print_sw_req),
                ("SwReqNonFunc", self._print_sw_req),
                ("SwConstraint", self._print_sw_constraint),
           ]
        )

        self._record_policy = RecordsPolicy.RECORD_SKIP_UNHANDLED

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert into project extended markdown format."

    def _print_sw_req(self, sw_req: Record_Object, level: int) -> Ret:
        """Prints the software requirement.

        Args:
            sw_req (Record_Object): Software requirement to print
            level (int): Current level of the record object
        """

        self._write_empty_line_on_demand()

        attribute_translation = {
            "description": "Description",
            "note": "Note",
            "verification_criteria": "Verification Criteria",
            "derived": "Derived"
        }

        return self._convert_record_object(sw_req, level, attribute_translation)

    def _print_sw_constraint(self, sw_constraint: Record_Object, level: int) -> Ret:
        """Prints the software constraint.

        Args:
            sw_constraint (Record_Object): Software constraint to print
            level (int): Current level of the record object
        """
        self._write_empty_line_on_demand()

        attribute_translation = {
            "description": "Description",
            "note": "Note",
            "derived": "Derived"
        }

        return self._convert_record_object(sw_constraint, level, attribute_translation)

# Functions ********************************************************************

# Main *************************************************************************
