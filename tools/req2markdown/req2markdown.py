"""Project specific Markdown converter functions.

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
import shutil
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.plantuml import PlantUML

from pyTRLCConverter.markdown_converter import MarkdownConverter
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

class CustomMarkDownConverter(MarkdownConverter):
    """Custom Project specific Markdown Converter.
    """

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert into project extended markdown format."

    def convert_section(self, section: str, level: int) -> Ret:
        """Converts a section to Markdown format.

        Args:
            section (str): Section to convert
            level (int): Current level of the section
        
        Returns:
            Ret: Status
        """
        markdown_text = self.markdown_create_heading(section, level + 1)
        self._fd.write(markdown_text)

        return Ret.OK

    # pylint: disable=unused-argument
    def convert_record_object(self, record: Record_Object, level: int) -> Ret:
        """Converts a record object to Markdown format.

        Args:
            record (Record_Object): Record object to convert
            level (int): Current level of the record object
        
        Returns:
            Ret: Status
        """

        if record.n_typ.name == "SwReqDiagram":
            self._print_diagram(record, level)

        elif record.n_typ.name == "SwReq":
            self._print_sw_req(record, level)

        elif record.n_typ.name == "SwConstraint":
            self. _print_sw_constraint(record, level)

        else:
            # Skipped.
            pass

        return Ret.OK

    def _print_table_head(self) -> None:
        """Prints the table head for software requirements and constraints.
        """
        column_titles = ["Attribute", "Value"]
        markdown_table_head = self.markdown_create_table_head(column_titles)

        self._fd.write(markdown_table_head)

    # pylint: disable=unused-argument
    def _print_diagram(self, diagram: Record_Object, level: int) -> None:
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

            plantuml_generator.generate(image_format, full_file_path, self._args.out)

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
                     " expected {expected_dst_path}."
                )

        else:
            # Copy diagram image file to output folder.
            shutil.copy(full_file_path, self._args.out)
            file_dst_path = os.path.basename(full_file_path)

        markdown_image = self.markdown_create_diagram_link(file_dst_path, caption)
        self._fd.write(markdown_image)

    def _print_sw_req(self, sw_req: Record_Object, level: int) -> None:
        """Prints the software requirement.

        Args:
            sw_req (Record_Object): Software requirement to print
            level (int): Current level of the record object
        """
        sw_req_attributes = sw_req.to_python_dict()

        info = sw_req_attributes["info"]
        if info is None:
            info = "N/A"

        derived = sw_req_attributes["derived"]
        derived_info = "N/A"
        if derived is not None:
            derived_info = ""
            for idx, derived_req in enumerate(derived):
                if 0 < idx:
                    derived_info += ", "

                anchor_tag = "#" + derived_req.replace("SwRequirements.", "").lower()
                anchor_tag = anchor_tag.replace(" ", "-")

                derived_info += self.markdown_create_link(derived_req, anchor_tag)

        markdown_text = self.markdown_create_heading(sw_req.name, level + 1)
        self._fd.write(markdown_text)

        self._print_table_head()

        table = [
            ["Description", self.markdown_escape(sw_req_attributes["description"])],
            ["Verification Proposal", self.markdown_escape(sw_req_attributes["verification_proposal"])],
            ["Info", self.markdown_escape(info)],
            ["Derived", derived_info]
        ]

        for row in table:
            markdown_table_row = self.markdown_append_table_row(row, False)
            self._fd.write(markdown_table_row)

        self._fd.write("\n")

    def _print_sw_constraint(self, sw_req: Record_Object, level: int) -> None:
        """Prints the software constraint.

        Args:
            sw_req (Record_Object): Software constraint to print
            level (int): Current level of the record object
        """
        sw_constraint_id = sw_req.name
        sw_constraint_attributes = sw_req.to_python_dict()
        description = sw_constraint_attributes["description"]
        info = sw_constraint_attributes["info"]

        if info is None:
            info = "N/A"

        markdown_text = self.markdown_create_heading(sw_constraint_id, level + 1)
        self._fd.write(markdown_text)

        self._print_table_head()

        table = [
            ["Description", description],
            ["Info", info]
        ]

        for row in table:
            markdown_table_row = self.markdown_append_table_row(row)
            self._fd.write(markdown_table_row)

        self._fd.write("\n")

# Main *************************************************************************
