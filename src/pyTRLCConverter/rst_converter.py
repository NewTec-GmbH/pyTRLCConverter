"""Converter to reStructuredText format.

    Author: Gabryel Reyes (gabryel.reyes@newtec.de)
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
import shutil
import tempfile
from typing import Optional, Any
from marko import Markdown
from trlc.ast import Implicit_Null, Record_Object, Record_Reference, String_Literal, Expression
from pyTRLCConverter.base_converter import BaseConverter
from pyTRLCConverter.rst.document import RstDocument
from pyTRLCConverter.rst.element import RstHeading, RstAdmonition, RstTable, RstBulletList
from pyTRLCConverter.rst.text import RstText
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import TrlcAstWalker
from pyTRLCConverter.logger import log_verbose, log_error
from pyTRLCConverter.marko.md2rst_renderer import Md2RstRenderer
from pyTRLCConverter.marko.gfm2rst_renderer import Gfm2RstRenderer

# Variables ********************************************************************

# Classes **********************************************************************

# pylint: disable-next=too-many-instance-attributes
class RstConverter(BaseConverter):
    """
    RstConverter provides functionality for converting to a reStructuredText format.

    The converter builds a reStructuredText AST (RstDocument made of block
    elements) while walking the TRLC symbols and writes the output file(s) only
    once the document is complete (in leave_file() for multiple-document mode and
    in finish() for single-document mode).
    """
    OUTPUT_FILE_NAME_DEFAULT = "output.rst"
    TOP_LEVEL_DEFAULT = "Specification"

    def __init__(self, args: Any) -> None:
        # lobster-trace: SwRequirements.sw_req_rst
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

        # The reStructuredText document currently being built. In multiple-document mode a new
        # document is created per file, in single-document mode one document is shared.
        self._document: Optional[RstDocument] = None

        # The base name of the output file currently being built. It is used to build the
        # labels of headings and admonitions.
        self._current_file_name = ""

        # The base level for the headings. Its the minimum level for the headings which depends
        # on the single/multiple document mode.
        self._base_level = 1

        # The AST walker meta data for processing the record object fields.
        # This will hold the information about the current package, type and attribute being processed.
        self._ast_meta_data = None

        self._plantuml_tmp_dir: Optional[tempfile.TemporaryDirectory] = None
        self._external_files: list = []

    @staticmethod
    def get_subcommand() -> str:
        # lobster-trace: SwRequirements.sw_req_rst
        """
        Return subcommand token for this converter.

        Returns:
            str: Parser subcommand token
        """
        return "rst"

    @staticmethod
    def get_description() -> str:
        # lobster-trace: SwRequirements.sw_req_rst
        """
        Return converter description.

        Returns:
            str: Converter description
        """
        return "Convert into reStructuredText format."

    @classmethod
    def register(cls, args_parser: Any) -> None:
        # lobster-trace: SwRequirements.sw_req_rst_multiple_doc_mode
        # lobster-trace: SwRequirements.sw_req_rst_single_doc_mode
        # lobster-trace: SwRequirements.sw_req_rst_sd_top_level_default
        # lobster-trace: SwRequirements.sw_req_rst_sd_top_level_custom
        # lobster-trace: SwRequirements.sw_req_rst_out_file_name_default
        # lobster-trace: SwRequirements.sw_req_rst_out_file_name_custom
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
            default=RstConverter.OUTPUT_FILE_NAME_DEFAULT,
            required=False,
            help="Name of the generated output file inside the output folder " \
                f"(default = {RstConverter.OUTPUT_FILE_NAME_DEFAULT}) in " \
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
            default=RstConverter.TOP_LEVEL_DEFAULT,
            required=False,
            help="Name of the top level heading, required in single document mode " \
                f"(default = {RstConverter.TOP_LEVEL_DEFAULT})."
        )

    def begin(self) -> Ret:
        # lobster-trace: SwRequirements.sw_req_rst_single_doc_mode
        # lobster-trace: SwRequirements.sw_req_rst_sd_top_level
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

            # pylint: disable-next=consider-using-with
            self._plantuml_tmp_dir = tempfile.TemporaryDirectory(prefix="pyTRLCConverter_rst_")

            # Single document mode?
            if self._args.single_document is True:
                self._document = RstDocument()
                self._current_file_name = self._args.name

                # The top level heading is always required in single document mode.
                self._document.add(RstHeading(self._args.top_level, 1, self._current_file_name))

                # All headings will be shifted by one level.
                self._base_level = self._base_level + 1

        return result

    def enter_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_rst_multiple_doc_mode
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

            # A new document is built for each file. The very first written part shall not have
            # an empty line before, which the document handles implicitly.
            self._document = RstDocument()
            self._current_file_name = self._file_name_trlc_to_rst(file_name)

        return Ret.OK

    def leave_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_rst_multiple_doc_mode
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

            result = self._write_document(self._current_file_name)

            self._copy_external_files(self._out_path)
            self._external_files = []
            self._document = None

        return result

    def convert_section(self, section: str, level: int) -> Ret:
        # lobster-trace: SwRequirements.sw_req_rst_section
        """
        Process the given section item.
        It will create a reStructuredText heading with the given section name and level.

        Args:
            section (str): The section name
            level (int): The section indentation level

        Returns:
            Ret: Status
        """
        assert len(section) > 0
        assert self._document is not None

        self._document.add(RstHeading(section, self._get_rst_heading_level(level), self._current_file_name))

        return Ret.OK

    def convert_record_object_generic(self, record: Record_Object, level: int, translation: Optional[dict]) -> Ret:
        # lobster-trace: SwRequirements.sw_req_rst_record
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

        return self._convert_record_object(record, level, translation)

    def finish(self):
        # lobster-trace: SwRequirements.sw_req_rst_single_doc_mode
        """
        Finish the conversion process.

        Returns:
            Ret: Status
        """
        result = Ret.OK

        # Single document mode?
        if self._args.single_document is True:
            assert self._document is not None

            result = self._write_document(self._current_file_name)

            self._copy_external_files(self._out_path)
            self._external_files = []
            self._document = None

        if self._plantuml_tmp_dir is not None:
            self._plantuml_tmp_dir.cleanup()
            self._plantuml_tmp_dir = None

        return result

    def _get_rst_heading_level(self, level: int) -> int:
        # lobster-trace: SwRequirements.sw_req_rst_section
        """
        Get the reStructuredText heading level from the TRLC object level.
        Its mandatory to use this method to calculate the reStructuredText heading level.
        Otherwise in single document mode the top level heading will be wrong.

        Args:
            level (int): The TRLC object level.

        Returns:
            int: reStructuredText heading level
        """
        return self._base_level + level

    def _file_name_trlc_to_rst(self, file_name_trlc: str) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_multiple_doc_mode
        """
        Convert a TRLC file name to a reStructuredText file name.

        Args:
            file_name_trlc (str): TRLC file name

        Returns:
            str: reStructuredText file name
        """
        file_name = os.path.basename(file_name_trlc)
        file_name = os.path.splitext(file_name)[0] + ".rst"

        return file_name

    def _write_document(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_rst_out_folder
        """
        Write the current reStructuredText document to the output file.

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

    def _on_implicit_null(self, _: Implicit_Null) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_record
        """
        Process the given implicit null value.

        Returns:
            str: The implicit null value.
        """
        return RstText.escape(self._empty_attribute_value)

    def _on_record_reference(self, record_reference: Record_Reference) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_record
        """
        Process the given record reference value and return a reStructuredText link.

        Args:
            record_reference (Record_Reference): The record reference value.

        Returns:
            str: reStructuredText link to the record reference.
        """
        return self._create_rst_link_from_record_object_reference(record_reference)

    def _on_string_literal(self, string_literal: String_Literal) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_string_format
        # lobster-trace: SwRequirements.sw_req_rst_render_md
        # lobster-trace: SwRequirements.sw_req_rst_render_gfm
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

    def _create_rst_link_from_record_object_reference(self, record_reference: Record_Reference) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_link
        """
        Create a reStructuredText cross-reference from a record reference.
        It considers the file name, the package name, and the record name.

        Args:
            record_reference (Record_Reference): Record reference

        Returns:
            str: reStructuredText cross-reference
        """
        assert record_reference.target is not None

        file_name = ""

        # Single document mode?
        if self._args.single_document is True:
            file_name = self._args.name

            # Is the link to a excluded file?
            for excluded_path in self._excluded_paths:

                if os.path.commonpath([excluded_path, record_reference.target.location.file_name]) == excluded_path:
                    file_name = self._file_name_trlc_to_rst(record_reference.target.location.file_name)
                    break

        # Multiple document mode
        else:
            file_name = self._file_name_trlc_to_rst(record_reference.target.location.file_name)

        record_name = record_reference.target.name

        # Create a target ID for the record
        target_id = f"{file_name}-{record_name.lower().replace(' ', '-')}"

        return RstText.link(str(record_reference.to_python_object()), target_id)

    def _other_dispatcher(self, expression: Expression) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_record
        # lobster-trace: SwRequirements.sw_req_rst_escape
        """
        Dispatcher for all other expressions.

        Args:
            expression (Expression): The expression to process.

        Returns:
            str: The processed expression.
        """
        return RstText.escape(expression.to_string())

    def _get_trlc_ast_walker(self) -> TrlcAstWalker:
        # lobster-trace: SwRequirements.sw_req_rst_record
        # lobster-trace: SwRequirements.sw_req_rst_escape
        # lobster-trace: SwRequirements.sw_req_rst_string_format
        """
        If a record object contains a record reference, the record reference will be converted to
        a Markdown link.
        If a record object contains an array of record references, the array will be converted to
        a reStructuredText list of links.
        Otherwise the record object fields attribute values will be written to the reStructuredText table.

        Returns:
            TrlcAstWalker: The TRLC AST walker.
        """
        trlc_ast_walker = TrlcAstWalker()
        trlc_ast_walker.add_dispatcher(
            Implicit_Null,
            None,
            self._on_implicit_null,
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
        # lobster-trace: SwRequirements.sw_req_rst_string_format
        # lobster-trace: SwRequirements.sw_req_rst_render_md
        # lobster-trace: SwRequirements.sw_req_rst_render_gfm
        # lobster-trace: SwRequirements.sw_req_rst_render_plantuml
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

        # If the attribute value is not already in reStructuredText format, it will be escaped.
        if self._render_cfg.is_format_rst(package_name, type_name, attribute_name) is False:

            # Is it CommonMark Markdown format?
            if self._render_cfg.is_format_md(package_name, type_name, attribute_name) is True:
                assert self._plantuml_tmp_dir is not None
                Md2RstRenderer.image_dir = self._plantuml_tmp_dir.name
                Md2RstRenderer.external_files = self._external_files
                markdown = Markdown(renderer=Md2RstRenderer)
                result = markdown.convert(attribute_value)

            # Is it GitHub Flavored Markdown format?
            elif self._render_cfg.is_format_gfm(package_name, type_name, attribute_name) is True:
                assert self._plantuml_tmp_dir is not None
                Md2RstRenderer.image_dir = self._plantuml_tmp_dir.name
                Md2RstRenderer.external_files = self._external_files
                markdown = Markdown(renderer=Gfm2RstRenderer, extensions=['gfm'])
                result = markdown.convert(attribute_value)

            # Otherwise escape the text for reStructuredText.
            else:
                result = RstText.escape(attribute_value)

        return result

    def _copy_external_files(self, dest_dir: str) -> None:
        # lobster-trace: SwRequirements.sw_req_rst_render_plantuml
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

    # pylint: disable-next=unused-argument
    def _convert_record_object(self, record: Record_Object, level: int, translation: Optional[dict]) -> Ret:
        # lobster-trace: SwRequirements.sw_req_rst_record
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

        # The record name will be the admonition.
        self._document.add(RstAdmonition(record.name, self._current_file_name))

        # The record fields will be written to a table.
        column_titles = ["Attribute Name", "Attribute Value"]

        # Build rows for the table.
        rows = []
        trlc_ast_walker = self._get_trlc_ast_walker()
        for name, value in record.field.items():
            attribute_name = self._translate_attribute_name(translation, name)
            attribute_name = RstText.escape(attribute_name)

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
                attribute_value = RstBulletList(walker_result, False).render()
            else:
                attribute_value = walker_result

            rows.append([attribute_name, attribute_value])

        self._document.add(RstTable(column_titles, rows))

        return Ret.OK

# Functions ********************************************************************

# Main *************************************************************************
