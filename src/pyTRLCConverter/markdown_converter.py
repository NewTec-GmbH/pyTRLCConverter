"""Converter to Markdown format.

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
import os
from typing import List, Optional
from trlc.ast import Implicit_Null, Record_Object, Record_Reference
from pyTRLCConverter.base_converter import BaseConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import TrlcAstWalker
from pyTRLCConverter.logger import log_verbose, log_error

# Variables ********************************************************************

# Classes **********************************************************************

# pylint: disable=too-many-instance-attributes
class MarkdownConverter(BaseConverter):
    """
    MarkdownConverter provides functionality for converting to a markdown format.
    """

    OUTPUT_FILE_NAME_DEFAULT = "output.md"
    TOP_LEVEL_DEFAULT = "Specification"

    def __init__(self, args: any) -> None:
        # lobster-trace: SwRequirements.sw_req_no_prj_spec
        # lobster-trace: SwRequirements.sw_req_markdown
        """
        Initializes the converter.

        Args:
            args (any): The parsed program arguments.
        """
        super().__init__(args)

        # The path to the given output folder.
        self._out_path = args.out

        # The excluded files in normalized form.
        self._excluded_files = []

        if args.exclude is not None:
            self._excluded_paths = [os.path.normpath(path) for path in args.exclude]

        # The file descriptor for the output file.
        self._fd = None

        # The base level for the headings. Its the minimum level for the headings which depends
        # on the single/multiple document mode.
        self._base_level = 1

        # For proper Markdown formatting, the first written Markdown part shall not have an empty line before.
        # But all following parts (heading, table, paragraph, image, etc.) shall have an empty line before.
        # And at the document bottom, there shall be just one empty line.
        self._empty_line_required = False

        # A top level heading is always required to generate a compliant Markdown document.
        # In single document mode it will always be necessary.
        # In multiple document mode only if there is no top level section.
        self._is_top_level_heading_req = True

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
    def register(cls, args_parser: any) -> None:
        # lobster-trace: SwRequirements.sw_req_markdown_multiple_doc_mode
        # lobster-trace: SwRequirements.sw_req_markdown_single_doc_mode
        # lobster-trace: SwRequirements.sw_req_markdown_top_level_default
        # lobster-trace: SwRequirements.sw_req_markdown_top_level_custom
        # lobster-trace: SwRequirements.sw_req_markdown_out_file_name_default
        # lobster-trace: SwRequirements.sw_req_markdown_out_file_name_custom
        """
        Register converter specific argument parser.

        Args:
            args_parser (any): Argument parser
        """
        super().register(args_parser)

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

    def begin(self) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_single_doc_mode
        # lobster-trace: SwRequirements.sw_req_markdown_sd_top_level
        """
        Begin the conversion process.

        Returns:
            Ret: Status
        """
        assert self._fd is None

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

            # Single document mode?
            if self._args.single_document is True:
                result = self._generate_out_file(self._args.name)

                if self._fd is not None:
                    self._write_top_level_heading_on_demand()

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
        result = Ret.OK

        # Multiple document mode?
        if self._args.single_document is False:
            assert self._fd is None

            file_name_md = self._file_name_trlc_to_md(file_name)
            result = self._generate_out_file(file_name_md)

            # The very first written Markdown part shall not have a empty line before.
            self._empty_line_required = False

        return result

    def leave_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_multiple_doc_mode
        """
        Leave a file.

        Args:
            file_name (str): File name

        Returns:
            Ret: Status
        """

        # Multiple document mode?
        if self._args.single_document is False:
            assert self._fd is not None
            self._fd.close()
            self._fd = None
            self._is_top_level_heading_req = True

        return Ret.OK

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
        assert self._fd is not None

        self._write_empty_line_on_demand()
        markdown_heading = self.markdown_create_heading(section, self._get_markdown_heading_level(level))
        self._fd.write(markdown_heading)

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
        assert self._fd is not None

        self._write_top_level_heading_on_demand()
        self._write_empty_line_on_demand()

        return self._convert_record_object(record, level, translation)

    def finish(self):
        # lobster-trace: SwRequirements.sw_req_markdown_single_doc_mode
        """
        Finish the conversion process.
        """

        # Single document mode?
        if self._args.single_document is True:
            assert self._fd is not None
            self._fd.close()
            self._fd = None

        return Ret.OK

    def _write_top_level_heading_on_demand(self) -> None:
        # lobster-trace: SwRequirements.sw_req_markdown_md_top_level
        # lobster-trace: SwRequirements.sw_req_markdown_sd_top_level
        """Write the top level heading if necessary.
        """
        if self._is_top_level_heading_req is True:
            self._fd.write(MarkdownConverter.markdown_create_heading(self._args.top_level, 1))
            self._empty_line_required = True
            self._is_top_level_heading_req = False

    def _write_empty_line_on_demand(self) -> None:
        # lobster-trace: SwRequirements.sw_req_markdown
        """
        Write an empty line if necessary.

        For proper Markdown formatting, the first written part shall not have an empty
        line before. But all following parts (heading, table, paragraph, image, etc.) shall
        have an empty line before. And at the document bottom, there shall be just one empty
        line.
        """
        if self._empty_line_required is False:
            self._empty_line_required = True
        else:
            self._fd.write("\n")

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

    def _generate_out_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_out_folder
        """
        Generate the output file.

        Args:
            file_name (str): The output file name without path.
            item_list ([Element]): List of elements.

        Returns:
            Ret: Status
        """
        result = Ret.OK
        file_name_with_path = file_name

        # Add path to the output file name.
        if 0 < len(self._out_path):
            file_name_with_path = os.path.join(self._out_path, file_name)

        try:
            self._fd = open(file_name_with_path, "w", encoding="utf-8") #pylint: disable=consider-using-with
        except IOError as e:
            log_error(f"Failed to open file {file_name_with_path}: {e}")
            result = Ret.ERROR

        return result

    def _on_implict_null(self, _: Implicit_Null) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Process the given implicit null value.
        
        Returns:
            str: The implicit null value
        """
        return self.markdown_escape(self._empty_attribute_value)

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

    # pylint: disable=line-too-long
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

        return MarkdownConverter.markdown_create_link(record_reference.to_python_object(), anchor_tag)

    def _get_trlc_ast_walker(self) -> TrlcAstWalker:
        # lobster-trace: SwRequirements.sw_req_markdown_record
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
        trlc_ast_walker.set_other_dispatcher(
            lambda expression: MarkdownConverter.markdown_escape(expression.to_python_object())
        )

        return trlc_ast_walker

    # pylint: disable=too-many-locals
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
        assert self._fd is not None

        # The record name will be the heading.
        markdown_heading = self.markdown_create_heading(record.name, self._get_markdown_heading_level(level + 1))
        self._fd.write(markdown_heading)
        self._fd.write("\n")

        # The record fields will be written to a table.
        # First write the table head.
        column_titles = ["Attribute Name", "Attribute Value"]
        markdown_table_head = self.markdown_create_table_head(column_titles)
        self._fd.write(markdown_table_head)

        # Walk through the record object fields and write the table rows.
        trlc_ast_walker = self._get_trlc_ast_walker()

        for name, value in record.field.items():
            # Translate the attribute name if available.
            attribute_name = name
            if translation is not None:
                if name in translation:
                    attribute_name = translation[name]

            attribute_name = self.markdown_escape(attribute_name)

            # Retrieve the attribute value by processing the field value.
            walker_result = trlc_ast_walker.walk(value)

            attribute_value = ""
            if isinstance(walker_result, list):
                # List every list item line by line.
                for idx, walker_result_item in enumerate(walker_result):
                    if 0 < idx:
                        attribute_value += "<br>"

                    attribute_value += walker_result_item

            else:
                attribute_value = walker_result

            # Write the attribute name and value to the Markdown table as row.
            markdown_table_row = self.markdown_append_table_row([attribute_name, attribute_value], False)
            self._fd.write(markdown_table_row)

        return Ret.OK

    @staticmethod
    def markdown_escape(text: str) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_escape
        """
        Escapes the text to be used in a Markdown document.

        Args:
            text (str): Text to escape

        Returns:
            str: Escaped text
        """
        characters = ["\\", "`", "*", "_", "{", "}", "[", "]", "<", ">", "(", ")", "#", "+", "-", ".", "!", "|"]

        for character in characters:
            text = text.replace(character, "\\" + character)

        return text

    @staticmethod
    def markdown_lf2soft_return(text: str) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_soft_return
        """
        A single LF will be converted to backslash + LF.
        Use it for paragraphs, but not for headings or tables.

        Args:
            text (str): Text
        Returns:
            str: Handled text
        """
        return text.replace("\n", "\\\n")

    @staticmethod
    def markdown_create_heading(text: str, level: int, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_heading
        """
        Create a Markdown heading.
        The text will be automatically escaped for Markdown if necessary.

        Args:
            text (str): Heading text
            level (int): Heading level [1; inf]
            escape (bool): Escape the text (default: True).

        Returns:
            str: Markdown heading
        """
        result = ""

        if 1 <= level:
            text_raw = text

            if escape is True:
                text_raw = MarkdownConverter.markdown_escape(text)

            result = f"{'#' * level} {text_raw}\n"

        else:
            log_error(f"Invalid heading level {level} for {text}.")

        return result

    @staticmethod
    def markdown_create_table_head(column_titles : List[str], escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_table
        """
        Create the table head for a Markdown table.
        The titles will be automatically escaped for Markdown if necessary.

        Args:
            column_titles ([str]): List of column titles.
            escape (bool): Escape the titles (default: True).

        Returns:
            str: Table head
        """
        table_head = "|"

        for column_title in column_titles:
            column_title_raw = column_title

            if escape is True:
                column_title_raw = MarkdownConverter.markdown_escape(column_title)

            table_head += f" {column_title_raw} |"

        table_head += "\n"

        table_head += "|"

        for column_title in column_titles:
            column_title_raw = column_title

            if escape is True:
                column_title_raw = MarkdownConverter.markdown_escape(column_title)

            table_head += " "

            for _ in range(len(column_title_raw)):
                table_head += "-"

            table_head += " |"

        table_head += "\n"

        return table_head

    @staticmethod
    def markdown_append_table_row(row_values: List[str], escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_table
        """
        Append a row to a Markdown table.
        The values will be automatically escaped for Markdown if necessary.

        Args:
            row_values ([str]): List of row values.
            escape (bool): Escapes every row value (default: True).

        Returns:
            str: Table row
        """
        table_row = "|"

        for row_value in row_values:
            row_value_raw = row_value

            if escape is True:
                row_value_raw = MarkdownConverter.markdown_escape(row_value)

            # Replace every LF with a HTML <br>.
            row_value_raw = row_value_raw.replace("\n", "<br>")

            table_row += f" {row_value_raw} |"

        table_row += "\n"

        return table_row

    @staticmethod
    def markdown_create_link(text: str, url: str, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_link
        """
        Create a Markdown link.
        The text will be automatically escaped for Markdown if necessary.
        There will be no newline appended at the end.

        Args:
            text (str): Link text
            url (str): Link URL
            escape (bool): Escapes text (default: True).

        Returns:
            str: Markdown link
        """
        text_raw = text

        if escape is True:
            text_raw = MarkdownConverter.markdown_escape(text)

        return f"[{text_raw}]({url})"

    @staticmethod
    def markdown_create_diagram_link(diagram_file_name: str, diagram_caption: str, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_image
        """
        Create a Markdown diagram link.
        The caption will be automatically escaped for Markdown if necessary.

        Args:
            diagram_file_name (str): Diagram file name
            diagram_caption (str): Diagram caption
            escape (bool): Escapes caption (default: True).

        Returns:
            str: Markdown diagram link
        """
        diagram_caption_raw = diagram_caption

        if escape is True:
            diagram_caption_raw = MarkdownConverter.markdown_escape(diagram_caption)

        # Allowed are absolute and relative to source paths.
        diagram_file_name = os.path.normpath(diagram_file_name)

        return f"![{diagram_caption_raw}]({diagram_file_name})\n"

    @staticmethod
    def markdown_text_color(text: str, color: str, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_text_color
        """
        Create colored text in Markdown.
        The text will be automatically escaped for Markdown if necessary.
        There will be no newline appended at the end.

        Args:
            text (str): Text
            color (str): HTML color
            escape (bool): Escapes text (default: True).

        Returns:
            str: Colored text
        """
        text_raw = text

        if escape is True:
            text_raw = MarkdownConverter.markdown_escape(text)

        return f"<span style=\"{color}\">{text_raw}</span>"

# Functions ********************************************************************

# Main *************************************************************************
