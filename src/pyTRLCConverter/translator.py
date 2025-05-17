"""
This module implements the requirement attribute translator.

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
from typing import Dict, Optional
from pyTRLCConverter.logger import log_verbose

# Variables ********************************************************************

# Classes **********************************************************************

class Translator():
    # lobster-trace: SwRequirements.sw_req_translation
    """
    This class implements the requirement attribute translator.
    """

    def __init__(self):
        """
        Constructs the requirement attribute translator.
        """
        self._translation = {}

    def load(self, file_name: str) -> bool:
        """
        Load the trasnlation JSON file.

        Args:
            file_name (str): The name of the JSON file to load.

        Returns:
            bool: True if the file was loaded successfully, False otherwise.
        """
        status = False

        log_verbose(f"Loading translation file {file_name}.")

        # Load the JSON file
        try:
            with open(file_name, 'r', encoding="utf-8") as file:
                self._translation = json.load(file)

            status = True

        except FileNotFoundError as e:
            log_verbose(f"Failed to load file {file_name}: {e}")

        return status

    def get_translation(self, req_type_name: str) -> Optional[Dict]:
        """
        Get the translation for a specific requirement type.

        Args:
            req_type_name (str): The name of the requirement type.

        Returns:
            Optional[Dict]: The translation dictionary for the requirement type, or None if not found.
        """
        translation = None

        if req_type_name in self._translation:
            translation = self._translation[req_type_name]

        return translation


    def translate(self, req_type_name: str, attr_name: str) -> str:
        """
        Translate the requirement attribute.

        Args:
            req_type_name (str): The name of the requirement type.
            attr_name (str): The name of the attribute to translate.

        Returns:
            str: The translated attribute name.
        """
        translation = attr_name

        if req_type_name not in self._translation:
            log_verbose(f"Failed to translate {req_type_name}: No translation available.")

        else:

            if attr_name not in self._translation[req_type_name]:
                log_verbose(f"Failed to translate {req_type_name}.{attr_name}: No translation available.")
            else:
                translation = self._translation[req_type_name][attr_name]

        return translation

# Functions ********************************************************************


# Main *************************************************************************
