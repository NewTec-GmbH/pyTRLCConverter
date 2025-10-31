"""Test the render configuration.
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

from pyTRLCConverter.render_config import RenderConfig

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

def test_tc_render_configuration_no_file(record_property):
    # lobster-trace: SwTests.tc_render_configuration
    """
    Loading a render configuration file that not exists, shall return an error.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
    """
    record_property("lobster-trace", "SwTests.tc_render_configuration")

    render_cfg = RenderConfig()
    is_success = render_cfg.load("tests/utils/non_existing_file.json")

    assert is_success is False

def test_tc_render_configuration_valid_file(record_property):
    # lobster-trace: SwTests.tc_render_configuration
    """
    Loading a render configuration file that exists, shall succeed.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
    """
    record_property("lobster-trace", "SwTests.tc_render_configuration")

    render_cfg = RenderConfig()
    is_success = render_cfg.load("tests/utils/renderCfg.json")

    assert is_success is True

    assert render_cfg.get_format_specifier("package", "type", "description") == RenderConfig.FORMAT_SPECIFIER_MD
    assert render_cfg.is_format_md("package", "type", "description") is True
    assert render_cfg.is_format_rst("package", "type", "description") is False
    assert render_cfg.is_format_plain("package", "type", "description") is False

    assert render_cfg.get_format_specifier("package", "typeRst", "description") == RenderConfig.FORMAT_SPECIFIER_RST
    assert render_cfg.is_format_md("package", "typeRst", "description") is False
    assert render_cfg.is_format_rst("package", "typeRst", "description") is True
    assert render_cfg.is_format_plain("package", "typeRst", "description") is False

    assert render_cfg.get_format_specifier("package", "type", "note") == RenderConfig.FORMAT_SPECIFIER_PLAIN
    assert render_cfg.is_format_md("package", "type", "note") is False
    assert render_cfg.is_format_rst("package", "type", "note") is False
    assert render_cfg.is_format_plain("package", "type", "note") is True

# Main *************************************************************************
