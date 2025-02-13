"""Converter to Word docx format.

    Author: Norbert Schulz (norbert.schulz@newtec.de)
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
import docx
from pyTRLCConverter.base_converter import BaseConverter
from pyTRLCConverter.log_verbose import log_verbose
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************
class DocxConverter(BaseConverter):
    # lobster-trace: SwRequirements.sw_req_docx
    """
    Converter to docx format.
    """
    def __init__(self, args: any) -> None:
        # lobster-trace: SwRequirements.sw_req_docx
        """
        Initialize the docx converter.
        """
        super().__init__(args)

        if args.template is not None:
            log_verbose(f"Loading template file {args.template}.")

        # lobster-trace: SwRequirements.sw_req_docx_template
        self._docx = docx.Document(docx=args.template)

    @staticmethod
    def get_subcommand() -> str:
        """ Return subcommand token for this converter.

        Returns:
            Ret: Status
        """
        return "docx"

    @staticmethod
    def get_description() -> str:
        """ Return converter description.
        
        Returns:
            Ret: Status
        """
        return "Convert into docx format."

    @staticmethod
    def register(args_parser, cls : type) -> None:
        """Register converter specific argument parser.

        Args:
            args_parser (object): Argument parser
            cls (type): The class type to register
        """
        BaseConverter.register(args_parser, cls)
        BaseConverter._parser.add_argument(
            "-t",
            "--template",
            type=str,
            default=None,
            required=False,
            help="Load the given docx file as a template to append to."
        )
        BaseConverter._parser.add_argument(
            "-n",
            "--name",
            type=str,
            default="output.docx",
            required=False,
            help="Name of the generated output file inside the output folder (default = output.docx)."
        )

    def enter_file(self, file_name: str) -> Ret:
        """Enter a file.

        Args:
            file_name (str): File name
        
        Returns:
            Ret: Status
        """
        return Ret.OK

    def leave_file(self, file_name: str) -> Ret:
        """Leave a file.

        Args:
            file_name (str): File name

        Returns:
            Ret: Status
        """
        return Ret.OK

    def convert_section(self, section: str, level: int) -> Ret:
        # lobster-trace: SwRequirements.sw_req_docx_section
        """Process the given section item.

        Args:
            section (str): The section name
            level (int): The section indentation level
        
        Returns:
            Ret: Status
        """
        self._docx.add_heading(section, level)
        return Ret.OK

    def convert_record_object(self, record: Record_Object, level: int) -> Ret:
        # lobster-trace: SwRequirements.sw_req_docx_record
        """Process the given record object.

        Args:
            record (Record_Object): The record object
            level (int): The record level
        
        Returns:
            Ret: Status
        """
        self._docx.add_heading(f"{record.name} ({record.n_typ.name})", level + 1)
        attributes = record.to_python_dict()

        table = self._docx.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        table.autofit = True

        # Set table headers
        header_cells = table.rows[0].cells
        header_cells[0].text = "Element"
        header_cells[1].text = "Value"

        # Populate table with attribute key-value pairs
        for key, value in attributes.items():
            if value is None:
                value = "N/A"

            cells = table.add_row().cells
            cells[0].text = key
            cells[1].text = value

        # Add a paragraph with the record object location
        p = self._docx.add_paragraph()
        p.add_run(f"from {record.location.file_name}:{record.location.line_no}").italic = True
        return Ret.OK

    def finish(self) -> Ret:
        # lobster-trace: SwRequirements.sw_req_docx_file
        """Finish the conversion.

        Returns:
            Ret: Status
        """
        result = Ret.OK

        if self._docx is not None:
            output_file_name = self._args.name
            if 0 < len(self._args.out):
                output_file_name = os.path.join(self._args.out, self._args.name)

            log_verbose(f"Writing docx {output_file_name}.")
            self._docx.save(output_file_name)
            self._docx = None

        return result

# Functions ********************************************************************


# Main *************************************************************************
