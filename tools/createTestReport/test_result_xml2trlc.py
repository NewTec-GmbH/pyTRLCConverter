"""Converts pytest results to corresponding TRLC output format.

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
import sys
import xml.etree.ElementTree as ET
from typing import IO, Optional

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

def _test_report_write_header(fd: IO) -> None:
    """Write test report header.

    Args:
        fd (IO): File descriptor
    """
    fd.write('package SwTests\n\n')
    fd.write('section "SW Test Results" {\n\n')

def _test_report_write_footer(fd: IO) -> None:
    """Write test report footer.

    Args:
        fd (IO): File descriptor
    """
    fd.write('}\n')

# pylint: disable=line-too-long
def _test_report_write_test_case_result(fd: IO, test_case_name: str, test_case_result: str, lobster_trace: Optional[str]) -> None:
    """Write test case result to test report.

    Args:
        fd (IO): File descriptor
        test_case_name (str): Name of the test case.
        test_case_result (str): Result of the test case (passed/failed).
        lobster_trace (Optional[str]): Test case id which is relates to the result.
    """
    test_case_id = test_case_name + "_result"
    fd.write(f'    SwTestCaseResult {test_case_id} {{\n')
    fd.write(f'        name = "{test_case_name}"\n')
    fd.write(f'        result = {test_case_result}\n')

    if lobster_trace is not None:
        fd.write(f'        relates = {lobster_trace}\n')

    fd.write('    }\n\n')

def convert_test_report(xml_file: str, output_file: str) -> bool:
    """Convert test report from XML format to corresponding TRLC format
        by considering the project specific defined TRLC model.

    Args:
        xml_file (str): The test report in XML format.
        output_file (str): The test report in TRLC format.

    Returns:
        bool: True if conversion was successful otherwise False.
    """
    result = True

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        with open(output_file, 'w', encoding='utf-8') as fd:
            _test_report_write_header(fd)

            for testcase in root.iter('testcase'):
                test_case_name = testcase.get('name')
                test_case_result = 'SwTestResult.PASSED'

                if testcase.find('failure') is not None:
                    test_case_result = 'SwTestResult.FAILED'

                lobster_trace = None
                properties = testcase.find('properties')
                if properties is not None:
                    for prop in properties.findall('property'):
                        if prop.get('name') == 'lobster-trace':
                            lobster_trace = prop.get('value')

                _test_report_write_test_case_result(fd, test_case_name, test_case_result, lobster_trace)

            _test_report_write_footer(fd)

    except FileNotFoundError:
        print(f"Error: File '{xml_file}' not found.")
        result = False

    return result

# Main *************************************************************************

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parse_report.py <input_xml_file> <output_trlc_file>")
        sys.exit(1)

    test_report_xml_file = sys.argv[1]
    test_report_trlc_file = sys.argv[2]

    if convert_test_report(test_report_xml_file, test_report_trlc_file) is False:
        sys.exit(1)

    sys.exit(0)
