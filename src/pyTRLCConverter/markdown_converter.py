"""Converter to Markdown format.

    Author: Andreas Merkle (andreas.merkle@newtec.de)
"""

# pyTRLCConverter - A tool to convert PlantUML diagrams to image files.
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
from typing import List
from pyTRLCConverter.base_converter import BaseConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************

class MarkdownConverter(BaseConverter):
    """MarkdownConverter provides functionality for converting to a markdown format.
    """

    def __init__(self, args: any) -> None:
        # lobster-trace: SwRequirements.sw_req_markdown
        """Initializes the converter.
        """
        super().__init__(args)

        self._out_path = args.out
        self._fd = None

    @staticmethod
    def get_subcommand() -> str:
        """ Return subcommand token for this converter.

        Returns:
            str: Parser subcommand token
        """
        return "markdown"

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

        Returns:
            str: Converter description
        """
        return "Convert into markdown format."

    def enter_file(self, file_name: str) -> Ret:
        """Enter a file.

        Args:
            file_name (str): File name
        
        Returns:
            Ret: Status
        """

        return self._generate_out_file(file_name)

    def leave_file(self, file_name: str) -> Ret:
        """Leave a file.

        Args:
            file_name (str): File name

        Returns:
            Ret: Status
        """
        if self._fd is not None:
            self._fd.close()
            self._fd = None

        return Ret.OK

    def convert_section(self, section: str, level: int) -> Ret:
        """Process the given section item.

        Args:
            section (str): The section name
            level (int): The section indentation level
        
        Returns:
            Ret: Status
        """
        self._fd.write(f"{'#' * (level + 1)} {section}\n\n")

        return Ret.OK

    def convert_record_object(self, record: Record_Object, level: int) -> Ret:
        """Process the given record object.

        Args:
            record (Record_Object): The record object
            level (int): The record level
        
        Returns:
            Ret: Status
        """
        self._fd.write(f"{record.name}\n")
        self._fd.write(f"{record.to_python_dict()}\n\n")
        return Ret.OK

    def finish(self) -> Ret:
        """Finish the conversion process.

        Returns:
            Ret: Status
        """
        return Ret.OK

    def _generate_out_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_markdown_out_folder
        """Generate the output file.

        Args:
            file_name (str): File name of the input file.
            item_list ([Element]): List of elements.

        Returns:
            Ret: Status
        """
        result = Ret.OK
        input_file_name = os.path.basename(file_name)
        output_file_name = os.path.splitext(input_file_name)[0] + ".md"

        # Add path to the output file name.
        if 0 < len(self._out_path):
            output_file_name = os.path.join(self._out_path, output_file_name)

        try:
            self._fd = open(output_file_name, "w", encoding="utf-8") #pylint: disable=consider-using-with
        except IOError as e:
            print(f"Failed to open file {output_file_name}: {e}", file=sys.stderr)
            result = Ret.ERROR

        return result

    @staticmethod
    def markdown_escape(text: str) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_escape
        """Escapes the text to be used in a Markdown document.

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
        """Create a Markdown heading.
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

        return f"{'#' * level} {text_raw}\n\n"

    @staticmethod
    def markdown_create_table_head(column_titles : List[str], escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_table
        """Create the table head for a Markdown table.
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

            for _ in range(len(column_title_raw)):
                table_head += "-"

            table_head += " |"

        table_head += "\n"

        return table_head

    @staticmethod
    def markdown_append_table_row(row_values: List[str], escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_markdown_table_row
        """Append a row to a Markdown table.
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
        """Create a Markdown link.
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
        """Create a Markdown diagram link.
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

# Main *************************************************************************
