"""Converter to reStructuredText format.

    Author: Gabryel Reyes (gabryel.reyes@newtec.de)
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

class RstConverter(BaseConverter):
    """
    RstConverter provides functionality for converting to a reStructuredText format.
    """
    OUTPUT_FILE_NAME_DEFAULT = "output.rst"
    TOP_LEVEL_DEFAULT = "Specification"

    def __init__(self, args: any) -> None:
        # lobster-trace: SwRequirements.sw_req_rst
        """
        Initializes the converter.

        Args:
            args (any): The parsed program arguments.
        """
        super().__init__(args)

        # The path to the given output folder.
        self._out_path = args.out

        # The excluded paths in normalized form.
        self._excluded_paths = []

        if args.exclude is not None:
            self._excluded_paths = [os.path.normpath(path) for path in args.exclude]

        # The file descriptor for the output file.
        self._fd = None

        # The base level for the headings. Its the minimum level for the headings which depends
        # on the single/multiple document mode.
        self._base_level = 1

        # For proper reStructuredText formatting, the first written part shall not have an empty line before.
        # But all following parts (heading, table, paragraph, image, etc.) shall have an empty line before.
        # And at the document bottom, there shall be just one empty line.
        self._empty_line_required = False

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
    def register(cls, args_parser: any) -> None:
        # lobster-trace: SwRequirements.sw_req_rst_multiple_doc_mode
        # lobster-trace: SwRequirements.sw_req_rst_single_doc_mode
        # lobster-trace: SwRequirements.sw_req_rst_sd_top_level_default
        # lobster-trace: SwRequirements.sw_req_rst_sd_top_level_custom
        # lobster-trace: SwRequirements.sw_req_rst_out_file_name_default
        # lobster-trace: SwRequirements.sw_req_rst_out_file_name_custom
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
                    self._write_empty_line_on_demand()
                    self._fd.write(RstConverter.rst_create_heading(self._args.top_level, 1, self._args.name))

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
        result = Ret.OK

        # Multiple document mode?
        if self._args.single_document is False:
            assert self._fd is None

            file_name_rst = self._file_name_trlc_to_rst(file_name)
            result = self._generate_out_file(file_name_rst)

            # The very first written reStructuredText part shall not have an empty line before.
            self._empty_line_required = False

        return result

    def leave_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_rst_multiple_doc_mode
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
        assert self._fd is not None

        self._write_empty_line_on_demand()
        rst_heading = self.rst_create_heading(section,
                                            self._get_rst_heading_level(level),
                                            os.path.basename(self._fd.name))
        self._fd.write(rst_heading)

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
        assert self._fd is not None

        self._write_empty_line_on_demand()

        return self._convert_record_object(record, level, translation)

    def finish(self):
        # lobster-trace: SwRequirements.sw_req_rst_single_doc_mode
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
        # lobster-trace: SwRequirements.sw_req_rst
        """
        Write an empty line if necessary.

        For proper reStructuredText formatting, the first written part shall not have an empty
        line before. But all following parts (heading, table, paragraph, image, etc.) shall
        have an empty line before. And at the document bottom, there shall be just one empty
        line.
        """
        if self._empty_line_required is False:
            self._empty_line_required = True
        else:
            self._fd.write("\n")

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

    def _generate_out_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_rst_out_folder
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
        # lobster-trace: SwRequirements.sw_req_rst_record
        """
        Process the given implicit null value.
        
        Returns:
            str: The implicit null value
        """
        return self.rst_escape(self._empty_attribute_value)

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

        return RstConverter.rst_create_link(record_reference.to_python_object(), target_id)

    def _get_trlc_ast_walker(self) -> TrlcAstWalker:
        # lobster-trace: SwRequirements.sw_req_rst_record
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
            lambda expression: RstConverter.rst_escape(expression.to_python_object())
        )

        return trlc_ast_walker

    # pylint: disable=too-many-locals, unused-argument
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
        assert self._fd is not None

         # The record name will be the admonition.
        file_name = os.path.basename(self._fd.name)
        rst_heading = self.rst_create_admonition(record.name,
                                                 file_name)
        self._fd.write(rst_heading)

        self._write_empty_line_on_demand()

        # The record fields will be written to a table.
        column_titles = ["Attribute Name", "Attribute Value"]

        # Build rows for the table.
        # Its required to calculate the maximum width for each column, therefore the rows
        # will be stored first in a list and then the maximum width will be calculated.
        # The table will be written after the maximum width calculation.
        rows = []
        trlc_ast_walker = self._get_trlc_ast_walker()
        for name, value in record.field.items():
            attribute_name = name
            if translation is not None and name in translation:
                attribute_name = translation[name]
            attribute_name = self.rst_escape(attribute_name)

            # Retrieve the attribute value by processing the field value.
            walker_result = trlc_ast_walker.walk(value)

            attribute_value = ""
            if isinstance(walker_result, list):
                # List every list item line by line.
                for idx, walker_result_item in enumerate(walker_result):
                    if 0 < idx:
                        attribute_value += "\n"

                    attribute_value += walker_result_item

            else:
                attribute_value = walker_result

            rows.append([attribute_name, attribute_value])

        # Calculate the maximum width of each column based on both headers and row values.
        max_widths = [len(title) for title in column_titles]
        for row in rows:
            for idx, value in enumerate(row):
                lines = value.split('\n')
                for line in lines:
                    max_widths[idx] = max(max_widths[idx], len(line))

        # Write the table head and rows.
        rst_table_head = self.rst_create_table_head(column_titles, max_widths)
        self._fd.write(rst_table_head)

        for row in rows:
            rst_table_row = self.rst_append_table_row(row, max_widths, False)
            self._fd.write(rst_table_row)

        return Ret.OK

    @staticmethod
    def rst_escape(text: str) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_escape
        """
        Escapes the text to be used in a reStructuredText document.

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
    def rst_create_heading(text: str,
                           level: int,
                           file_name: str,
                           escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_heading
        """
        Create a reStructuredText heading with a label.
        The text will be automatically escaped for reStructuredText if necessary.

        Args:
            text (str): Heading text
            level (int): Heading level [1; 7]
            file_name (str): File name where the heading is found
            escape (bool): Escape the text (default: True).

        Returns:
            str: reStructuredText heading with a label
        """
        result = ""

        if 1 <= level <= 7:
            text_raw = text

            if escape is True:
                text_raw = RstConverter.rst_escape(text)

            label = f"{file_name}-{text_raw.lower().replace(' ', '-')}"

            underline_char = ["=", "#", "~", "^", "\"", "+", "'"][level - 1]
            underline = underline_char * len(text_raw)

            result = f".. _{label}:\n\n{text_raw}\n{underline}\n"

        else:
            log_error(f"Invalid heading level {level} for {text}.")

        return result

    @staticmethod
    def rst_create_admonition(text: str,
                              file_name: str,
                              escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_admonition
        """
        Create a reStructuredText admonition with a label.
        The text will be automatically escaped for reStructuredText if necessary.

        Args:
            text (str): Admonition text
            file_name (str): File name where the heading is found
            escape (bool): Escape the text (default: True).

        Returns:
            str: reStructuredText admonition with a label
        """
        text_raw = text

        if escape is True:
            text_raw = RstConverter.rst_escape(text)

        label = f"{file_name}-{text_raw.lower().replace(' ', '-')}"
        admonition_label = f".. admonition:: {text_raw}"

        return f".. _{label}:\n\n{admonition_label}\n"

    @staticmethod
    def rst_create_table_head(column_titles: List[str], max_widths: List[int], escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_table
        """
        Create the table head for a reStructuredText table in grid format.
        The titles will be automatically escaped for reStructuredText if necessary.

        Args:
            column_titles ([str]): List of column titles.
            max_widths ([int]): List of maximum widths for each column.
            escape (bool): Escape the titles (default: True).

        Returns:
            str: Table head
        """
        if escape:
            column_titles = [RstConverter.rst_escape(title) for title in column_titles]

        # Create the top border of the table
        table_head = "    +" + "+".join(["-" * (width + 2) for width in max_widths]) + "+\n"

        # Create the title row
        table_head += "    |"
        table_head += "|".join([f" {title.ljust(max_widths[idx])} " for idx, title in enumerate(column_titles)]) + "|\n"

        # Create the separator row
        table_head += "    +" + "+".join(["=" * (width + 2) for width in max_widths]) + "+\n"

        return table_head

    @staticmethod
    def rst_append_table_row(row_values: List[str], max_widths: List[int], escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_table
        """
        Append a row to a reStructuredText table in grid format.
        The values will be automatically escaped for reStructuredText if necessary.
        Supports multi-line cell values.

        Args:
            row_values ([str]): List of row values.
            max_widths ([int]): List of maximum widths for each column.
            escape (bool): Escapes every row value (default: True).

        Returns:
            str: Table row
        """
        if escape:
            row_values = [RstConverter.rst_escape(value) for value in row_values]

        # Split each cell value into lines.
        split_values = [value.split('\n') for value in row_values]
        max_lines = max(len(lines) for lines in split_values)

        # Create the row with multi-line support.
        table_row = ""
        for line_idx in range(max_lines):
            table_row += "    |"
            for col_idx, lines in enumerate(split_values):
                if line_idx < len(lines):
                    table_row += f" {lines[line_idx].ljust(max_widths[col_idx])} "
                else:
                    table_row += " " * (max_widths[col_idx] + 2)
                table_row += "|"
            table_row += "\n"

        # Create the separator row.
        separator_row = "    +" + "+".join(["-" * (width + 2) for width in max_widths]) + "+\n"

        return table_row + separator_row

    @staticmethod
    def rst_create_link(text: str, target: str, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_link
        """
        Create a reStructuredText cross-reference.
        The text will be automatically escaped for reStructuredText if necessary.
        There will be no newline appended at the end.

        Args:
            text (str): Link text
            target (str): Cross-reference target
            escape (bool): Escapes text (default: True).

        Returns:
            str: reStructuredText cross-reference
        """
        text_raw = text

        if escape is True:
            text_raw = RstConverter.rst_escape(text)

        return f":ref:`{text_raw} <{target}>`"

    @staticmethod
    def rst_create_diagram_link(diagram_file_name: str, diagram_caption: str, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_image
        """
        Create a reStructuredText diagram link.
        The caption will be automatically escaped for reStructuredText if necessary.

        Args:
            diagram_file_name (str): Diagram file name
            diagram_caption (str): Diagram caption
            escape (bool): Escapes caption (default: True).

        Returns:
            str: reStructuredText diagram link
        """
        diagram_caption_raw = diagram_caption

        if escape is True:
            diagram_caption_raw = RstConverter.rst_escape(diagram_caption)

        # Allowed are absolute and relative to source paths.
        diagram_file_name = os.path.normpath(diagram_file_name)

        result =  f".. figure:: {diagram_file_name}\n    :alt: {diagram_caption_raw}\n"

        if diagram_caption_raw:
            result += f"\n    {diagram_caption_raw}\n"

        return result

    @staticmethod
    def rst_role(text: str, role: str, escape: bool = True) -> str:
        # lobster-trace: SwRequirements.sw_req_rst_role
        """
        Create role text in reStructuredText.
        The text will be automatically escaped for reStructuredText if necessary.
        There will be no newline appended at the end.

        Args:
            text (str): Text
            color (str): Role
            escape (bool): Escapes text (default: True).

        Returns:
            str: Text with role
        """
        text_raw = text

        if escape is True:
            text_raw = RstConverter.rst_escape(text)

        return f":{role}:`{text_raw}`"

# Functions ********************************************************************

# Main *************************************************************************
