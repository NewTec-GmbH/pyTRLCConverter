""" Provides the export mapping configuration.

    The export mapping allows a project to keep attributes in its TRLC requirements
    that are deliberately not exported (internal-only attributes).

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


class ExportMap():
    """Export mapping provider.

    Determines which TRLC attributes shall be excluded from the export. The
    matching follows the same ``(package, type, attribute)`` regex-triplet style
    as the render configuration. A missing key in an exclude item matches any
    value, so a single attribute can be excluded across all packages and types.
    """

    def __init__(self):
        """Constructs the export mapping provider.
        """
        # The export mapping as dict.
        #
        # Example in JSON format:
        # { "exclude": [{ "package": ".*", "type": "SwReq", "attribute": "internal_note" }] }
        self._cfg = {}

    def load(self, file_name: str) -> bool:
        """Loads the export mapping from the given file.

        Args:
            file_name (str): Path to the export mapping file.

        Returns:
            bool: True if successful, False otherwise.
        """
        status = False

        log_verbose(f"Loading export mapping {file_name}.")

        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                self._cfg = json.load(f)
            status = True

        except FileNotFoundError:
            pass

        return status

    @staticmethod
    def _is_pattern_match(item: dict, key: str, value: str) -> bool:
        """Checks whether the given value matches the regex pattern stored under key in the item.

        A missing key is treated as a wildcard that matches any value.

        Args:
            item (dict): Single export mapping item.
            key (str): The item key holding the regex pattern (e.g. "package").
            value (str): The value to match against the pattern.

        Returns:
            bool: True if the value matches the pattern or the key is absent, otherwise False.
        """
        it_matches = True

        if key in item:
            it_matches = re.match(item[key], value) is not None

        return it_matches

    def is_excluded(self, trlc_package: str, trlc_type: str, trlc_type_attribute: str) -> bool:
        """Checks whether the given TRLC package, type and attribute shall be excluded from export.

        Args:
            trlc_package (str): The TRLC package.
            trlc_type (str): The TRLC type.
            trlc_type_attribute (str): The TRLC type attribute.

        Returns:
            bool: True if the attribute shall be excluded from export, otherwise False.
        """
        excluded = False

        for item in self._cfg.get("exclude", []):
            match_list = [
                self._is_pattern_match(item, "package", trlc_package),
                self._is_pattern_match(item, "type", trlc_type),
                self._is_pattern_match(item, "attribute", trlc_type_attribute)
            ]

            # All of the available ones must match!
            if all(match_list):
                excluded = True
                break

        return excluded


# Functions ********************************************************************

# Main *************************************************************************
