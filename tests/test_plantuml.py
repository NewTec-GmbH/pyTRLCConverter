"""
Unit tests for the PlantUML class in the pyTRLCConverter module.

This file contains tests that verify the functionality of the PlantUML class,
including the creation of server URLs for PlantUML diagrams.

Fixtures:
    plantuml_instance: Provides an instance of the PlantUML class with a mocked server URL.

Tests:
    test_make_server_url: Tests the _make_server_url method of the PlantUML class.
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
import os
import base64
import urllib.parse
import zlib
from unittest.mock import patch, mock_open
import pytest
from pyTRLCConverter.plantuml import (
    PlantUML,
    BASE64_ENCODE_CHARS,
    PLANTUML_ENCODE_CHARS,
)

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

# pylint: disable=W0212 # Access to a protected member

@pytest.fixture
def plantuml_instance():
    # lobster-exclude: Utility fixture for other test cases.
    """
    Create an instance of PlantUML with a server URL.

    This function temporarily sets the PLANTUML environment variable to
    "http://plantuml.com/plantuml" and returns an instance of the PlantUML class.

    Returns:
        PlantUML: An instance of the PlantUML class configured to use the specified server URL.
    """
    with patch.dict(os.environ, {"PLANTUML": "http://plantuml.com/plantuml"}):
        return PlantUML()


# pylint: disable-next=redefined-outer-name
def test_make_server_url(record_property, plantuml_instance: PlantUML):
    # lobster-trace: SwTests.tc_plantuml
    """
    Test the _make_server_url method of the PlantUML instance.

    The expected PlantUML server URL is generated using the same
    compression and encoding algorithm as the implementation itself.
    This avoids relying on a zlib-specific compressed byte stream that
    can differ between Python/zlib versions.
    """
    record_property("lobster-trace", "SwTests.tc_plantuml")

    diagram_type = "svg"
    diagram_path = "test_diagram.puml"
    mock_diagram_content = "@startuml\nAlice -> Bob: Hello\n@enduml"

    # Build the expected URL using the same PlantUML encoding algorithm.
    compressed_data = zlib.compress(
        mock_diagram_content.encode("utf-8")
    )[2:-4]

    base64_encoded_data = base64.b64encode(compressed_data)

    base64_to_puml_trans = bytes.maketrans(
        BASE64_ENCODE_CHARS.encode("utf-8"),
        PLANTUML_ENCODE_CHARS.encode("utf-8"),
    )

    expected_encoded_data = base64_encoded_data.translate(
        base64_to_puml_trans
    ).decode("utf-8")

    expected_url = (
        f"http://plantuml.com/plantuml/"
        f"{diagram_type}/"
        f"{urllib.parse.quote(expected_encoded_data)}"
    )

    # Test the URL creation when reading the diagram content from a file.
    with patch(
        "builtins.open",
        mock_open(read_data=mock_diagram_content),
    ):
        result_url = plantuml_instance._make_server_url(
            diagram_type,
            diagram_path,
        )

    assert result_url == expected_url

    # Repeat the test by giving the diagram content directly to the function.
    result_url = plantuml_instance._make_server_url(
        diagram_type,
        mock_diagram_content,
        source_is_file=False,
    )

    assert result_url == expected_url

# Main *************************************************************************
