"""
This module implements the persistent ReqIF identifier store.

The store keeps the identifiers of ReqIF Identifiable elements immutable across
consecutive exports by persisting a mapping from a stable logical key to the
generated identifier in a JSON file.

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
from pyTRLCConverter.logger import log_error, log_verbose

# Variables ********************************************************************

# Classes **********************************************************************


class ReqifIdentifierStore():
    """Persistent store mapping stable logical keys to immutable ReqIF identifiers.

    On the initial conversion the store is empty and identifiers are generated on
    demand. The mapping can be persisted to a JSON file and loaded again on
    subsequent conversions so that already known elements keep their identifiers
    while new elements receive new identifiers.
    """

    SCHEMA_VERSION = 1

    def __init__(self) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_immutable
        """Construct an empty identifier store."""
        self._identifiers = {}
        self._next_id = 1

    def load(self, file_name: str) -> bool:
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_init
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_reuse
        """Load the identifier store from a JSON file.

        A missing file is treated as the initial conversion and leaves the store
        empty without reporting an error.

        Args:
            file_name (str): The name of the JSON file to load.

        Returns:
            bool: True if loading succeeded or the file does not exist yet, False on error.
        """
        status = True

        log_verbose(f"Loading ReqIF identifier store {file_name}.")

        try:
            with open(file_name, "r", encoding="utf-8") as file:
                data = json.load(file)

            self._identifiers = dict(data.get("identifiers", {}))
            self._next_id = int(data.get("next_id", len(self._identifiers) + 1))

        except FileNotFoundError:
            log_verbose(f"ReqIF identifier store {file_name} does not exist yet; starting empty.")

        except (OSError, IOError, ValueError) as exc:
            log_error(f"Failed to load ReqIF identifier store {file_name}: {exc}")
            status = False

        return status

    def get_or_create(self, key: str, prefix: str) -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_immutable
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_reuse
        """Return the stored identifier for the given key or create a new immutable one.

        A new identifier is built from the given prefix and a monotonic counter that
        never reuses a number, so identifiers stay unique and stable.

        Args:
            key (str): Stable logical key identifying the ReqIF element.
            prefix (str): Identifier prefix (e.g. ``"spec-object"`` or ``"hierarchy"``).

        Returns:
            str: The immutable identifier associated with the key.
        """
        identifier = self._identifiers.get(key)

        if identifier is None:
            identifier = f"{prefix}-{self._next_id}"
            self._next_id += 1
            self._identifiers[key] = identifier

        return identifier

    def save(self, file_name: str) -> bool:
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_init
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_reuse
        """Persist the identifier store to a JSON file.

        Args:
            file_name (str): The name of the JSON file to write.

        Returns:
            bool: True if the file was written successfully, False otherwise.
        """
        status = True

        log_verbose(f"Saving ReqIF identifier store {file_name}.")

        data = {
            "version": ReqifIdentifierStore.SCHEMA_VERSION,
            "next_id": self._next_id,
            "identifiers": self._identifiers
        }

        try:
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, sort_keys=True)

        except (OSError, IOError) as exc:
            log_error(f"Failed to save ReqIF identifier store {file_name}: {exc}")
            status = False

        return status

# Functions ********************************************************************


# Main *************************************************************************
