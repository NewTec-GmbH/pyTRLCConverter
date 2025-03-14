"""Project specific converter for testing purposes only.

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

from trlc.ast import Record_Object

from pyTRLCConverter.ret import Ret
from pyTRLCConverter.base_converter import BaseConverter

# Variables ********************************************************************

# Classes **********************************************************************


class SimpleConverter(BaseConverter):
    """
    Custom project specific converter for testing purposes only.
    
    It will print the section name, the record name and the description of the record.
    """

    @staticmethod
    def get_subcommand() -> str:
        """ Return subcommand token for this converter.

        Returns:
            str: subcomand argument token
        """
        return "simple"

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert TRLC files to simple format."

    def convert_section(self, section: str, level: int) -> Ret:
        """Process the given section item.

        Args:
            section (str): The section name
            level (int): The section indentation level

        Returns:
            Ret: Status
        """
        print(f"{section}\n")

        return Ret.OK

    def convert_record_object_generic(self, record: Record_Object, level: int) -> Ret:
        """Convert a record object generically.

        Args:
            record (Record_Object): The record object
            level (int): The record level

        Returns:
            Ret: Status
        """
        attributes = record.to_python_dict()

        description = attributes["description"]

        print(f"{record.name}")
        print(f"{description}")

        return Ret.OK

# Functions ********************************************************************

# Main *************************************************************************
