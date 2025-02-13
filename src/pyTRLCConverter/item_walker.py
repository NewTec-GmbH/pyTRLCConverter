"""
This module implements a TRLC items walker over the loaded model.

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
import sys
from trlc.ast import Symbol_Table

from pyTRLCConverter.abstract_converter import AbstractConverter
from pyTRLCConverter.log_verbose import log_verbose
from pyTRLCConverter.trlc_helper import get_file_dict_from_symbols, is_item_record, is_item_section
from pyTRLCConverter.ret import Ret

# Variables ********************************************************************

# Classes **********************************************************************
class ItemWalker: #pylint: disable=too-few-public-methods
    """
    A walker that traverses through the TRLC items in the given symbol table.

    Attributes:
        _converter (AbstractConverter): The converter used for processing items.
        _exclude_files (list): List of file paths to exclude from processing.
    """

    def __init__(self, args : any, converter : AbstractConverter) -> None:
        """
        Initializes the TrlcWalker with the given arguments and converter.

        Args:
            args (any): Arguments containing the exclude file paths.
            converter (AbstractConverter): The converter used for processing items.
        """
        self._converter = converter
        self._exclude_files = args.exclude

    def walk_symbols(self, symbol_table: Symbol_Table) -> Ret:
        """
        Walks through the items in the given symbol table and processes them.

        Args:
            symbol_table (Symbol_Table): The symbol table containing items to be walked through.

        Returns:
            Ret: Status of the walk operation.
        """
        result = Ret.OK
        skip_it = False

        files_dict = get_file_dict_from_symbols(symbol_table)
        for file_name, item_list in files_dict.items():
            if self._exclude_files is not None:
                for excluded_path in self._exclude_files:
                    if os.path.commonpath([excluded_path, file_name]) == excluded_path:
                        skip_it = True
                        break

            if skip_it is True:
                log_verbose(f"Skipping file {file_name}.")
            else:
                log_verbose(f"Processing file {file_name}.")
                result = self._walk_file(file_name, item_list)

            if result != Ret.OK:
                break

        self._converter.finish()

        return result

    def _walk_file(self, file_name: str, item_list: any) -> Ret:
        """
        Walks through the items in the given file.

        Args:
            file_name (str): The name of the file.
            item_list (any): The list of trlc items in the file.

        Returns:
            Ret: The result of the walk operation.
        """
        result = Ret.ERROR

        try:
            if Ret.OK == self._converter.enter_file(file_name):
                if Ret.OK == self._walk_items(item_list):
                    if Ret.OK == self._converter.leave_file(file_name):
                        result = Ret.OK

        except Exception as e: # pylint: disable=broad-except
            print(f"Error processing file {file_name}: {e}", file=sys.stderr)

        return result

    def _walk_items(self, item_list: list) -> Ret:
        """
        Walks through the given list of items.

        Args:
            item_list (list): The list of items to walk through.

        Returns:
            Ret: The result of the walk operation.
        """

        result = Ret.OK

        try:
            for item in item_list:
                result = self._visit_item(item)

                if result != Ret.OK:
                    break
        except Exception as e: # pylint: disable=broad-except
            print(f"Error processing item {item}: {e}", file=sys.stderr)
            result = Ret.ERROR

        return Ret.OK

    def _visit_item(self, item: any) -> Ret:
        """
        Visits the given item and processes it based on its type.

        Args:
            item (any): The item to visit.

        Returns:
            Ret: The result of the visit.
        """
        result = Ret.OK

        if is_item_section(item):
            result = self._converter.convert_section(item[0], item[1])
        elif is_item_record(item):
            result = self._converter.convert_record_object(item[0], item[1])
        else:
            print(f"Unrecognized item type {item}", file=sys.stderr)
            result = Ret.ERROR

        return result

# Functions ********************************************************************


# Main *************************************************************************
