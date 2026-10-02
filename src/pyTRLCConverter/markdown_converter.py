"""Converter to Markdown format.

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
import hashlib
import os
import re
import shutil
import tempfile
from typing import Optional, Any
from trlc.ast import Implicit_Null, Record_Object, Record_Reference, String_Literal, Expression
from pyTRLCConverter.base_converter import BaseConverter
from pyTRLCConverter.markdown.document import MarkdownDocument
from pyTRLCConverter.markdown.element import Heading, Table, BulletList
from pyTRLCConverter.markdown.text import MarkdownText
from pyTRLCConverter.plantuml import PlantUML
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import TrlcAstWalker
from pyTRLCConverter.logger import log_verbose, log_error

# Variables ********************************************************************

# Classes **********************************************************************

# pylint: disable-next=too-many-instance-attributes
class MarkdownConverter(BaseConverter):
    """
    MarkdownConverter provides functionality for converting to a markdown format.

    The converter builds a Markdown AST (MarkdownDocument made of block elements)
    while walking the TRLC symbols and writes the output file(s) only once the
    document is complete (in leave_file() for multiple-document mode and in
    finish() for single-document mode).
    """

    OUTPUT_FILE_NAME_DEFAULT = "output.md"
    TOP_LEVEL_DEFAULT = "Specification"

    def __init__(self, args: Any) -> None:
        # lobster-trace: SwRequirements.sw_req_no_prj_spec
        # lobster-trace: SwRequirements.sw_req_markdown
        """
        Initializes the converter.

        Args:
            args (Any): The parsed program arguments.
        """
        super().__init__(args)

        # The path to the given output folder.
        self._out_path = args.out

        # The excluded paths in normalized form.
        self._excluded_paths = []

        if args.exclude is not None:
            self._excluded_paths = [os.path.normpath(path) for path in args.exclude]

        # The Markdown document currently being built. In multiple-document mode a new
        # document is created per file, in single-document mode one document is shared.
        self._document: Optional[MarkdownDocument] = None

        # The base level for the headings. Its the minimum level for the headings which depends
        # on the single/multiple document mode.
        self._base_level = 1

        # A top level heading is always required to generate a compliant Markdown document.
        # In single document mode it will always be necessary.
        # In multiple document mode only if there is no top level section.
        self._is_top_level_heading_req = True

        # The AST walker meta data for processing the record object fields.
        # This will hold the information about the current package, type and attribute being processed.
        self._ast_meta_data = None

        self._plantuml_tmp_dir: Optional[tempfile.TemporaryDirectory] = None
        self._external_files: list = []

    @staticmethod
    def get_subcommand() -> str:
        # lobster-trace: SwRequirements.sw_req_markdown
        """
        Return subcommand token for this converter.

        Returns:
            str: Parser subcommand token
        """
        return "markdown"

    @staticmethod
    def get_description() -> str:
        # lobster-trace: SwRequirements.sw_req_markdown
        """
        Return converter description.

        Returns:
            str: Converter description
        """
        return "Convert into markdown format."

    @classmethod
    def register(cls, args_parser: Any) -> None:
        # lobster-trace: SwRequirements.sw_req_markdown_multiple_doc_mode
        # lobster-trace: SwRequirements.sw_req_markdown_single_doc_mode
        # lobster-trace: SwRequirements.sw_req_markdown_top_level_default
        # lobster-trace: SwRequirements.sw_req_markdown_top_level_custom
        # lobster-trace: SwRequirements.sw_req_markdown_out_file_name_default
        # lobster-trace: SwRequirements.sw_req_markdown_out_file_name_custom
        # lobster-trace: SwRequirements.sw_req_markdown_render_plantuml
        # lobster-trace: SwRequirements.sw_req_cli_render_plantuml
        """
        Register converter specific argument parser.

        Args:
            args_parser (Any): Argument parser
        """
        super().register(args_parser)

        assert BaseConverter._parser is not None

        BaseConverter._parser.add_argument(
            "-e",
            "--empty",
            type=str,
            default=BaseConverter.EMPTY_ATTRIBUTE_DEFAULT,
            required=False,
            help="Every attribute value which is empty will output the string " \
                f"(default = {BaseConverter.EMPTY_ATTRIBUTE_DEFAULT})."
        )

        BaseConverter._parser.add_argument(
            "-n",
            "--name",
            type=str,
            default=MarkdownConverter.OUTPUT_FILE_NAME_DEFAULT,
            required=False,
            help="Name of the generated output file inside the output folder " \
                f"(default = {MarkdownConverter.OUTPUT_FILE_NAME_DEFAULT}) in " \
                "case a single document is generated."
        )

        BaseConverter._parser.add_argument(
            "-sd",
            "--single-document",
            action="store_true",
            required=False,
            default=False,
            help="Generate a single document instead of multiple files. The default is to generate multiple files."
        )

        BaseConverter._parser.add_argument(
            "-tl",
            "--top-level",
            type=str,
            default=MarkdownConverter.TOP_LEVEL_DEFAULT,
            required=False,
            help="Name of the top level heading, required in single document mode " \
                f"(default = {MarkdownConverter.TOP_LEVEL_DEFAULT})."
        )

        BaseConverter._parser.add_argument(
            "--render-plantuml",
            action="store_true",
            required=False,
            default=False,
            help="Render plantuml fenced code blocks as SVG image references. "
                 "Without this option plantuml blocks are passed through unchanged."
        )

    def begin(self) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_single_doc_mode
        # lobster-trace: SwRequirements.sw_req_markdown_sd_top_level
        """
        Begin the conversion process.

        Returns:
            Ret: Status
        """
        assert self._document is None

        # Call the base converter to initialize the common stuff.
        result = BaseConverter.begin(self)

        if result == Ret.OK:

            # Single document mode?
            if self._args.single_document is True:
                log_verbose("Single document mode.")
            else:
                log_verbose("Multiple document mode.")

            # Set the value for empty attributes.
            self._empty_attribute_value = self._args.empty

            log_verbose(f"Empty attribute value: {self._empty_attribute_value}")

            if self._args.render_plantuml is True:
                # pylint: disable-next=consider-using-with
                self._plantuml_tmp_dir = tempfile.TemporaryDirectory(
                    prefix="pyTRLCConverter_markdown_"
                )

            # Single document mode?
            if self._args.single_document is True:
                self._document = MarkdownDocument()

                # The top level heading is always required in single document mode.
                self._document.add(Heading(self._args.top_level, 1))
                self._is_top_level_heading_req = False

                # All headings will be shifted by one level.
                self._base_level = self._base_level + 1

        return result

    def enter_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_multiple_doc_mode
        """
        Enter a file.

        Args:
            file_name (str): File name

        Returns:
            Ret: Status
        """
        # Multiple document mode?
        if self._args.single_document is False:
            assert self._document is None

            # A new document is built for each file. The very first written Markdown part
            # shall not have an empty line before, which the document handles implicitly.
            self._document = MarkdownDocument()
            self._is_top_level_heading_req = True

        return Ret.OK

    def leave_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_multiple_doc_mode
        """
        Leave a file.

        Args:
            file_name (str): File name

        Returns:
            Ret: Status
        """
        result = Ret.OK

        # Multiple document mode?
        if self._args.single_document is False:
            assert self._document is not None

            file_name_md = self._file_name_trlc_to_md(file_name)
            result = self._write_document(file_name_md)

            self._copy_external_files(self._out_path)
            self._external_files = []
            self._document = None
            self._is_top_level_heading_req = True

        return result

    def convert_section(self, section: str, level: int) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_section
        # lobster-trace: SwRequirements.sw_req_markdown_md_top_level
        """
        Process the given section item.
        It will create a Markdown heading with the given section name and level.

        Args:
            section (str): The section name
            level (int): The section indentation level

        Returns:
            Ret: Status
        """
        assert len(section) > 0
        assert self._document is not None

        self._document.add(Heading(section, self._get_markdown_heading_level(level)))

        # If a section heading is written, there is no top level heading required anymore.
        self._is_top_level_heading_req = False

        return Ret.OK

    def convert_record_object_generic(self, record: Record_Object, level: int, translation: Optional[dict]) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        # lobster-trace: SwRequirements.sw_req_markdown_md_top_level
        """
        Process the given record object in a generic way.

        The handler is called by the base converter if no specific handler is
        defined for the record type.

        Args:
            record (Record_Object): The record object.
            level (int): The record level.
            translation (Optional[dict]): Translation dictionary for the record object.
                                            If None, no translation is applied.

        Returns:
            Ret: Status
        """
        assert self._document is not None

        self._add_top_level_heading_on_demand()

        return self._convert_record_object(record, level, translation)

    def finish(self):
        # lobster-trace: SwRequirements.sw_req_markdown_single_doc_mode
        """
        Finish the conversion process.

        Returns:
            Ret: Status
        """
        result = Ret.OK

        # Single document mode?
        if self._args.single_document is True:
            assert self._document is not None

            result = self._write_document(self._args.name)

            self._copy_external_files(self._out_path)
            self._external_files = []
            self._document = None

        if self._plantuml_tmp_dir is not None:
            self._plantuml_tmp_dir.cleanup()
            self._plantuml_tmp_dir = None

        return result

    def _add_top_level_heading_on_demand(self) -> None:
        # lobster-trace: SwRequirements.sw_req_markdown_md_top_level
        # lobster-trace: SwRequirements.sw_req_markdown_sd_top_level
        """Add the top level heading to the document if necessary.
        """
        assert self._document is not None

        if self._is_top_level_heading_req is True:
            self._document.add(Heading(self._args.top_level, 1))
            self._is_top_level_heading_req = False

    def _get_markdown_heading_level(self, level: int) -> int:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """Get the Markdown heading level from the TRLC object level.
            Its mandatory to use this method to calculate the Markdown heading level.
            Otherwise in single document mode the top level heading will be wrong.

        Args:
            level (int): The TRLC object level.

        Returns:
            int: Markdown heading level
        """
        return self._base_level + level

    def _file_name_trlc_to_md(self, file_name_trlc: str) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_multiple_doc_mode
        """
        Convert a TRLC file name to a Markdown file name.

        Args:
            file_name_trlc (str): TRLC file name

        Returns:
            str: Markdown file name
        """
        file_name = os.path.basename(file_name_trlc)
        file_name = os.path.splitext(file_name)[0] + ".md"

        return file_name

    def _write_document(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_out_folder
        """
        Write the current Markdown document to the output file.

        Args:
            file_name (str): The output file name without path.

        Returns:
            Ret: Status
        """
        assert self._document is not None

        result = Ret.OK
        file_name_with_path = file_name

        # Add path to the output file name.
        if 0 < len(self._out_path):
            file_name_with_path = os.path.join(self._out_path, file_name)

        try:
            with open(file_name_with_path, "w", encoding="utf-8") as out_file:
                out_file.write(self._document.render())
        except IOError as e:
            log_error(f"Failed to open file {file_name_with_path}: {e}")
            result = Ret.ERROR

        return result

    def _on_implict_null(self, _: Implicit_Null) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Process the given implicit null value.

        Returns:
            str: The implicit null value.
        """
        return MarkdownText.escape(self._empty_attribute_value)

    def _on_record_reference(self, record_reference: Record_Reference) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Process the given record reference value and return a markdown link.

        Args:
            record_reference (Record_Reference): The record reference value.

        Returns:
            str: Markdown link to the record reference.
        """
        return self._create_markdown_link_from_record_object_reference(record_reference)

    def _on_string_literal(self, string_literal: String_Literal) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_string_format
        # lobster-trace: SwRequirements.sw_req_markdown_render_md
        # lobster-trace: SwRequirements.sw_req_markdown_render_gfm
        """
        Process the given string literal value.

        Args:
            string_literal (String_Literal): The string literal value.

        Returns:
            str: The string literal value.
        """
        result = string_literal.to_string()

        if self._ast_meta_data is not None:
            package_name = self._ast_meta_data.get("package_name", "")
            type_name = self._ast_meta_data.get("type_name", "")
            attribute_name = self._ast_meta_data.get("attribute_name", "")

            result = self._render(package_name, type_name, attribute_name, result)

        return result

    # pylint: disable-next=line-too-long
    def _create_markdown_link_from_record_object_reference(self, record_reference: Record_Reference) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Create a Markdown link from a record reference.
        It considers the file name, the package name, and the record name.

        Args:
            record_reference (Record_Reference): Record reference

        Returns:
            str: Markdown link
        """
        assert record_reference.target is not None

        file_name = ""

        # Single document mode?
        if self._args.single_document is True:
            file_name = self._args.name

            # Is the link to a excluded file?
            for excluded_path in self._excluded_paths:

                if os.path.commonpath([excluded_path, record_reference.target.location.file_name]) == excluded_path:
                    file_name = self._file_name_trlc_to_md(record_reference.target.location.file_name)
                    break

        # Multiple document mode
        else:
            file_name = self._file_name_trlc_to_md(record_reference.target.location.file_name)

        record_name = record_reference.target.name

        anchor_tag = file_name + "#" + record_name.lower().replace(" ", "-")

        return MarkdownText.link(str(record_reference.to_python_object()), anchor_tag)

    def _other_dispatcher(self, expression: Expression) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        # lobster-trace: SwRequirements.sw_req_markdown_escape
        """
        Dispatcher for all other expressions.

        Args:
            expression (Expression): The expression to process.

        Returns:
            str: The processed expression.
        """
        return MarkdownText.escape(expression.to_string())

    def _get_trlc_ast_walker(self) -> TrlcAstWalker:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        # lobster-trace: SwRequirements.sw_req_markdown_escape
        # lobster-trace: SwRequirements.sw_req_markdown_string_format
        """
        If a record object contains a record reference, the record reference will be converted to
        a Markdown link.
        If a record object contains an array of record references, the array will be converted to
        a Markdown list of links.
        Otherwise the record object fields attribute values will be written to the Markdown table.

        Returns:
            TrlcAstWalker: The TRLC AST walker.
        """
        trlc_ast_walker = TrlcAstWalker()
        trlc_ast_walker.add_dispatcher(
            Implicit_Null,
            None,
            self._on_implict_null,
            None
        )
        trlc_ast_walker.add_dispatcher(
            Record_Reference,
            None,
            self._on_record_reference,
            None
        )
        trlc_ast_walker.add_dispatcher(
            String_Literal,
            None,
            self._on_string_literal,
            None
        )
        trlc_ast_walker.set_other_dispatcher(self._other_dispatcher)

        return trlc_ast_walker

    def _render(self, package_name: str, type_name: str, attribute_name: str, attribute_value: str) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_string_format
        # lobster-trace: SwRequirements.sw_req_markdown_render_md
        # lobster-trace: SwRequirements.sw_req_markdown_render_gfm
        # lobster-trace: SwRequirements.sw_req_markdown_render_plantuml
        """Render the attribute value depending on its format.

        Args:
            package_name (str): The package name.
            type_name (str): The type name.
            attribute_name (str): The attribute name.
            attribute_value (str): The attribute value.

        Returns:
            str: The rendered attribute value.
        """
        result = attribute_value

        # If the attribute value is not already in Markdown format, it will be escaped.
        if self._render_cfg.is_format_md(package_name, type_name, attribute_name) is False and \
            self._render_cfg.is_format_gfm(package_name, type_name, attribute_name) is False:

            result = MarkdownText.escape(attribute_value)
            result = MarkdownText.lf2soft_return(result)

        if self._args.render_plantuml is True:
            result = self._render_plantuml_blocks(result)

        return result

    def _render_plantuml_blocks(self, text: str) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_render_plantuml
        # lobster-trace: SwRequirements.sw_req_plantuml
        """Replace plantuml fenced code blocks with SVG image references.

        Each ```plantuml ... ``` block is replaced by ``![](plantuml_<hash>.svg)``.
        The SVG is written to the temporary image directory and registered in
        ``_external_files`` for copying to the output folder. On failure an
        inline ``[PlantUML error: ...]`` text is emitted instead.

        Args:
            text (str): Markdown text that may contain plantuml fenced blocks.

        Returns:
            str: Text with plantuml blocks replaced.
        """
        assert self._plantuml_tmp_dir is not None

        def _replace(match: re.Match) -> str:
            diagram_source = match.group(1)
            try:
                plantuml = PlantUML()
                svg_bytes = plantuml.generate_to_bytes("svg", diagram_source)
                digest = hashlib.sha1(diagram_source.encode("utf-8")).hexdigest()[:12]
                local_name = f"plantuml_{digest}.svg"
                svg_path = os.path.join(self._plantuml_tmp_dir.name, local_name)
                with open(svg_path, "wb") as svg_file:
                    svg_file.write(svg_bytes)
                self._external_files.append((svg_path, local_name))
                return f"![]({local_name})"
            except (FileNotFoundError, OSError) as exc:
                return f"[PlantUML error: {exc}]"

        return re.sub(r"```plantuml\n(.*?)```", _replace, text, flags=re.DOTALL)

    def _copy_external_files(self, dest_dir: str) -> None:
        # lobster-trace: SwRequirements.sw_req_markdown_render_plantuml
        """Copy all collected external files to the given destination directory.

        Args:
            dest_dir (str): Destination directory path.
        """
        copied_sources = set()

        for source_path, local_name in self._external_files:
            if source_path in copied_sources:
                continue

            dest_path = os.path.join(dest_dir, local_name)

            try:
                shutil.copy2(source_path, dest_path)
                copied_sources.add(source_path)
            except (OSError, IOError) as exc:
                log_error(f"Failed to copy external file '{source_path}': {exc}", False)

    def _convert_record_object(self, record: Record_Object, level: int, translation: Optional[dict]) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Process the given record object.

        Args:
            record (Record_Object): The record object.
            level (int): The record level.
            translation (Optional[dict]): Translation dictionary for the record object.
                                            If None, no translation is applied.

        Returns:
            Ret: Status
        """
        assert self._document is not None

        # The record name will be the heading.
        self._document.add(Heading(record.name, self._get_markdown_heading_level(level + 1)))

        # The record fields will be written to a table.
        # First define the table column titles.
        table_column_titles = ["Attribute Name", "Attribute Value"]
        table_rows = []

        # Walk through the record object fields and build the table rows.
        trlc_ast_walker = self._get_trlc_ast_walker()

        for name, value in record.field.items():
            attribute_name = self._translate_attribute_name(translation, name)
            attribute_name = MarkdownText.escape(attribute_name)

            # Retrieve the attribute value by processing the field value.
            # The result will be a string representation of the value.
            # If the value is an array of record references, the result will be a Markdown list of links.
            # If the value is a single record reference, the result will be a Markdown link.
            # If the value is a string literal, the result will be the string literal value that considers
            # its formatting.
            # Otherwise the result will be the attribute value in a proper format.
            self._ast_meta_data = {
                "package_name": record.n_package.name,
                "type_name": record.n_typ.name,
                "attribute_name": name
            }
            walker_result = trlc_ast_walker.walk(value)

            attribute_value = ""
            if isinstance(walker_result, list):
                attribute_value = BulletList(walker_result, False).render()
            else:
                attribute_value = walker_result

            # Append the attribute name and value to the table rows.
            table_rows.append([attribute_name, attribute_value])

        self._document.add(Table(table_column_titles, table_rows))

        return Ret.OK

# Functions ********************************************************************

# Main *************************************************************************
