"""
This module implements the persistent ReqIF metadata store.

The ReqIF metadata store keeps the round-trip state of a ReqIF conversion in a JSON
file. It maps a stable logical key to the identifier of a ReqIF Identifiable element,
so identifiers stay immutable across consecutive exports, and it stores additional
ReqIF metadata (e.g. the specification-type identity) that is not itself an
identifier but must be reproduced on the round-trip.

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
from typing import Optional
from pyTRLCConverter.logger import log_error, log_verbose

# Variables ********************************************************************

# Metadata key of the preserved SPECIFICATION-TYPE identifier.
METADATA_SPECIFICATION_TYPE_IDENTIFIER = "specification-type-identifier"

# Metadata key of the preserved SPECIFICATION-TYPE long name.
METADATA_SPECIFICATION_TYPE_LONG_NAME = "specification-type-long-name"

# Classes **********************************************************************


class ReqifMetaData():
    """Persistent ReqIF metadata store.

    Maps stable logical keys to immutable ReqIF identifiers and holds additional
    ReqIF metadata values. On the initial conversion the store is empty and
    identifiers are generated on demand. The store can be persisted to a JSON file
    and loaded again on subsequent conversions so that already known elements keep
    their identifiers and metadata while new elements receive new identifiers.
    """

    SCHEMA_VERSION = 2

    def __init__(self) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_immutable
        """Construct an empty ReqIF metadata store."""
        self._identifiers = {}
        self._metadata = {}
        self._next_id = 1

    def load(self, file_name: str) -> bool:
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_init
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_reuse
        """Load the ReqIF metadata store from a JSON file.

        A missing file is treated as the initial conversion and leaves the store
        empty without reporting an error. A version 1 file without a metadata section
        loads with an empty metadata map.

        Args:
            file_name (str): The name of the JSON file to load.

        Returns:
            bool: True if loading succeeded or the file does not exist yet, False on error.
        """
        status = True

        log_verbose(f"Loading ReqIF metadata store {file_name}.")

        try:
            with open(file_name, "r", encoding="utf-8") as file:
                data = json.load(file)

            self._identifiers = dict(data.get("identifiers", {}))
            self._metadata = dict(data.get("metadata", {}))
            self._next_id = int(data.get("next_id", len(self._identifiers) + 1))

        except FileNotFoundError:
            log_verbose(f"ReqIF metadata store {file_name} does not exist yet; starting empty.")

        except (OSError, IOError, ValueError) as exc:
            log_error(f"Failed to load ReqIF metadata store {file_name}: {exc}")
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

    def resolve(self, key: str, default_identifier: str) -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_immutable
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_reuse
        """Return the stored identifier for the given key or store the given default.

        Unlike :meth:`get_or_create`, an unknown key is associated with the provided
        ``default_identifier`` (a readable slug) instead of a counter-based value. This
        keeps generated identifiers stable and human-readable while still reusing a
        seeded original identifier on a round-trip.

        Args:
            key (str): Stable logical key identifying the ReqIF element.
            default_identifier (str): Identifier to store and return when the key is unknown.

        Returns:
            str: The identifier associated with the key.
        """
        identifier = self._identifiers.get(key)

        if identifier is None:
            identifier = default_identifier
            self._identifiers[key] = identifier

        return identifier

    def seed_identifier(self, key: str, identifier: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_identifier
        """Seed the identifier of a ReqIF element under its stable logical key.

        Args:
            key (str): Stable logical key identifying the ReqIF element.
            identifier (str): The identifier to associate with the key.
        """
        self._identifiers[key] = identifier

    def set_metadata(self, key: str, value: str) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_identifier
        """Store a ReqIF metadata value under the given key.

        Args:
            key (str): Metadata key.
            value (str): Metadata value.
        """
        self._metadata[key] = value

    def get_metadata(self, key: str) -> Optional[str]:
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_reuse
        """Return the ReqIF metadata value for the given key, or None if unknown.

        Args:
            key (str): Metadata key.

        Returns:
            Optional[str]: The metadata value, or None if the key is unknown.
        """
        return self._metadata.get(key)

    def get_reverse_map(self) -> dict:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Return a mapping from stored identifier to its stable logical key.

        Used by the ReqIF import to match an incoming ReqIF element back to the TRLC
        element it was generated from.

        Returns:
            dict: Mapping from identifier to logical key.
        """
        return {identifier: key for key, identifier in self._identifiers.items()}

    def save(self, file_name: str) -> bool:
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_init
        # lobster-trace: SwRequirements.sw_req_reqif_identifier_store_reuse
        """Persist the ReqIF metadata store to a JSON file.

        Args:
            file_name (str): The name of the JSON file to write.

        Returns:
            bool: True if the file was written successfully, False otherwise.
        """
        status = True

        log_verbose(f"Saving ReqIF metadata store {file_name}.")

        data = {
            "version": ReqifMetaData.SCHEMA_VERSION,
            "next_id": self._next_id,
            "identifiers": self._identifiers,
            "metadata": self._metadata
        }

        try:
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, sort_keys=True)

        except (OSError, IOError) as exc:
            log_error(f"Failed to save ReqIF metadata store {file_name}: {exc}")
            status = False

        return status

# Functions ********************************************************************


def spec_object_type_key(trlc_type_name: str) -> str:
    # lobster-trace: SwRequirements.sw_req_reqif_import_type_identity
    """Return the stable logical key of a ReqIF SPEC-OBJECT-TYPE.

    Args:
        trlc_type_name (str): The TRLC type name.

    Returns:
        str: The stable logical key.
    """
    return f"spec-object-type:{trlc_type_name}"


def attribute_definition_key(trlc_type_name: str, definition_key: str) -> str:
    # lobster-trace: SwRequirements.sw_req_reqif_import_type_identity
    """Return the stable logical key of a ReqIF ATTRIBUTE-DEFINITION.

    Args:
        trlc_type_name (str): The TRLC type name owning the attribute.
        definition_key (str): The internal attribute definition key (e.g. ``field_Text``).

    Returns:
        str: The stable logical key.
    """
    return f"attribute-definition:{trlc_type_name}.{definition_key}"


def enum_datatype_key(trlc_enum_name: str) -> str:
    # lobster-trace: SwRequirements.sw_req_reqif_import_type_identity
    """Return the stable logical key of a ReqIF DATATYPE-DEFINITION-ENUMERATION.

    Args:
        trlc_enum_name (str): The TRLC enumeration type name.

    Returns:
        str: The stable logical key.
    """
    return f"enum-datatype:{trlc_enum_name}"


def enum_value_key(trlc_enum_name: str, trlc_literal_name: str) -> str:
    # lobster-trace: SwRequirements.sw_req_reqif_import_type_identity
    """Return the stable logical key of a ReqIF ENUM-VALUE.

    Args:
        trlc_enum_name (str): The TRLC enumeration type name.
        trlc_literal_name (str): The TRLC enumeration literal name.

    Returns:
        str: The stable logical key.
    """
    return f"enum-value:{trlc_enum_name}.{trlc_literal_name}"


def specification_key(spec_long_name: str) -> str:
    # lobster-trace: SwRequirements.sw_req_reqif_import_type_identity
    """Return the stable logical key of a ReqIF SPECIFICATION.

    Args:
        spec_long_name (str): The specification long name.

    Returns:
        str: The stable logical key.
    """
    return f"specification:{spec_long_name}"


# Main *************************************************************************
