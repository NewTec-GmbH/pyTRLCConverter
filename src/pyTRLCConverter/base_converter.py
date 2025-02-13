""" Converter base class which does the argparser handling and provides helper functions.

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
import os
from typing import Optional
from pyTRLCConverter.abstract_converter import AbstractConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import Record_Object

class BaseConverter(AbstractConverter):
    """
    Base converter with empty method implementations and helper functions 
    for subclassing converters.
    """
    # converter specific sub parser
    _parser = None

    def __init__(self, args: any) -> None:
        """
        Initializes the converter with the given arguments.

        Args:
            args: The parsed program arguments.
        """
        self._args = args

    @staticmethod
    def register(args_parser, cls : type) -> None:
        """Register converter specific argument parser.

        Args:
            args_parser (object): Argument parser
            cls (type): The class type to register
        """
        BaseConverter._parser = args_parser.add_parser(
            cls.get_subcommand(),
            help=cls.get_description()
        )
        BaseConverter._parser.set_defaults(converter_class=cls)

    def enter_file(self, file_name: str) -> Ret:
        """Enter a file.

        Args:
            file_name (str): File name

        Returns:
            Ret: Status
        """
        return Ret.OK

    def leave_file(self, file_name: str) -> Ret:
        """Leave a file.

        Args:
            file_name (str): File name
        
        Returns:
            Ret: Status
        """
        return Ret.OK

    def convert_section(self, section: str, level: int) -> Ret:
        """Process the given section item.

        Args:
            section (str): The section name
            level (int): The section indentation level
        
        Returns:
            Ret: Status
        """
        return Ret.OK

    def convert_record_object(self, record: Record_Object, level: int) -> Ret:
        """Process the given record object.

        Args:
            record (Record_Object): The record object
            level (int): The record level
        
        Returns:
            Ret: Status
        """
        return Ret.OK

    def finish(self):
        """Finish the conversion process.
        """
        return Ret.OK

    # helpers **************************************************************

    def _locate_file(self, file_path: str) -> Optional[str]:
        """
        Locate a file by searching through the sources list if it 
        cannot be accessed by the given file_path.

        Args:
            file_path (str): The name of the file to locate.

        Returns:
            str: The full path to the located file if found, otherwise None.
        """

        calculated_path = None

        # Is the path to the diagram invalid?
        if os.path.isfile(file_path) is False:
            # Maybe the path is relative to one of the source paths.
            for src_item in self._args.source:
                if os.path.isdir(src_item):
                    full_file_path = os.path.join(src_item, file_path)

                    if os.path.isfile(full_file_path) is False:
                        full_file_path = None
                    else:
                        calculated_path = full_file_path
                        break

        return calculated_path
