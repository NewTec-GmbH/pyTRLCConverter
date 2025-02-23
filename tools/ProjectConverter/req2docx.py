"""Project specific docx converter functions.

    Author: Norbert Schulz (norbert.schulz@newtec.de)
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
import docx
from pyTRLCConverter.base_converter import RecordsPolicy
from pyTRLCConverter.docx_converter import DocxConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import Record_Object

# pylint: disable=wrong-import-order
from image_processing import convert_plantuml_to_image, locate_file

# Variables ********************************************************************

# Classes **********************************************************************

class CustomDocxConverter(DocxConverter):
    """Custom Project specific Docx format converter. 
    """
    def __init__(self, args: any) -> None:
        """
        Initialize the custom docx converter.
        """
        super().__init__(args)

        # set project specific record handlers for the converter.
        self._set_project_record_handlers(
           [
                ("Info", self._convert_record_object_info),
                ("Image", self._convert_record_object_image),
                ("PlantUML", self._convert_record_object_plantuml),
           ]
        )
        self._record_policy = RecordsPolicy.RECORD_CONVERT_ALL
        self._img_counter = 1

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert into project specific docx format."

    # pylint: disable=unused-argument
    def _convert_record_object_info(self, record: Record_Object, level: int) -> Ret:
        """Convert an information record object to the destination format.

        Args:
            record (Record_Object): The record object to convert.
            level (int): Current level of the record object
        
        Returns:
            Ret: Status
        """
        self._docx.add_paragraph(self._get_attribute(record, "description"))
        return Ret.OK

    def _convert_record_object_plantuml(self, record: Record_Object, level: int) -> Ret:
        """Convert a Plantuml diagram record object to the destination format.

        Args:
            record (Record_Object): The record object to convert.
            level (int): Current level of the record object
        
        Returns:
            Ret: Status
        """
        result = Ret.ERROR

        image_file = convert_plantuml_to_image(
            self._get_attribute(record, "file_path"),
            self._args.out,
            self._args.source
        )

        if image_file is not None:
            self._add_image(image_file, self._get_attribute(record, "caption"), level)
            result = Ret.OK

        return result

    def _convert_record_object_image(self, record: Record_Object, level: int) -> Ret:
        """Convert a software diagram record object to the destination format.

        Args:
            record (Record_Object): The record object to convert.
            level (int): Current level of the record object
        
        Returns:
            Ret: Status
        """
        result = Ret.ERROR

        image_file = locate_file(self._get_attribute(record, "file_path"), self._args.source)
        if image_file is not None:
            self._add_image(image_file, self._get_attribute(record, "caption"), level)
            result = Ret.OK

        return result

    def _add_image(self, image_file: str, caption: str, level:int) -> None:
        """Add an image to the docx file.

        Args:
            image_file (str): The image file to add.
            caption (str): The caption of the image.
            level (int): Current level of the record object
        """
        p = self._docx.add_paragraph()
        p.paragraph_format.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(image_file, width=docx.shared.Inches(6))
        run.add_text(f"Figure {self._img_counter} {caption}")

        self._img_counter += 1

# Functions ********************************************************************

# Main *************************************************************************
