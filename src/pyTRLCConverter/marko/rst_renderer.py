"""reStructuredText renderer for Marko.

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

from __future__ import annotations
from typing import TYPE_CHECKING, Any, cast
from marko import Renderer

if TYPE_CHECKING:
    from . import block, inline

# Variables ********************************************************************

# Classes **********************************************************************

# pylint: disable-next=too-many-public-methods
class RSTRenderer(Renderer):
    # lobster-trace: SwRequirements.sw_req_rst_render_md
    """Renderer for reStructuredText output."""

    def render_paragraph(self, element: block.Paragraph) -> str:
        """
        Renders a paragraph element.

        Args:
            element (block.Paragraph): The paragraph element to render.

        Returns:
            str: The rendered paragraph as a string.
        """
        return self.render_children(element) + "\n\n"

    def render_list(self, element: block.List) -> str:
        """
        Renders a list (ordered or unordered) element.

        Args:
            element (block.List): The list element to render.

        Returns:
            str: The rendered list as a string.
        """
        items = []
        marker = "#" if element.ordered else "*"

        for child in element.children:
            item = self.render_list_item(child, marker)
            items.append(item)

        return "\n".join(items) + "\n"

    def render_list_item(self, element: block.ListItem, marker="*") -> str:
        """
        Renders a list item element.

        Args:
            element (block.ListItem): The list item element to render.
            marker (str, optional): The marker to use for the list item. Defaults to "*".

        Returns:
            str: The rendered list item as a string.
        """
        content = self.render_children(element)

        return f"{marker} {content}"

    def render_quote(self, element: block.Quote) -> str:
        """
        Renders a blockquote element.

        Args:
            element (block.Quote): The blockquote element to render.

        Returns:
            str: The rendered blockquote as a string.
        """
        quote = self.render_children(element)
        quoted = "\n".join([f"  {line}" if line.strip() else "" for line in quote.splitlines()])

        return quoted + "\n\n"

    def render_fenced_code(self, element: block.FencedCode) -> str:
        """
        Renders a fenced code block element.

        Args:
            element (block.FencedCode): The fenced code block element to render.

        Returns:
            str: The rendered fenced code block as a string.
        """
        lang = element.lang or ""
        code = element.children[0].children  # type: ignore

        return f".. code-block:: {lang}\n\n    " + "\n    ".join(code.splitlines()) + "\n\n"

    def render_code_block(self, element: block.CodeBlock) -> str:
        """
        Renders a code block element.

        Args:
            element (block.CodeBlock): The code block element to render.

        Returns:
            str: The rendered code block as a string.
        """
        return self.render_fenced_code(cast("block.FencedCode", element))

    def render_html_block(self, element: block.HTMLBlock) -> str:
        """
        Renders a raw HTML block element.

        Args:
            element (block.HTMLBlock): The HTML block element to render.

        Returns:
            str: The rendered HTML block as a string.
        """
        # reStructuredText does not support raw HTML, so output as a literal block.
        body = element.body

        return "::\n\n    " + "\n    ".join(body.splitlines()) + "\n\n"

    # pylint: disable-next=unused-argument
    def render_thematic_break(self, element: block.ThematicBreak) -> str:
        """
        Renders a thematic break (horizontal rule) element.

        Args:
            element (block.ThematicBreak): The thematic break element to render.

        Returns:
            str: The rendered thematic break as a string.
        """
        return "\n----\n\n"

    def render_heading(self, element: block.Heading) -> str:
        """
        Renders a heading element.

        Args:
            element (block.Heading): The heading element to render.

        Returns:
            str: The rendered heading as a string.
        """
        text = self.render_children(element)
        underline = {
            1: "=",
            2: "-",
            3: "~",
            4: "^",
            5: '"',
            6: "'"
        }.get(element.level, "-")

        return f"{text}\n{underline * len(text)}\n\n"

    def render_setext_heading(self, element: block.SetextHeading) -> str:
        """
        Renders a setext heading element.

        Args:
            element (block.SetextHeading): The setext heading element to render.

        Returns:
            str: The rendered setext heading as a string.
        """
        return self.render_heading(cast("block.Heading", element))

    # pylint: disable-next=unused-argument
    def render_blank_line(self, element: block.BlankLine) -> str:
        """
        Renders a blank line element.

        Args:
            element (block.BlankLine): The blank line element to render.

        Returns:
            str: The rendered blank line as a string.
        """
        return "\n"

    # pylint: disable-next=unused-argument
    def render_link_ref_def(self, element: block.LinkRefDef) -> str:
        """
        Renders a link reference definition element.

        Args:
            element (block.LinkRefDef): The link reference definition element to render.

        Returns:
            str: The rendered link reference definition as a string.
        """
        # reStructuredText uses reference links differently; skip for now.
        return ""

    def render_emphasis(self, element: inline.Emphasis) -> str:
        """
        Renders an emphasis (italic) element.

        Args:
            element (inline.Emphasis): The emphasis element to render.

        Returns:
            str: The rendered emphasis as a string.
        """
        return f"*{self.render_children(element)}*"

    def render_strong_emphasis(self, element: inline.StrongEmphasis) -> str:
        """
        Renders a strong emphasis (bold) element.

        Args:
            element (inline.StrongEmphasis): The strong emphasis element to render.

        Returns:
            str: The rendered strong emphasis as a string.
        """
        return f"**{self.render_children(element)}**"

    def render_inline_html(self, element: inline.InlineHTML) -> str:
        """
        Renders an inline HTML element.

        Args:
            element (inline.InlineHTML): The inline HTML element to render.

        Returns:
            str: The rendered inline HTML as a string.
        """
        # Output as literal block.
        html_content = cast(str, element.children)
        return f"``{html_content}``"

    def render_plain_text(self, element: Any) -> str:
        """
        Renders plain text or any element with string children.

        Args:
            element (Any): The element to render.

        Returns:
            str: The rendered plain text as a string.
        """
        if isinstance(element.children, str):
            return element.children

        return self.render_children(element)

    def render_link(self, element: inline.Link) -> str:
        """
        Renders a link element.

        Args:
            element (inline.Link): The link element to render.

        Returns:
            str: The rendered link as a string.
        """
        body = self.render_children(element)
        url = element.dest
        title = f" ({element.title})" if element.title else ""

        return f"`{body} <{url}>`_{title}"

    def render_auto_link(self, element: inline.AutoLink) -> str:
        """
        Renders an auto link element.

        Args:
            element (inline.AutoLink): The auto link element to render.

        Returns:
            str: The rendered auto link as a string.
        """
        return self.render_link(cast("inline.Link", element))

    def render_image(self, element: inline.Image) -> str:
        """
        Renders an image element.

        Args:
            element (inline.Image): The image element to render.

        Returns:
            str: The rendered image as a string.
        """
        url = element.dest
        alt = self.render_children(element)
        title = f"  :alt: {alt}" if alt else ""
        extra_title = f"  :title: {element.title}" if element.title else ""

        return f".. image:: {url}\n{title}\n{extra_title}\n"

    def render_literal(self, element: inline.Literal) -> str:
        """
        Renders a literal (inline code) element.

        Args:
            element (inline.Literal): The literal element to render.

        Returns:
            str: The rendered literal as a string.
        """
        return self.render_raw_text(cast("inline.RawText", element))

    def render_raw_text(self, element: inline.RawText) -> str:
        """
        Renders a raw text element.

        Args:
            element (inline.RawText): The raw text element to render.

        Returns:
            str: The rendered raw text as a string.
        """
        return f"{element.children}"

    # pylint: disable-next=unused-argument
    def render_line_break(self, element: inline.LineBreak) -> str:
        """
        Renders a line break element.

        Args:
            element (inline.LineBreak): The line break element to render.

        Returns:
            str: The rendered line break as a string.
        """
        return "\n"

    def render_code_span(self, element: inline.CodeSpan) -> str:
        """
        Renders a code span (inline code) element.

        Args:
            element (inline.CodeSpan): The code span element to render.

        Returns:
            str: The rendered code span as a string.
        """
        return f"``{cast(str, element.children)}``"

# Functions ********************************************************************

# Main *************************************************************************
