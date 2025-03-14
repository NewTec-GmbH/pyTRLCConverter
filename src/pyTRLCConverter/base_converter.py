""" Converter base class which does the argparser handling and provides helper functions.

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
import sys
from enum import Enum
from pyTRLCConverter.abstract_converter import AbstractConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************


class RecordsPolicy(Enum):
    """
    Enum class to define policies for handling records during conversion.

    Attributes:
        RECORD_CONVERT_ALL (int): Convert all records, including undefined ones
                                  using convert_record_object_generic().
        RECORD_SKIP_UNDEFINED (int): Skip records types that are not linked to a handler.
    """
    RECORD_CONVERT_ALL= 1
    RECORD_SKIP_UNDEFINED = 2


class BaseConverter(AbstractConverter):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """
    Base converter with empty method implementations and helper functions 
    for subclassing converters.
    """
    # Converter specific sub parser
    _parser = None

    # Default value used to replace empty attribute values.
    EMPTY_ATTRIBUTE_DEFAULT = "N/A"

    def __init__(self, args: any) -> None:
        """
        Initializes the converter with the given arguments.

        Args:
            args (any): The parsed program arguments.
        """

        # Store the command line arguments.
        self._args = args

        # Record handler dictionary for project specific record handlers.
        self._record_handler_dict = {}  # type: dict[str, callable]

        # Set the default policy for handling records.
        self._record_policy = RecordsPolicy.RECORD_CONVERT_ALL

        # Set the default value for empty attributes.
        self._empty_attribute_value = BaseConverter.EMPTY_ATTRIBUTE_DEFAULT

    @classmethod
    def register(cls, args_parser: any) -> None:
        """Register converter specific argument parser.

        Args:
            args_parser (any): Argument parser
        """
        BaseConverter._parser = args_parser.add_parser(
            cls.get_subcommand(),
            help=cls.get_description()
        )
        BaseConverter._parser.set_defaults(converter_class=cls)

    def begin(self) -> Ret:
        """ Begin the conversion process.

        Returns:
            Ret: Status
        """
        return Ret.OK

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

        # check for a specific record handler
        record_handler = self._record_handler_dict.get(record.n_typ.name)
        if callable(record_handler):
            result = record_handler(record, level)

            # Don't trust project specific handlers to return a valid status.
            if not isinstance(result, Ret):
                print(f"Invalid return value from record handler for record {record.n_typ.name}.", file=sys.stderr)
                result = Ret.ERROR

        elif self._record_policy == RecordsPolicy.RECORD_CONVERT_ALL:
            result = self.convert_record_object_generic(record, level)
        else:
            result = Ret.OK

        return result

    def finish(self):
        """Finish the conversion process.
        """
        return Ret.OK

    # helpers **************************************************************

    def convert_record_object_generic(self, record: Record_Object, level: int) -> Ret:
        """Convert a record object generically.

        Args:
            record (Record_Object): The record object
            level (int): The record level

        Returns:
            Ret: Status
        """

        raise NotImplementedError

    def _set_project_record_handler(self, record_type: str, handler: callable) -> None:
        """Set a project specific record handler.

        Args:
            record_type (str): The record type
            handler (callable): The handler function
        """
        self._record_handler_dict[record_type] = handler

    def _set_project_record_handlers(self, handlers: dict[str, callable]) -> None:
        """Set project specific record handlers.

        Args:
            handler (dict[str, callable]): List of record type and handler function tuples
        """
        for record_type, handler in handlers.items():
            self._set_project_record_handler(record_type, handler)

    def _get_attribute(self, record: Record_Object, attribute_name: str) -> str:
        """Get the attribute value from the record object.
            If the attribute is not found or empty, return the default value.

        Args:
            record (Record_Object): The record object
            attribute_name (str): The attribute name to get the value from.

        Returns:
            str: The attribute value
        """
        record_dict = record.to_python_dict()
        attribute_value = record_dict[attribute_name]

        if attribute_value is None:
            attribute_value = self._empty_attribute_value
        elif attribute_value == "":
            attribute_value = self._empty_attribute_value

        return attribute_value

# Functions ********************************************************************

# Main *************************************************************************
