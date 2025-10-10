""" Provides the render configuration to all converters.

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
import json
import re

from pyTRLCConverter.logger import log_verbose

# Variables ********************************************************************

# Classes **********************************************************************


class RenderConfig():
    """Render configuration provider.
    """

    FORMAT_SPECIFIER_PLAIN = "plain"
    FORMAT_SPECIFIER_MD = "md"
    FORMAT_SPECIFIER_RST = "rst"

    def __init__(self):
        """Constructs the render configuration provider.
        """
        # The render configuration as dict.
        #
        # Example in JSON format:
        # { "renderCfg": [{ "package": "XX", "type": "YY", "attribute": "ZZ", "format": "md" }] }
        self._cfg = {}

    def load(self, file_name: str) -> bool:
        """Loads the render configuration from the given file.
        
        Args:
           file_name (str): Path to the render configuration file.
           
        Returns:
           bool: True if successful, False otherwise.
        """
        status = False

        log_verbose(f"Loading render configuration {file_name}.")

        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                self._cfg = json.load(f)
            status = True

        except FileNotFoundError:
            pass

        return status

    def _is_package_match(self, item: dict, trlc_package: str) -> bool:
        """Checks if the given TRLC package matches the package pattern in the given item.

        Args:
            item (dict): Single render configuration item.
            trlc_package (str): The TRLC package.

        Returns:
            bool: If the given TRLC package matches the package pattern in the given item.
        """
        it_matches = False

        if "package" in item:
            if re.match(item["package"], trlc_package):
                it_matches = True

        return it_matches

    def _is_type_match(self, item: dict, trlc_type: str) -> bool:
        """Checks if the given TRLC type matches the type pattern in the given item.

        Args:
            item (dict): Single render configuration item.
            trlc_type (str): The TRLC type.

        Returns:
            bool: If the given TRLC type matches the type pattern in the given item.
        """
        it_matches = False

        if "type" in item:
            if re.match(item["type"], trlc_type):
                it_matches = True

        return it_matches

    def _is_type_attribute_match(self, item: dict, trlc_type_attribute: str) -> bool:
        """Checks if the given TRLC type attribute matches the type attribute pattern in the given item.

        Args:
            item (dict): Single render configuration item.
            trlc_type (str): The TRLC type attribute.

        Returns:
            bool: If the given TRLC type attribute matches the type attribute pattern in the given item.
        """
        it_matches = False

        if "attribute" in item:
            if re.match(item["attribute"], trlc_type_attribute):
                it_matches = True

        return it_matches

    def get_format_specifier(self, trlc_package: str, trlc_type: str, trlc_type_attribute: str) -> str:
        """Returns the format specifier for the given TRLC package, type and attribute.

        Args:
            trlc_package (str): The TRLC package.
            trlc_type (str): The TRLC type.
            trlc_type_attribute (str): The TRLC type attribute.

        Returns:
            str: The format specifier for the given TRLC package, type and attribute.
        """
        format_specifier = ""

        if "renderCfg" in self._cfg:
            for item in self._cfg["renderCfg"]:
                match_list = []

                match_list.append(self._is_package_match(item, trlc_package))
                match_list.append(self._is_type_match(item, trlc_type))
                match_list.append(self._is_type_attribute_match(item, trlc_type_attribute))

                # All of the available ones must match!
                if all(match_list):
                    if "format" in item:
                        format_specifier = item["format"]

        return format_specifier

    def is_format_plain(self, trlc_package: str, trlc_type: str, trlc_type_attribute: str) -> bool:
        """Checks if the given TRLC package, type and attribute should be rendered in plain text format.

        Args:
            trlc_package (str): The TRLC package.
            trlc_type (str): The TRLC type.
            trlc_type_attribute (str): The TRLC type attribute.
        
        Returns:
           bool: True if the given TRLC attribute has plain text format, otherwise False.
        """
        return self.get_format_specifier(trlc_package, trlc_type, trlc_type_attribute) == self.FORMAT_SPECIFIER_PLAIN

    def is_format_md(self, trlc_package: str, trlc_type: str, trlc_type_attribute: str) -> bool:
        """Checks if the given TRLC package, type and attribute should be rendered in markdown format.

        Args:
            trlc_package (str): The TRLC package.
            trlc_type (str): The TRLC type.
            trlc_type_attribute (str): The TRLC type attribute.
        
        Returns:
           bool: True if the given TRLC attribute has Markdown format, otherwise False.
        """
        return self.get_format_specifier(trlc_package, trlc_type, trlc_type_attribute) == self.FORMAT_SPECIFIER_MD

    def is_format_rst(self, trlc_package: str, trlc_type: str, trlc_type_attribute: str) -> bool:
        """Checks if the given TRLC package, type and attribute should be rendered in reStructuredText format.

        Args:
            trlc_package (str): The TRLC package.
            trlc_type (str): The TRLC type.
            trlc_type_attribute (str): The TRLC type attribute.

        Returns:
           bool: True if the given TRLC attribute has reStructuredText format, otherwise False.
        """
        return self.get_format_specifier(trlc_package, trlc_type, trlc_type_attribute) == self.FORMAT_SPECIFIER_RST

# Functions ********************************************************************

# Main *************************************************************************
