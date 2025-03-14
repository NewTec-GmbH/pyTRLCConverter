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
import pytest
from unittest.mock import patch, mock_open
from pyTRLCConverter.plantuml import PlantUML

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

# pylint: disable=W0212 # Access to a protected member

@pytest.fixture
def plantuml_instance():
    """
    Create an instance of PlantUML with a server URL.

    This function temporarily sets the PLANTUML environment variable to
    "http://plantuml.com/plantuml" and returns an instance of the PlantUML class.

    Returns:
        PlantUML: An instance of the PlantUML class configured to use the specified server URL.
    """
    with patch.dict(os.environ, {"PLANTUML": "http://plantuml.com/plantuml"}):
        return PlantUML()


def test_make_server_url(record_property: any, plantuml_instance: PlantUML):
    # lobster-trace: SwTests.tc_cli
    """
    Test the _make_server_url method of the PlantUML instance.
    This test verifies that the _make_server_url method correctly generates
    the server URL for a given diagram type and path. It mocks the content
    of the diagram file and checks if the generated URL matches the expected URL.
    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        plantuml (PlantUML): An instance of the PlantUML class.
    Asserts:
        The generated URL starts with the expected base URL.
        The generated URL matches the expected URL.
    """
    record_property("lobster-trace", "SwTests.tc_cli")
    
    diagram_type = "svg"
    diagram_path = "test_diagram.puml"
    expected_url = "http://plantuml.com/plantuml/svg/SoWkIImgAStDuNBCoKnELT2rKt3AJx9Iy4ZDoSddSaZDIm7A0G0%3D"

    mock_diagram_content = "@startuml\nAlice -> Bob: Hello\n@enduml"
    with patch("builtins.open", mock_open(read_data=mock_diagram_content)):
        result_url = plantuml_instance._make_server_url(diagram_type, diagram_path)

    assert result_url.startswith("http://plantuml.com/plantuml/svg/")
    assert result_url == expected_url

# Main *************************************************************************
