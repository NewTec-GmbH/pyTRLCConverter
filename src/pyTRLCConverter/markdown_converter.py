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
import sys
from typing import List, Optional
from trlc import trlc
from pyTRLCConverter.base_converter import BaseConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import Record_Object
from pyTRLCConverter.log_verbose import log_verbose

# Variables ********************************************************************

# Classes **********************************************************************

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

        # The file descriptor for the output file. Used in single and multiple document mode.
        self._fd = None

        # The base level for the headings. Its the minimum level for the headings which depends
        # on the single/multiple document mode.
        self._base_level = 1

        # For proper Markdown formatting, the first written Markdown part shall not have an empty line before.
        # But all following parts (heading, table, paragraph, image, etc.) shall have an empty line before.
        # And at the document bottom, there shall be just one empty line.
        self._empty_line_required = False

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
        # lobster-trace: SwRequirements.sw_req_markdown_sd_top_level_default
        # lobster-trace: SwRequirements.sw_req_markdown_sd_top_level_custom
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
            help="Every attribute value which is empty will output the string." \
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
            help="Name of the top level heading, required in single document mode. " \
                f"(default = {MarkdownConverter.TOP_LEVEL_DEFAULT})"
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

        result = Ret.OK

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
                self._fd.write(MarkdownConverter.markdown_create_heading(self._args.top_level, 1))

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

        return Ret.OK

    def convert_section(self, section: str, level: int) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_section
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

        return Ret.OK

    def convert_record_object_generic(self, record: Record_Object, level: int) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Process the given record object.

        Args:
            record (Record_Object): The record object
            level (int): The record level
        
        Returns:
            Ret: Status
        """
        assert self._fd is not None

        self._write_empty_line_on_demand()
        return self._convert_record_object(record, level, None)

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

    def _write_empty_line_on_demand(self) -> None:
        # lobster-trace: SwRequirements.sw_req_markdown
        """
        Write an empty line if necessary.
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
            print(f"Failed to open file {file_name_with_path}: {e}", file=sys.stderr)
            result = Ret.ERROR

        return result

    def _on_implict_null(self, _) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Process the given implicit null value.
        
        Returns:
            str: The implicit null value
        """
        return self._empty_attribute_value

    def _on_array_aggregate(self, value: trlc.ast.Array_Aggregate) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Process the given array aggregate value.
        It will process the array elements recursively.
        Each element will be separated by a comma.

        Args:
            value (trlc.ast.Array_Aggregate): The array aggregate value.
        
        Returns:
            str: A comma separated list of array element names or Markdown links.
        """
        result = ""

        dispatcher_map = {
            trlc.ast.Implicit_Null: self._on_implict_null,
            trlc.ast.Array_Aggregate: self._on_array_aggregate,
            trlc.ast.Record_Reference: self._on_record_reference
        }

        if len(value.value) > 0:
            type_name = type(value.value[0])
            if type_name in dispatcher_map:
                for idx, item in enumerate(value.value):
                    if idx > 0:
                        result += ", "

                    result += dispatcher_map[type_name](item)
            else:
                result = self.markdown_escape(value.to_python_object())

        return result

    def _on_record_reference(self, value: trlc.ast.Record_Reference) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Process the given record reference value and return a markdown link.

        Args:
            value (trlc.ast.Record_Reference): The record reference value.
        
        Returns:
            str: Markdown link to the record reference.
        """
        return self._create_markdown_link_from_record_object_reference(value)

    def _on_field(self, value: trlc.ast.Expression) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Process the given field value and return it as a string.
        The main purpose is to handle arrays and record references explicitly.
        A record reference will be converted into a markdown link.

        Args:
            value (trlc.ast.Expression): The field value
        
        Returns:
            str: The field value
        """
        result = ""

        dispatcher_map = {
            trlc.ast.Implicit_Null: self._on_implict_null,
            trlc.ast.Array_Aggregate: self._on_array_aggregate,
            trlc.ast.Record_Reference: self._on_record_reference
        }

        type_name = type(value)
        if type_name in dispatcher_map:
            result = dispatcher_map[type_name](value)
        else:
            result = self.markdown_escape(value.to_python_object())

        return result

    def _create_markdown_link_from_record_object_reference(self, record_reference: trlc.ast.Record_Reference) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Create a Markdown link from a record reference.
        It considers the file name, the package name, and the record name.

        Args:
            record_reference (trlc.ast.Record_Reference): Record reference

        Returns:
            str: Markdown link
        """
        file_name = ""

        # Single document mode?
        if self._args.single_document is True:
            file_name = self._args.name

        # Multiple document mode
        else:
            file_name = self._file_name_trlc_to_md(record_reference.target.location.file_name)

        record_name = record_reference.target.name

        anchor_tag = file_name + "#" + record_name.lower().replace(" ", "-")

        return MarkdownConverter.markdown_create_link(record_reference.to_python_object(), anchor_tag)

    def _convert_record_object(self, record: Record_Object, level: int, attribute_translation: Optional[dict]) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_record
        """
        Process the given record object.

        Args:
            record (Record_Object): The record object.
            level (int): The record level.
            attribute_translation (Optional[dict]): Attribute translation (attribute name -> user friendly name).
        
        Returns:
            Ret: Status
        """
        markdown_heading = self.markdown_create_heading(record.name, self._get_markdown_heading_level(level + 1))
        self._fd.write(markdown_heading)
        self._fd.write("\n")

        column_titles = ["Attribute Name", "Attribute Value"]
        markdown_table_head = self.markdown_create_table_head(column_titles)
        self._fd.write(markdown_table_head)

        for name, value in record.field.items():
            # Translate the attribute name if available.
            attribute_name = name
            if attribute_translation is not None:
                if name in attribute_translation:
                    attribute_name = attribute_translation[name]

            attribute_name = self.markdown_escape(attribute_name)

            # Retrieve the attribute value by processing the field value.
            attribute_value = self._on_field(value)

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
    def markdown_create_heading(text: str, level: int, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_heading
        """
        Create a Markdown heading.
        The text will be automatically escaped for Markdown if necessary.

        Args:
            text (str): Heading text
            level (int): Heading level
            escape (bool): Escape the text (default: True).

        Returns:
            str: Markdown heading
        """
        text_raw = text

        if escape is True:
            text_raw = MarkdownConverter.markdown_escape(text)

        return f"{'#' * level} {text_raw}\n"

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

        return f"![{diagram_caption_raw}](./{diagram_file_name})\n"

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
