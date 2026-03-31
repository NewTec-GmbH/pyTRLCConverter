"""Project specific ReqIF converter functions.

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
import mimetypes
import os
import shutil
from typing import Optional, Any

from trlc.ast import String_Literal

from pyTRLCConverter.base_converter import RecordsPolicy
from pyTRLCConverter.logger import log_error
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.reqif_converter import ReqifConverter
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************


class CustomReqIFConverter(ReqifConverter):
    """Custom Project specific ReqIF Converter.
        Its main task is to handle image references by copying
        them to the output folder. This is required to bundle
        it to a .reqifz file.
    """

    def __init__(self, args: Any) -> None:
        """
        Initialize the custom converter.

        Args:
            args (Any): The parsed program arguments.
        """
        super().__init__(args)
        self._current_doc_name: str = ""
        self._file_path_value_ref: Optional[String_Literal] = None

        # Set project specific record handlers for the converter.
        self._set_project_record_handlers(
           {
               "Image": self._handle_reference
           }
        )
        self._record_policy = RecordsPolicy.RECORD_CONVERT_ALL

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Handles image references."

    def enter_file(self, file_name: str) -> Ret:
        """Store the current document name and delegate to the base class.

        Args:
            file_name (str): Path of the TRLC file being entered.

        Returns:
            Ret: Status
        """
        self._current_doc_name = os.path.splitext(os.path.basename(file_name))[0]
        return super().enter_file(file_name)

    def _handle_reference(self, record: Record_Object, level: int, translation: Optional[dict]) -> Ret:
        """Handle the referenced file by copying it to the output folder.

        If the record contains a 'file_path' field, the referenced file is
        copied to the current output directory (or the document subfolder when
        --reqifz is active).  The field value passed to the generic converter
        is stripped to the bare filename so the generated ReqIF assumes the
        file is co-located with the output.

        Args:
            record (Record_Object): TRLC record with reference attribute.
            level (int): Current level of the record object.
            translation (Optional[dict]): Translation dictionary for the record object.
                                            If None, no translation is applied.

        Returns:
            Ret: Status
        """
        self._file_path_value_ref = None

        for name, value in record.field.items():
            if name == "file_path" and isinstance(value, String_Literal):
                src_path = value.to_string()

                if 0 < len(self._out_path) and self._args.reqifz:
                    out_dir = os.path.join(self._out_path, self._current_doc_name)
                elif 0 < len(self._out_path):
                    out_dir = self._out_path
                elif self._args.reqifz:
                    out_dir = self._current_doc_name
                else:
                    out_dir = "."

                os.makedirs(out_dir, exist_ok=True)

                if os.path.isfile(src_path):
                    shutil.copy2(src_path, os.path.join(out_dir, os.path.basename(src_path)))
                else:
                    log_error(f"Referenced file not found: {src_path}")

                self._file_path_value_ref = value
                break

        result = self.convert_record_object_generic(record, level, translation)
        self._file_path_value_ref = None
        return result

    def _on_string_literal(self, string_literal: String_Literal) -> str:
        """Return the string value, stripping the directory component for the file_path field.

        Args:
            string_literal (String_Literal): The string literal expression.

        Returns:
            str: String value with path stripped if this is the active file_path reference.
        """
        raw = string_literal.to_string()
        if self._file_path_value_ref is not None and string_literal is self._file_path_value_ref:
            raw = os.path.basename(raw)
        return raw

    def _render(self, package_name: str, type_name: str, attribute_name: str,
                attribute_value: str) -> str:
        """Render the attribute value as XHTML.

        For Image records the file_path field is rendered as an XHTML <object>
        element so that ReqIF viewers can display the referenced file inline.
        The MIME type is derived from the file extension.
        All other attributes are handled by the base class.

        Args:
            package_name (str): TRLC package name of the record.
            type_name (str): TRLC type name of the record.
            attribute_name (str): Attribute field name.
            attribute_value (str): Raw attribute value string (filename only).

        Returns:
            str: XHTML-wrapped content string.
        """
        if type_name == "Image" and attribute_name == "file_path":
            mime_type, _ = mimetypes.guess_type(attribute_value)
            if mime_type is None:
                mime_type = "application/octet-stream"
            xhtml = f'<object type="{mime_type}" data="{attribute_value}"></object>'
            return self._wrap_xhtml(xhtml)
        return super()._render(package_name, type_name, attribute_name, attribute_value)

# Functions ********************************************************************

# Main *************************************************************************
