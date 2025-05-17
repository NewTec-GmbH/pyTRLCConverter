"""Log verbose functionality.

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

import sys
import logging

# Variables ********************************************************************

_VERBOSE_ENABLED = False
logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

# Classes **********************************************************************

# Functions ********************************************************************

def is_verbose_enabled() -> bool:
    # lobster-trace: SwRequirements.sw_req_verbose_mode
    """Check if verbose mode is enabled.
    
    Returns:
        bool: True if verbose mode is enabled, False otherwise.
    """
    return _VERBOSE_ENABLED

def enable_verbose(enable : bool) -> None:
    # lobster-trace: SwRequirements.sw_req_verbose_mode
    """Enable or disable verbose mode.
    
    Args:
        enable (bool): True to enable verbose mode, False to disable it.
    """
    global _VERBOSE_ENABLED # pylint: disable=global-statement
    _VERBOSE_ENABLED = enable

def log_verbose(message : str) -> None:
    # lobster-trace: SwRequirements.sw_req_verbose_mode
    """Print a message if verbose mode is enabled.
    
    Args:
        message (str): The message to print.
    """
    if _VERBOSE_ENABLED:
        print(message)

def log_error(message : str, show_timestamp : str = False) -> None:
    """Prints an error and optionally a timestamp with it

    Args:
        message (str): The error message
        show_timestamp (bool, optional): Option to enable logging. Defaults to False.
    """
    if show_timestamp:
        logging.error(message)
    else:
        print(message, file=sys.stderr)


# Main *************************************************************************
