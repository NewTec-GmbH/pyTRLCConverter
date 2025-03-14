"""This module provides version and author information.

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
import importlib.metadata as meta
import os
import sys
import toml

# Variables ********************************************************************

__version__ = "???"
__author__ = "???"
__email__ = "???"
__repository__ = "???"
__license__ = "???"

# Classes **********************************************************************

# Functions ********************************************************************

def resource_path(relative_path):
    # lobster-trace: SwRequirements.sw_req_version
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # pylint: disable=protected-access
        # pylint: disable=no-member
        base_path = sys._MEIPASS
    except Exception:  # pylint: disable=broad-except
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def init_from_metadata():
    # lobster-trace: SwRequirements.sw_req_version
    """Initialize dunders from importlib.metadata
    Requires that the package was installed.

    Returns:
        list: Tool related information
    """

    my_metadata = meta.metadata('pyTRLCConverter')

    return \
        my_metadata.get('Version', '???'), \
        my_metadata.get('Author', '???'), \
        my_metadata.get('Author-email', '???'), \
        my_metadata.get('Project-URL', 'repository, ???').replace("repository, ", ""), \
        my_metadata.get('License', '???')

def init_from_toml():
    # lobster-trace: SwRequirements.sw_req_version
    """Initialize dunders from pypackage.toml file

    Tried if package wasn't installed.

    Returns:
        list: Tool related information
    """

    toml_file = resource_path("pyproject.toml")
    data = toml.load(toml_file)

    return \
        data["project"]["version"], \
        data["project"]["authors"][0]["name"], \
        data["project"]["authors"][0]["email"], \
        data["project"]["urls"]["repository"], \
        data["project"]["license"]["text"]

# Main *************************************************************************

try:
    __version__, __author__, __email__, __repository__, __license__ = init_from_metadata()

except meta.PackageNotFoundError:
    __version__, __author__, __email__, __repository__, __license__ = init_from_toml()
