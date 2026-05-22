"""ReqIF Renderer for Marko.
    It is used to convert GitHub Flavored Markdown AST to ReqIF-compatible XHTML.

    Author: Stefan Vogel (stefan.vogel@newtec.de)
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

from __future__ import annotations
from pyTRLCConverter.marko.md2reqif_renderer import Md2ReqifRenderer

# Variables ********************************************************************

# Classes **********************************************************************


class Gfm2ReqifRenderer(Md2ReqifRenderer):
    # lobster-trace: SwRequirements.sw_req_reqif_render_gfm
    # lobster-trace: SwRequirements.sw_req_reqif_render_plantuml
    # lobster-trace: SwRequirements.sw_req_plantuml
    """Renderer for ReqIF XHTML output from GitHub Flavored Markdown.

    Inherits the inline PlantUML handling from :class:`Md2ReqifRenderer`.
    The GFM extension is applied by the surrounding ``Markdown`` instance, so
    this subclass only exists to provide a distinct renderer type for the GFM
    code path.
    """

# Functions ********************************************************************

# Main *************************************************************************
