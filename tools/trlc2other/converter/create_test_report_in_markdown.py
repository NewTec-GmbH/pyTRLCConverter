"""Project specific Markdown converter functions.

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
from typing import Optional, Any
from pyTRLCConverter.base_converter import RecordsPolicy
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.markdown_converter import MarkdownConverter
from pyTRLCConverter.markdown.element import Heading, Table
from pyTRLCConverter.markdown.text import MarkdownText
from pyTRLCConverter.trlc_helper import Record_Object

# Variables ********************************************************************

# Classes **********************************************************************


class CustomMarkdownConverter(MarkdownConverter):
    """Custom Project specific Markdown converter responsible for converting the
        SW test case results into Markdown format.
    """

    def __init__(self, args: Any) -> None:
        """Initializes the converter.

        Args:
            args (Any): The parsed program arguments.
        """
        super().__init__(args)

        # Set project specific record handlers for the converter.
        self._set_project_record_handlers(
           {
            "SwTestCaseResult": self._print_test_case_result
           }
        )

        self._record_policy = RecordsPolicy.RECORD_SKIP_UNDEFINED

    @staticmethod
    def get_description() -> str:
        """ Return converter description.

         Returns:
            str: Converter description
        """
        return "Convert SW test case results to Markdown format."

    def convert_section(self, section: str, level: int) -> Ret:
        """Converts a section to Markdown format.

        Args:
            section (str): Section to convert
            level (int): Current level of the section

        Returns:
            Ret: Status
        """
        assert len(section) > 0
        assert self._document is not None

        self._document.add(Heading(section, self._get_markdown_heading_level(level)))

        return Ret.OK

    # pylint: disable-next=line-too-long
    def _print_test_case_result(self, test_case_result: Record_Object, _level: int, _translation: Optional[dict]) -> Ret:
        """Prints the software test case result.

        Args:
            test_case_result (Record_Object): Software test case result to print.
            _level (int): Current level of the record object.
            _translation (Optional[dict]): Translation dictionary for the record object.
                                            If None, no translation is applied.

        Returns:
           Ret: Status
        """
        assert self._document is not None

        test_case_result_attributes = test_case_result.to_python_dict()

        test_function_name = self._get_attribute(test_case_result, "name")
        test_result = self._get_attribute(test_case_result, "result")

        test_case = test_case_result_attributes["relates"]
        if test_case is None:
            test_case = MarkdownText.escape("N/A")
        elif isinstance(test_case, list):
            test_case_links = []
            for tc in test_case:
                anchor_tag = "#" + tc.replace("SwTests.", "").lower()
                anchor_tag = anchor_tag.replace(" ", "-")
                test_case_links.append(MarkdownText.link(tc, anchor_tag))

            test_case = ", ".join(test_case_links)
        else:
            anchor_tag = "#" + test_case.replace("SwTests.", "").lower()
            anchor_tag = anchor_tag.replace(" ", "-")

            test_case = MarkdownText.link(test_case, anchor_tag)

        test_function_name = MarkdownText.escape(test_function_name)

        if test_result == "PASSED":
            test_result = MarkdownText.colored_text(test_result, "color:lightgreen")
        elif test_result == "FAILED":
            test_result = MarkdownText.colored_text(test_result, "color:red")

        row = [test_case, test_function_name, test_result]

        self._document.add(Table(["Test Case", "Test Function", "Test Result"], [row]))

        return Ret.OK

# Functions ********************************************************************

# Main *************************************************************************
