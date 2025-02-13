"""Abstract converter interface which all implementations must fullfill.

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
from abc import ABC, abstractmethod
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************

class AbstractConverter(ABC):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Abstract converter interface.
    """
    @staticmethod
    def register(args_parser, cls: type) -> None:
        """Register converter specific argument parser.

        Args:
            args_parser (object): Argument parser
            cls (type):  The class type to use
        """
        raise NotImplementedError

    @abstractmethod
    def enter_file(self, file_name : str) -> None:
        """Enter a file.

        Args:
            file_name (str): File name
        """
        raise NotImplementedError

    @abstractmethod
    def leave_file(self, file_name : str) -> None:
        """Leave a file.

        Args:
            file_name (str): File name
        """
        raise NotImplementedError

    @abstractmethod
    def convert_section(self, section: str, level: int) -> Ret:
        """ Process the given section item.

        Args:
            section (str): The section name
            level (int): The section indentation level
        
        Returns:
            Ret: Status
        """
        raise NotImplementedError

    @abstractmethod
    def convert_record_object(self, record : Record_Object, level: int ) -> Ret:
        """ Process the given  record object
        
        Args:
            record (Record_Object): The record object
            level (int): The record indentation level

        Returns:
            Ret: Status
        """
        raise NotImplementedError

    @abstractmethod
    def finish(self) -> Ret:
        """ Finish the conversion process.

        Returns:
            Ret: Status
        """
        raise NotImplementedError

    @staticmethod
    def get_subcommand() -> str:
        """ Return subcommand token for this converter.

        Returns:
            str: subcomand argument token
        """
        raise NotImplementedError

    @staticmethod
    def get_description() -> str:
        """ Return converter description. 
        
        Returns:
            str: Converter description
        """
        raise NotImplementedError
