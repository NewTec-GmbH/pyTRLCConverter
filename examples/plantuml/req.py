"""Project specific Markdown converter functions.

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
import shutil
from pyTRLCConverter.base_converter import RecordsPolicy
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.plantuml import PlantUML

from pyTRLCConverter.markdown_converter import MarkdownConverter
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************


class ExamplePlantumlMarkDownConverter(MarkdownConverter):
    """Custom Project specific Markdown Converter.
    """

    def __init__(self, args: any) -> None:
        """
        Initialize the custom markdown converter.
        """
        super().__init__(args)

        # Set project specific record handlers for the converter.
        self._set_project_record_handlers(
           [
                ("PlantUML", self._print_diagram),
           ]
        )
        self._record_policy = RecordsPolicy.RECORD_CONVERT_ALL

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert into project extended markdown format."

    def _print_table_head(self) -> None:
        """Prints the table head for software requirements and constraints.
        """
        column_titles = ["Attribute", "Value"]
        markdown_table_head = self.markdown_create_table_head(column_titles)

        self._fd.write(markdown_table_head)

    # pylint: disable=unused-argument
    def _print_diagram(self, diagram: Record_Object, level: int) -> Ret:
        """Prints the diagram.

        Args:
            diagram (Record_Object): Diagram to print
            level (int): Current level of the record object
        """
        plantuml_generator = PlantUML()
        image_format = "png"
        diagram_dict = diagram.to_python_dict()
        file_path = diagram_dict["file_path"]
        caption = diagram_dict["caption"]
        full_file_path = file_path
        file_dst_path = None

        # Is the path to the diagram invalid?
        if os.path.isfile(full_file_path) is False:

            full_file_path = self._locate_file(full_file_path)
            # Diagram not found?
            if full_file_path is None:
                raise FileNotFoundError(f"{file_path} not found.")

        if plantuml_generator.is_plantuml_file(file_path):

            plantuml_generator.generate(
                image_format, full_file_path, self._args.out)

            file_dst_path = os.path.basename(full_file_path)
            file_dst_path = os.path.splitext(file_dst_path)[0]
            file_dst_path += "." + image_format

            # PlantUML uses as output filename the diagram name if available.
            # The diagram name may differ from the filename.
            # To aovid that a invalid reference will be in the Markdown document,
            # ensure that the generated filename is as expected.
            expected_dst_path = os.path.join(self._args.out, file_dst_path)
            if os.path.isfile(expected_dst_path) is False:
                raise FileNotFoundError(
                    f"{file_path} diagram name ('@startuml <name>') may differ from file name,"
                    f" expected {expected_dst_path}."
                )

        else:
            # Copy diagram image file to output folder.
            shutil.copy(full_file_path, self._args.out)
            file_dst_path = os.path.basename(full_file_path)

        markdown_image = self.markdown_create_diagram_link(
            file_dst_path, caption)
        self._fd.write(markdown_image)

        return Ret.OK

    def _print_req(self, req: Record_Object, level: int) -> None:
        """Prints the requirement.

        Args:
            req (Record_Object): Requirement to print
            level (int): Current level of the record object
        """
        description = self._get_attribute(req, "description")

        markdown_text = self.markdown_create_heading(req.name, level + 1)
        self._fd.write(markdown_text)

        self._print_table_head()

        table = [
            ["Description", self.markdown_escape(description)]
        ]

        for row in table:
            markdown_table_row = self.markdown_append_table_row(row, False)
            self._fd.write(markdown_table_row)

        self._fd.write("\n")

# Functions ********************************************************************

# Main *************************************************************************
