"""
Project specific ReqIF converter for Generic.rsl types.

This module provides a project specific ReqIF converter subclass with
support for the TRLC record types defined in Generic.rsl.

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
import os
import shutil
from typing import Optional

# pylint: disable=import-error
from reqif.models.reqif_types import SpecObjectAttributeType
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.reqif_converter import ReqifConverter
from pyTRLCConverter.trlc_helper import Record_Object

# pylint: disable=wrong-import-order
from image_processing import convert_plantuml_to_image, locate_file

# Variables ********************************************************************

# Classes **********************************************************************


class GenericRslReqifConverter(ReqifConverter):
    """Project specific ReqIF converter subclass for generic.rsl types."""

    # pylint: disable-next=unused-argument
    def _print_info(self, info: Record_Object, level: int, translation: Optional[dict]) -> Ret:
        """Prints the information as a ReqIF spec-object.

        Args:
            info (Record_Object): Information to print.
            level (int): Current level of the record object.
            translation (Optional[dict]): Translation dictionary for the record object.
                                          If None, no translation is applied.

        Returns:
            Ret: Status
        """
        description = self._get_attribute(info, "description")
        rendered = self._render(
            info.n_package.name,
            info.n_typ.name,
            "description",
            description
        )

        spec_object = self._create_spec_object(
            item_name=info.name,
            type_key=self._get_record_type_key(info),
            type_long_name=info.n_typ.name,
            attribute_value_map={
                ReqifConverter.ATTRIBUTE_KEY_RECORD_FOREIGN_ID: {
                    "long_name": "ID",
                    "value": info.name,
                    "attribute_type": SpecObjectAttributeType.STRING
                },
                "field_description": {
                    "long_name": "Description",
                    "value": rendered
                }
            }
        )

        self._append_hierarchy(spec_object.identifier, level + 1, info.name, is_container=False)

        return Ret.OK

    # pylint: disable-next=unused-argument
    def _print_plantuml(self, diagram: Record_Object, level: int, translation: Optional[dict]) -> Ret:
        """Converts a PlantUML diagram to SVG and embeds an external file link as ReqIF XHTML.

        The generated SVG file is written to the output directory and referenced
        via an XHTML <img> element inside the spec-object attribute value.

        Args:
            diagram (Record_Object): Diagram record to process.
            level (int): Current level of the record object.
            translation (Optional[dict]): Translation dictionary for the record object.
                                          If None, no translation is applied.

        Returns:
            Ret: Status
        """
        image_file = convert_plantuml_to_image(
            self._get_attribute(diagram, "file_path"),
            self._args.out,
            self._args.source
        )

        caption = self._get_attribute(diagram, "caption")

        if image_file is not None:
            # Reference the generated SVG as an external file link in XHTML.
            img_xhtml = self._wrap_xhtml(
                f'<img src="{os.path.basename(image_file)}" alt="{caption}"/>'
            )
        else:
            img_xhtml = self._plain_text_to_xhtml(caption)

        spec_object = self._create_spec_object(
            item_name=diagram.name,
            type_key=self._get_record_type_key(diagram),
            type_long_name=diagram.n_typ.name,
            attribute_value_map={
                ReqifConverter.ATTRIBUTE_KEY_RECORD_FOREIGN_ID: {
                    "long_name": "ID",
                    "value": diagram.name,
                    "attribute_type": SpecObjectAttributeType.STRING
                },
                "field_image": {
                    "long_name": "Image",
                    "value": img_xhtml
                },
                "field_caption": {
                    "long_name": "Caption",
                    "value": self._plain_text_to_xhtml(caption)
                }
            }
        )

        self._append_hierarchy(spec_object.identifier, level + 1, diagram.name, is_container=False)

        return Ret.OK

    # pylint: disable-next=unused-argument
    def _print_image(self, image: Record_Object, level: int, translation: Optional[dict]) -> Ret:
        """Copies an image file to the output directory and embeds an external file link as ReqIF XHTML.

        The image file is copied to the output folder and referenced via an
        XHTML <img> element inside the spec-object attribute value.

        Args:
            image (Record_Object): Image record to process.
            level (int): Current level of the record object.
            translation (Optional[dict]): Translation dictionary for the record object.
                                          If None, no translation is applied.

        Returns:
            Ret: Status
        """
        image_file = locate_file(self._get_attribute(image, "file_path"), self._args.source)
        caption = self._get_attribute(image, "caption")

        if image_file is not None:
            # Copy image file to the output folder so it is co-located with the .reqif file.
            shutil.copy(image_file, self._args.out)

            # Reference the copied image as an external file link in XHTML.
            img_xhtml = self._wrap_xhtml(
                f'<img src="{os.path.basename(image_file)}" alt="{caption}"/>'
            )
        else:
            img_xhtml = self._plain_text_to_xhtml(caption)

        spec_object = self._create_spec_object(
            item_name=image.name,
            type_key=self._get_record_type_key(image),
            type_long_name=image.n_typ.name,
            attribute_value_map={
                ReqifConverter.ATTRIBUTE_KEY_RECORD_FOREIGN_ID: {
                    "long_name": "ID",
                    "value": image.name,
                    "attribute_type": SpecObjectAttributeType.STRING
                },
                "field_image": {
                    "long_name": "Image",
                    "value": img_xhtml
                },
                "field_caption": {
                    "long_name": "Caption",
                    "value": self._plain_text_to_xhtml(caption)
                }
            }
        )

        self._append_hierarchy(spec_object.identifier, level + 1, image.name, is_container=False)

        return Ret.OK

# Functions ********************************************************************

# Main *************************************************************************
