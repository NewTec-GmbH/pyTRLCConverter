""" Provides the import filter configuration for the initial ReqIF import.

    The import filter restricts which ReqIF spec-object types are imported and which
    attributes are dropped, matched against the ReqIF long names.

    Author: Andreas Merkle (andreas.merkle@newtec.de)
"""

# pyTRLCConverter - A tool to convert TRLC files to specific formats.
# Copyright (c) 2024 - 2026 NewTec GmbH
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


class ImportFilter():
    """Import filter provider for the initial ReqIF import.

    Two independent filters are supported, matched against the ReqIF long names:

    - ``includeTypes``: a list of regex patterns; if present and non-empty, only spec-object
      types whose long name matches one of the patterns are imported.
    - ``exclude``: a list of ``(type, attribute)`` regex items; a matching attribute is dropped.
      A missing key in an item matches any value.
    """

    def __init__(self):
        """Constructs a permissive import filter (imports everything).
        """
        # The import filter as dict.
        #
        # Example in JSON format:
        # { "includeTypes": ["Requirement"], "exclude": [{ "type": ".*", "attribute": "InternalNote" }] }
        self._cfg = {}

    def load(self, file_name: str) -> bool:
        """Loads the import filter from the given file.

        Args:
            file_name (str): Path to the import filter file.

        Returns:
            bool: True if successful, False otherwise.
        """
        status = False

        log_verbose(f"Loading import filter {file_name}.")

        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                self._cfg = json.load(f)
            status = True

        except FileNotFoundError:
            pass

        return status

    def is_type_included(self, type_long_name: str) -> bool:
        """Checks whether a spec-object type shall be imported.

        Args:
            type_long_name (str): The ReqIF spec-object type long name.

        Returns:
            bool: True if the type shall be imported, otherwise False.
        """
        include_patterns = self._cfg.get("includeTypes", [])
        included = True

        if include_patterns:
            included = any(re.match(pattern, type_long_name) is not None for pattern in include_patterns)

        return included

    def is_attribute_excluded(self, type_long_name: str, attribute_long_name: str) -> bool:
        """Checks whether an attribute shall be dropped from the import.

        Args:
            type_long_name (str): The ReqIF spec-object type long name.
            attribute_long_name (str): The ReqIF attribute long name.

        Returns:
            bool: True if the attribute shall be dropped, otherwise False.
        """
        excluded = False

        for item in self._cfg.get("exclude", []):
            if (self._is_pattern_match(item, "type", type_long_name)
                    and self._is_pattern_match(item, "attribute", attribute_long_name)):
                excluded = True
                break

        return excluded

    @staticmethod
    def _is_pattern_match(item: dict, key: str, value: str) -> bool:
        """Checks whether the value matches the regex pattern stored under key in the item.

        A missing key is treated as a wildcard that matches any value.

        Args:
            item (dict): Single filter item.
            key (str): The item key holding the regex pattern (e.g. "type").
            value (str): The value to match against the pattern.

        Returns:
            bool: True if the value matches the pattern or the key is absent, otherwise False.
        """
        it_matches = True

        if key in item:
            it_matches = re.match(item[key], value) is not None

        return it_matches


# Functions ********************************************************************

# Main *************************************************************************
