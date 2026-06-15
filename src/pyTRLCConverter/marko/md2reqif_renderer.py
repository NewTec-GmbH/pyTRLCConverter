"""ReqIF Renderer for Marko.
    It is used to convert CommonMark AST to ReqIF-compatible XHTML.

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

from __future__ import annotations
import hashlib
import html
import os
from typing import TYPE_CHECKING, Optional
from marko.html_renderer import HTMLRenderer
from pyTRLCConverter.plantuml import PlantUML

if TYPE_CHECKING:
    from marko import block

# Variables ********************************************************************

# Classes **********************************************************************


class Md2ReqifRenderer(HTMLRenderer):
    # lobster-trace: SwRequirements.sw_req_reqif_render_md
    # lobster-trace: SwRequirements.sw_req_reqif_render_plantuml
    # lobster-trace: SwRequirements.sw_req_plantuml
    """Renderer for ReqIF XHTML output.

    Extends marko's CommonMark HTML renderer so that fenced code blocks tagged
    ``plantuml`` are rendered as embedded SVG images referenced via XHTML
    ``<object>`` elements. Other fenced code blocks are rendered by the parent
    class as ``<pre><code>`` blocks.
    """

    # Destination directory where generated SVG images are written. The
    # converter is responsible for setting this before each ``convert()`` call
    # and for ensuring the directory exists and survives until the external
    # files have been copied to the final output location.
    image_dir: Optional[str] = None

    # List of ``(source_path, local_name)`` tuples collected during rendering.
    # The converter merges these into its own ``_external_files`` list so the
    # images are copied alongside the ReqIF document.
    external_files: Optional[list] = None

    def render_fenced_code(self, element: "block.FencedCode") -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_render_md
        # lobster-trace: SwRequirements.sw_req_plantuml
        """Render a fenced code block as ReqIF XHTML.

        If the language tag is ``plantuml``, the diagram source is rendered as
        an embedded SVG image referenced via an XHTML ``<object>`` element.
        If PlantUML is not available, an error string is emitted instead.
        For all other language tags the block is rendered by the parent class.

        Args:
            element (block.FencedCode): The fenced code block element to render.

        Returns:
            str: XHTML representation of the fenced code block.
        """
        if element.lang == "plantuml":
            return self._render_plantuml(element.children[0].children)

        return super().render_fenced_code(element)

    def _render_plantuml(self, diagram_source: str) -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_render_md
        # lobster-trace: SwRequirements.sw_req_plantuml
        """Render a PlantUML diagram as an embedded SVG reference.

        Generates SVG bytes via the PlantUML tool, writes them to a temporary
        file under :attr:`image_dir`, registers the file in
        :attr:`external_files` so the converter can copy it next to the ReqIF
        document, and returns an XHTML ``<object>`` element referencing the
        image by its local name.

        On failure (PlantUML not available, server error, ...) an error
        paragraph is emitted instead.

        Args:
            diagram_source (str): The PlantUML diagram source text.

        Returns:
            str: XHTML fragment referencing the generated image, or an error
                paragraph if image generation failed.
        """
        assert Md2ReqifRenderer.image_dir is not None
        assert Md2ReqifRenderer.external_files is not None

        try:
            plantuml = PlantUML()
            svg_bytes = plantuml.generate_to_bytes("svg", diagram_source)

            # Derive a stable, content-addressed file name from the diagram
            # source so identical diagrams share a single SVG and different
            # diagrams never collide when several documents are written to the
            # same output directory (multi-document mode).
            digest = hashlib.sha1(diagram_source.encode("utf-8")).hexdigest()[:12]
            local_name = f"plantuml_{digest}.svg"
            svg_path = os.path.join(Md2ReqifRenderer.image_dir, local_name)
            with open(svg_path, "wb") as svg_file:
                svg_file.write(svg_bytes)

            Md2ReqifRenderer.external_files.append((svg_path, local_name))

            result = f'<p><object type="image/svg+xml" data="{html.escape(local_name)}"></object></p>\n'
        except (FileNotFoundError, OSError) as exc:
            result = f"<p>[PlantUML error: {html.escape(str(exc))}]</p>\n"

        return result

# Functions ********************************************************************

# Main *************************************************************************
