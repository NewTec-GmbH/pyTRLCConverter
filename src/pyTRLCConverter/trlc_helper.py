"""TRLC helper functions.

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
import os
from typing import Union, Optional
from trlc.errors import Message_Handler
from trlc.trlc import Source_Manager
from trlc.ast import Array_Aggregate, Expression, Record_Object
from pyTRLCConverter.logger import log_verbose

# Variables ********************************************************************

# Classes **********************************************************************

class TrlcAstWalker():
    # lobster-trace: SwRequirements.sw_req_markdown
    # lobster-trace: SwRequirements.sw_req_rst
    """
    This class helps to walk through the TRLC AST. It uses a dispatcher map to handle
    the different AST nodes.

    It contains three dispatcher maps: begin, process and finish.
    
    The begin map is used to handle the node when it is entered, the process map is used to
    handle the node when it is processed and the finish map is used to handle the node when
    it is finished.
    
    The dispatcher map is a dictionary with the type name as key and the handler as value.

    By default the walker contains a dispatcher map only for the Array_Aggregate node. The other
    nodes are handled by the other dispatcher. If no other dispatcher is set, the node is
    converted to a string.
    """
    def __init__(self) -> None:
        self._dispatcher_map_begin = {}
        self._dispatcher_map_process = {
            Array_Aggregate: self._on_array_aggregate
        }
        self._dispatcher_map_finish = {}
        self._other_dispatcher = None

    def walk(self, expression: Expression) -> Union[list[str],str]:
        """
        Walk through the TRLC AST.

        Args:
            expression (Expression): The AST node.

        Returns:
            Union[list[str],str]: The result of the walking as string or list of strings.
        """
        return self._on_general(expression)

    # pylint: disable=line-too-long
    def add_dispatcher(self, type_name: type, begin: Optional[callable], process: Optional[callable], finish: Optional[callable]) -> None:
        """
        Add a dispatcher to the walker.

        Args:
            type_name (type): The type name
            begin (Optional[callable]): The begin handler
            process (Optional[callable]): The process handler
            finish (Optional[callable]): The finish handler
        """
        if begin is not None:
            self._dispatcher_map_begin[type_name] = begin

        if process is not None:
            self._dispatcher_map_process[type_name] = process

        if finish is not None:
            self._dispatcher_map_finish[type_name] = finish

    def set_other_dispatcher(self, dispatcher: callable) -> None:
        """
        Set the other dispatcher. This dispatcher is called when no dispatcher is found for the node.

        Args:
            dispatcher (callable): The other dispatcher
        """
        self._other_dispatcher = dispatcher

    def _dispatch(self, dispatcher_map: dict, expression: Expression, handle_other: bool) -> Union[list[str],str]:
        """
        Dispatch the expression to the dispatcher map.

        Args:
            dispatcher_map (dict): The dispatcher map.
            expression (Expression): The AST node.
            handle_other (bool): If True, the other dispatcher is called when no dispatcher is found.

        Returns:
            Union[list[str],str]: The result of the dispatcher.
        """
        result = ""

        type_name = type(expression)

        if type_name in dispatcher_map:
            result = dispatcher_map[type_name](expression)
        elif handle_other is True:
            result = self._on_other(expression)

        return result

    def _on_array_aggregate(self, array_aggregate: Array_Aggregate) -> list[str]:
        """
        Handle the Array_Aggregate node.

        Args:
            array_aggregate (Array_Aggregate): The AST node.

        Returns:
            list[str]: The result of the handling.
        """
        result = []

        self._dispatch(self._dispatcher_map_begin, array_aggregate, False)

        for expression in array_aggregate.value:
            value_result = self._dispatch(self._dispatcher_map_process, expression, True)

            if isinstance(value_result, list):
                result.extend(value_result)
            else:
                result.append(value_result)

        self._dispatch(self._dispatcher_map_finish, array_aggregate, False)

        return result

    def _on_general(self, expression: Expression) -> Union[list[str],str]:
        """
        Handle the general case.

        Args:
            expression (Expression): The AST node.

        Returns:
            Union[list[str],str]: The result of the handling.
        """
        self._dispatch(self._dispatcher_map_begin, expression, False)
        result = self._dispatch(self._dispatcher_map_process, expression, True)
        self._dispatch(self._dispatcher_map_finish, expression, False)

        return result

    def _on_other(self, expression: Expression) -> Union[list[str],str]:
        """
        Handle the other case.

        Args:
            expression (Expression): The AST node.

        Returns:
            Union[list[str],str]: The result of the handling.
        """
        result = ""

        if self._other_dispatcher is not None:
            result = self._other_dispatcher(expression)
        else:
            result = expression.to_string()

        return result

# Functions ********************************************************************

def get_trlc_symbols(source_items, includes):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Get the TRLC symbol table by parsing the given folder.

    Args:
        source_items ([str]|str): One or more paths to folder with TRLC files \
                                  or a single path to a TRLC file.
        includes (str|None): Path for automatically file inclusion.

    Returns:
        Symbol_Table: TRLC symbol table
    """
    symbol_table = None

    # Create Source_Manager.
    mh = Message_Handler()
    sm = Source_Manager(mh)

    # Read all .rsl and .trlc files in the given directory.
    try:
        # Handle first the include folders, because the source folders may depend on them.
        if includes is not None:
            for folder in includes:
                log_verbose(f"Registering include folder: {folder}")
                sm.register_include(folder)

        for src_item in source_items:
            if os.path.isdir(src_item):
                log_verbose(f"Registering source folder: {src_item}")
                sm.register_directory(src_item)
            else:
                log_verbose(f"Registering source file: {src_item}")
                sm.register_file(src_item)

        symbol_table = sm.process()
    except AssertionError:
        pass

    return symbol_table

def is_item_file_name(item):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Check if the item is a file name.

    Args:
        item (str|tuple): The item to check.

    Returns:
        bool: True if the item is a file name, otherwise False.
    """
    return isinstance(item, str)

def is_item_section(item):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Check if the item is a section.

    Args:
        item (str|tuple): The item to check.

    Returns:
        bool: True if the item is a section, otherwise False.
    """
    return isinstance(item, tuple) and \
            len(item) == 2 and \
            isinstance(item[0], str) and \
            isinstance(item[1], int)

def is_item_record(item):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Check if the item is a record.

    Args:
        item (str|tuple): The item to check.

    Returns:
        bool: True if the item is a record, otherwise False.
    """
    return isinstance(item, tuple) and \
            len(item) == 2 and \
            isinstance(item[0], Record_Object) and \
            isinstance(item[1], int)

def get_file_dict_from_symbols(symbols):
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Get a dictionary with the file names and their content.

    Args:
        symbols (Symbol_Table): The TRLC symbols to dump.

    Returns:
        dict: A dictionary with the file names and their content.
    """
    file_dict = {}
    item_list = None

    if symbols is not None:
        for item in symbols.iter_record_objects_by_section():
            # Is item a file name?
            if is_item_file_name(item):
                file_dict[item] = []
                item_list = file_dict[item]

            else:
                item_list.append(item)

    return file_dict

# Main *************************************************************************
