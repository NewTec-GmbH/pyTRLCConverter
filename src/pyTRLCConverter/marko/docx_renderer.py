"""Docx Renderer for Marko.

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
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.document import Document as DocxDocument

if TYPE_CHECKING:
    from . import block, inline
    from .element import Element
    from .block import Document

# Variables ********************************************************************

# Classes **********************************************************************

# pylint: disable-next=too-many-public-methods
class DocxRenderer(Renderer):
    """Renderer for docx output."""

    def __init__(self) -> None:
        """Initialize docx renderer."""
        super().__init__()
        self._list_indent_level = 0

    def render_children(self, element: Any) -> Any:
        """
        Recursively renders child elements of a given element to
        a docx document.

        Args:
            element (Element): The parent element whose children are to be rendered.

        Returns:
            DocxDocument: The rendered children as a docx document.
        """
        docx_document = docx.Document()

        for child in element.children:
            docx_child_document = self.render(child)

            # Copy paragraphs from the child document to the main document.
            # This is a simple way to merge documents and includes text and basic formatting.
            for para in docx_child_document.paragraphs:
                docx_document._body._element.append(para._element) # pylint: disable=protected-access

        return docx_document

    def render_paragraph(self, element: block.Paragraph) -> DocxDocument:
        """
        Renders a paragraph element.

        Args:
            element (block.Paragraph): The paragraph element to render.

        Returns:
            DocxDocument: The rendered paragraph as a docx document.
        """
        return self.render_children(element)

    def render_list(self, element: block.List) -> DocxDocument:
        """
        Renders a list (ordered or unordered) element.

        Args:
            element (block.List): The list element to render.

        Returns:
            DocxDocument: The rendered list as a docx document.
        """
        docx_document = docx.Document()

        self._list_indent_level += 1

        style = "List Number" if element.ordered else "List Bullet"

        if self._list_indent_level > 1:
            style += f" {self._list_indent_level}"

        for child in element.children:
            docx_child_document = self.render_list_item(child)

            # Copy paragraphs from the child document to the main document.
            # This is a simple way to merge documents and includes text and basic formatting.
            for para in docx_child_document.paragraphs:

                # Add style to paragraph if not already set.
                # This avoids overwriting existing styles in nested lists.
                # Only set style if paragraph doesn't have an explicit style name
                current_style = getattr(para, "style", None)
                style_name = getattr(current_style, "name", None) if current_style else None
                if not style_name or style_name == 'Normal':
                    para.style = style

                docx_document._body._element.append(para._element) # pylint: disable=protected-access

        self._list_indent_level -= 1

        return docx_document

    def render_list_item(self, element: block.ListItem) -> DocxDocument:
        """
        Renders a list item element.

        Args:
            element (block.ListItem): The list item element to render.
            marker (str, optional): The marker to use for the list item. Defaults to "*".

        Returns:
            DocxDocument: The rendered list item as a docx document.
        """
        return self.render_children(element)

    def render_quote(self, element: block.Quote) -> DocxDocument:
        """
        Renders a blockquote element.

        Args:
            element (block.Quote): The blockquote element to render.

        Returns:
            DocxDocument: The rendered blockquote as a docx document.
        """
        # For simplicity, render blockquote content as normal content.
        return self.render_children(element)

    def render_fenced_code(self, element: block.FencedCode) -> DocxDocument:
        """
        Renders a fenced code block element.

        Args:
            element (block.FencedCode): The fenced code block element to render.

        Returns:
            DocxDocument: The rendered fenced code block as a docx document.
        """
        lang = getattr(element, 'lang', "")
        code = element.children

        docx_document = docx.Document()
        para = docx_document.add_paragraph()
        run = para.add_run(code)
        run.font.name = "Consolas"
        para.style = "Code" if "Code" in [s.name for s in docx_document.styles] else para.style

        # Optionally, add language as a comment or prefix
        if lang:
            para.insert_paragraph_before(f"[{lang}]")

        return docx_document

    def render_code_block(self, element: block.CodeBlock) -> DocxDocument:
        """
        Renders a code block element.

        Args:
            element (block.CodeBlock): The code block element to render.

        Returns:
            DocxDocument: The rendered code block as a docx document.
        """
        return self.render_fenced_code(cast("block.FencedCode", element))

    def render_html_block(self, element: block.HTMLBlock) -> DocxDocument:
        """
        Renders a raw HTML block element.

        Args:
            element (block.HTMLBlock): The HTML block element to render.

        Returns:
            DocxDocument: The rendered HTML block as a docx document.
        """
        return self.render_fenced_code(cast("block.FencedCode", element))

    # pylint: disable-next=unused-argument
    def render_thematic_break(self, element: block.ThematicBreak) -> DocxDocument:
        """
        Renders a thematic break (horizontal rule) element.

        Args:
            element (block.ThematicBreak): The thematic break element to render.

        Returns:
            DocxDocument: The rendered thematic break as a docx document.
        """
        docx_document = docx.Document()
        # Add a horizontal rule by inserting a paragraph with a bottom border
        para = docx_document.add_paragraph()
        p = para._element # pylint: disable=protected-access

        paragraph_properties = p.get_or_add_pPr()
        p_bdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), 'auto')
        p_bdr.append(bottom)
        paragraph_properties.append(p_bdr)

        return docx_document

    def render_heading(self, element: block.Heading) -> DocxDocument:
        """
        Renders a heading element.

        Args:
            element (block.Heading): The heading element to render.

        Returns:
            DocxDocument: The rendered heading as a docx document.
        """
        docx_document = docx.Document()

        level = min(max(element.level, 1), 9)  # docx supports levels 1-9
        heading = docx_document.add_heading(level=level)
        heading.add_run(self.render_children(element).text)

        return docx_document

    def render_setext_heading(self, element: block.SetextHeading) -> DocxDocument:
        """
        Renders a setext heading element.

        Args:
            element (block.SetextHeading): The setext heading element to render.

        Returns:
            DocxDocument: The rendered setext heading as a docx document.
        """
        return self.render_heading(cast("block.Heading", element))

    # pylint: disable-next=unused-argument
    def render_blank_line(self, element: block.BlankLine) -> DocxDocument:
        """
        Renders a blank line element.

        Args:
            element (block.BlankLine): The blank line element to render.

        Returns:
            DocxDocument: The rendered blank line as a docx.Document.
        """
        docx_document = docx.Document()
        docx_document.add_paragraph()
        return docx_document

    # pylint: disable-next=unused-argument
    def render_link_ref_def(self, element: block.LinkRefDef) -> DocxDocument:
        """
        Renders a link reference definition element.

        Args:
            element (block.LinkRefDef): The link reference definition element to render.

        Returns:
            DocxDocument: The rendered link reference definition as a docx.Document.
        """
        # reStructuredText uses reference links differently; skip for now.
        return docx.Document()

    def render_emphasis(self, element: inline.Emphasis) -> DocxDocument:
        """
        Renders an emphasis (italic) element.

        Args:
            element (inline.Emphasis): The emphasis element to render.

        Returns:
            DocxDocument: The rendered emphasis as a docx document.
        """
        docx_document = docx.Document()
        children = self.render_children(element)

        for para in children.paragraphs:
            run = para.add_run()
            run.italic = True
            run.add_text(para.text)

        return docx_document

    def render_strong_emphasis(self, element: inline.StrongEmphasis) -> DocxDocument:
        """
        Renders a strong emphasis (bold) element.

        Args:
            element (inline.StrongEmphasis): The strong emphasis element to render.

        Returns:
            DocxDocument: The rendered strong emphasis as a docx document.
        """
        docx_document = docx.Document()
        children = self.render_children(element)

        for para in children.paragraphs:
            run = para.add_run()
            run.bold = True
            run.add_text(para.text)

        return docx_document

    def render_inline_html(self, element: inline.InlineHTML) -> DocxDocument:
        """
        Renders an inline HTML element.

        Args:
            element (inline.InlineHTML): The inline HTML element to render.

        Returns:
            DocxDocument: The rendered inline HTML as a docx document.
        """
        return self.render_fenced_code(cast("block.FencedCode", element))

    def render_plain_text(self, element: Any) -> DocxDocument:
        """
        Renders plain text or any element with string children.

        Args:
            element (Any): The element to render.

        Returns:
            DocxDocument: The rendered plain text as a docx document.
        """
        if isinstance(element.children, str):
            docx_document = docx.Document()
            docx_document.add_paragraph(element.children)
            return docx_document

        return self.render_children(element)

    def render_link(self, element: inline.Link) -> DocxDocument:
        """
        Renders a link element.

        Args:
            element (inline.Link): The link element to render.

        Returns:
            DocxDocument: The rendered link as a docx document.
        """
        body = self.render_children(element)
        url = element.dest
        title = f" ({element.title})" if element.title else ""

        docx_document = docx.Document()
        for para in body.paragraphs:
            run = para.add_run()
            run.text = f"{para.text} [{url}{title}]"

        return docx_document

    def render_auto_link(self, element: inline.AutoLink) -> DocxDocument:
        """
        Renders an auto link element.

        Args:
            element (inline.AutoLink): The auto link element to render.

        Returns:
            DocxDocument: The rendered auto link as a docx document.
        """
        return self.render_link(cast("inline.Link", element))

    def render_image(self, element: inline.Image) -> DocxDocument:
        """
        Renders an image element.

        Args:
            element (inline.Image): The image element to render.

        Returns:
            DocxDocument: The rendered image as a docx document.
        """
        url = element.dest
        alt = self.render_children(element)
        title = f"  :alt: {alt}" if alt else ""
        extra_title = f"  :title: {element.title}" if element.title else ""

        docx_document = docx.Document()
        docx_document.add_paragraph(f"{url}\n{title}\n{extra_title}\n")

        return docx_document

    def render_literal(self, element: inline.Literal) -> DocxDocument:
        """
        Renders a literal (inline code) element.

        Args:
            element (inline.Literal): The literal element to render.

        Returns:
            DocxDocument: The rendered literal as a docx document.
        """
        return self.render_raw_text(cast("inline.RawText", element))

    def render_raw_text(self, element: inline.RawText) -> DocxDocument:
        """
        Renders a raw text element.

        Args:
            element (inline.RawText): The raw text element to render.

        Returns:
            DocxDocument: The rendered raw text as a docx document.
        """
        docx_document = docx.Document()
        docx_document.add_paragraph(element.children)

        return docx_document

    # pylint: disable-next=unused-argument
    def render_line_break(self, element: inline.LineBreak) -> DocxDocument:
        """
        Renders a line break element.

        Args:
            element (inline.LineBreak): The line break element to render.

        Returns:
            DocxDocument: The rendered line break as a docx document.
        """
        docx_document = docx.Document()
        docx_document.add_paragraph("\n")

        return docx_document

    def render_code_span(self, element: inline.CodeSpan) -> DocxDocument:
        """
        Renders a code span (inline code) element.

        Args:
            element (inline.CodeSpan): The code span element to render.

        Returns:
            DocxDocument: The rendered code span as a docx document.
        """
        docx_document = docx.Document()
        docx_document.add_paragraph(f"``{cast(str, element.children)}``")

        return docx_document

# Functions ********************************************************************

# Main *************************************************************************
