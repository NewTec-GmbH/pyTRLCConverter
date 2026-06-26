"""Provides the import configuration for the ReqIF merge import.

    Combines the attribute translation and the render configuration to determine, for a
    given TRLC attribute, the ReqIF long name used on export and the desired TRLC value
    derived from an imported ReqIF attribute value (reverse rendering).

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
import html
from typing import Optional
from pyTRLCConverter.render_config import RenderConfig
from pyTRLCConverter.reqif_reader import extract_object_data
from pyTRLCConverter.translator import Translator

# Variables ********************************************************************

# Classes **********************************************************************


class ImportConfig:
    """Maps TRLC attributes to ReqIF long names and reverses rendered ReqIF values."""

    def __init__(self, translator: Translator, render_cfg: RenderConfig) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Initializes the import configuration.

        Args:
            translator (Translator): The attribute name translator (TRLC to ReqIF long name).
            render_cfg (RenderConfig): The render configuration used to classify attributes.
        """
        self._translator = translator
        self._render_cfg = render_cfg

    def reqif_long_name(self, type_name: str, attr_name: str) -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Return the ReqIF long name used on export for a TRLC attribute.

        Args:
            type_name (str): The TRLC record type name.
            attr_name (str): The TRLC attribute name.

        Returns:
            str: The ReqIF long name.
        """
        return self._translator.translate(type_name, attr_name)

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def desired_value(self, package: str, type_name: str, attr_name: str,
                      reqif_value: str, is_xhtml: bool) -> Optional[str]:
        # lobster-trace: SwRequirements.sw_req_reqif_import_merge
        """Return the desired TRLC value for an imported ReqIF attribute value.

        The reverse rendering depends on the attribute's configured format. A return value
        of None means the attribute is not safely reversible (e.g. Markdown or GFM) and the
        existing TRLC value shall be preserved.

        Args:
            package (str): The TRLC package name.
            type_name (str): The TRLC record type name.
            attr_name (str): The TRLC attribute name.
            reqif_value (str): The imported ReqIF attribute value (XHTML inner content or raw value).
            is_xhtml (bool): Whether the imported value originated from an XHTML attribute.

        Returns:
            Optional[str]: The desired TRLC value, or None when the attribute shall be preserved.
        """
        if self._render_cfg.is_format_xhtml(package, type_name, attr_name) is True:
            desired = reqif_value
        elif self._render_cfg.is_format_path(package, type_name, attr_name) is True:
            desired = extract_object_data(reqif_value)
        elif (self._render_cfg.is_format_md(package, type_name, attr_name) is True
              or self._render_cfg.is_format_gfm(package, type_name, attr_name) is True):
            desired = None
        elif is_xhtml is True:
            desired = unrender_plain_xhtml(reqif_value)
        else:
            desired = reqif_value

        return desired


# Functions ********************************************************************


def unrender_plain_xhtml(inner_xhtml: str) -> Optional[str]:
    # lobster-trace: SwRequirements.sw_req_reqif_import_merge
    """Reverse the plain-text to XHTML rendering performed by the ReqIF export.

    The export wraps plain text in ``<p>`` paragraphs, turns single newlines into ``<br/>``
    and escapes XML entities. This function reverses that for the common case. If the content
    is not a simple paragraph structure (e.g. it contains tables or lists), None is returned so
    the caller preserves the existing value.

    Args:
        inner_xhtml (str): The inner XHTML content (outer div already removed).

    Returns:
        Optional[str]: The plain text, or None if the content is not a simple paragraph structure.
    """
    result: Optional[str] = None
    stripped = inner_xhtml.strip()

    if stripped.startswith("<p>") and stripped.endswith("</p>"):
        body = stripped[len("<p>"):-len("</p>")]
        paragraphs = body.split("</p><p>")

        if all(("<p>" not in paragraph and "</p>" not in paragraph) for paragraph in paragraphs):
            result = "\n\n".join(
                html.unescape(paragraph.replace("<br/>", "\n"))
                for paragraph in paragraphs
            )

    return result


# Main *************************************************************************
