""" Converter base class which does nothing (besides printing call names in verbose mode.)

    Author: Norbert Schulz (norbert.schulz@newtec.de)
"""

# pyTRLCConverter - A tool to convert PlantUML diagrams to image files.
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
from pyTRLCConverter.base_converter import BaseConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import Record_Object

# Classes **********************************************************************

class DumpConverter(BaseConverter):
    #lobster-trace: Dump.sw_req_ascii_conversion
    """Simple converter implemention that just dumps all items.
    """

    @staticmethod
    def get_subcommand() -> str:
        """ Return subcommand token for this converter.

        Returns:
            str: Parser subcommand token
        """
        return "dump"

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

        Returns:
            str: Converter description
        """
        return "Dump TRCL item list to console."

    def enter_file(self, file_name: str) -> Ret:
        """Enter a file.

        Args:
            file_name (str): File name

        Returns:
            Ret: Status
        """
        print(f"Entering file: {file_name}")
        return Ret.OK

    def leave_file(self, file_name: str) -> Ret:
        """Leave a file.

        Args:
            file_name (str): File name
        
        Returns:
            Ret: Status
        """
        print(f"Leaving file: {file_name}")
        return Ret.OK

    def convert_section(self, section: str, level: int) -> Ret:
        """Process the given section item.

        Args:
            section (str): The section name
            level (int): The section indentation level
        
        Returns:
            Ret: Status
        """
        print(f"{_blanks(level)}Section: {section} at level: {level}")
        return Ret.OK

    def convert_record_object(self, record: Record_Object, level: int) -> Ret:
        """Process the given record object.

        Args:
            record (Record_Object): The record object
            level (int): The record level
        
        Returns:
            Ret: Status
        """
        print(f"{_blanks(level)}Record {record.name}, Level: {level}")
        print(f"{record.dump(indent=level+1)}")
        return Ret.OK

    def finish(self)-> Ret:
        """Finish the conversion process.

         Returns:
            Ret: Status
        """
        print("Finishing conversion process.")
        return Ret.OK


def _blanks(count: int) -> str:
    """ Create a string with 'count' blanks.
     Args:
            count (int): number of blanks for string creation.
    Returns:
            str: string with count blanks.
    """
    return ' ' * count
