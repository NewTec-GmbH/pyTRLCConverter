"""PlantUML to image file converter.

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
import subprocess
import sys
import zlib
import base64
import urllib
import urllib.parse
import requests

from pyTRLCConverter.logger import log_verbose, log_error

# Variables ********************************************************************

# URL encoding char sets.
# See https://plantuml.com/de/text-encoding for differences to base64 in URL encode.
BASE64_ENCODE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
PLANTUML_ENCODE_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"

# Classes **********************************************************************


class PlantUML():
    # lobster-trace: SwRequirements.sw_req_plantuml
    """PlantUML image generator.
    """
    def __init__(self) -> None:
        self._server_url = None
        self._plantuml_jar = None
        self._working_directory = os.path.abspath(os.getcwd())

        if "PLANTUML" in os.environ:
            plantuml_access = os.environ["PLANTUML"]
            try:
                # Use server method if PLANTUML is a URL.
                if urllib.parse.urlparse(plantuml_access).scheme in ['http', 'https']:
                    self._server_url = plantuml_access
                else:
                    self._plantuml_jar = os.environ["PLANTUML"]
            except ValueError:
                self._plantuml_jar = os.environ["PLANTUML"]

    def _get_absolute_path(self, path):
        """Get absolute path to the diagram.
            This is required by PlantUML java program for the output path.

        Args:
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        absolute_path = path

        if os.path.isabs(path) is False:
            absolute_path = os.path.join(self._working_directory, path)

        return absolute_path

    def is_plantuml_file(self, diagram_path):
        """Is the diagram a PlantUML file?
            Only the file extension will be checked.

        Args:
            diagram_path (str): Diagram path.

        Returns:
            bool: If file is a PlantUML file, it will return True otherwise False.
        """
        is_valid = False

        if diagram_path.endswith(".plantuml") or \
            diagram_path.endswith(".puml") or \
            diagram_path.endswith(".wsd"):
            is_valid = True

        return is_valid

    def _make_server_url(self, diagram_type: str, diagram_path: str) -> str:
        """Generate a plantuml server GET URL from a diagram data file.

        Args:
            diagram_type (str): Diagram type, e.g. svg. See PlantUML -t options.
            diagram_path (str): Path to the PlantUML diagram.

        Raises:
            FileNotFoundError: PlantUML diagram file not found.
        """
        # Read PlantUML diagram data from given file.
        with open(diagram_path, 'r', encoding='utf-8') as input_file:
            diagram_string = input_file.read().encode('utf-8')

        # Compress the data using deflate.
        # Strib Zlib's 2 byte header and 4 byte checksum for raw deflate data.
        compressed_data = zlib.compress(diagram_string)[2:-4]

        # Encode the compressed data using base64.
        base64_encoded_data = base64.b64encode(compressed_data)

        # Translate from base64 to plantuml char encoding.
        base64_to_puml_trans = bytes.maketrans(
            BASE64_ENCODE_CHARS.encode('utf-8'),
            PLANTUML_ENCODE_CHARS.encode('utf-8')
        )
        puml_encoded_data = base64_encoded_data.translate(base64_to_puml_trans).decode('utf-8')

        # Create the URL for the PlantUML server.
        query_url = (
            f"{self._server_url}/"
            f"{diagram_type}/"
            f"{urllib.parse.quote(puml_encoded_data)}"
        )

        return query_url

    def generate(self, diagram_type: str, diagram_path: str, dst_path: str) -> None:
        """Generate plantuml image.

        Args:
            diagram_type (str): Diagram type, e.g. svg. See PlantUML -t options.
            diagram_path (str): Path to the PlantUML diagram.
            dst_path (str): Path to the destination of the generated image.

        Raises:
            FileNotFoundError: PlantUML java jar file not found in local mode.
            FileNotFoundError: PlantUML diagram file not found.
            requests.exceptions.RequestException: Error during GET request to PlantUML server.
            OSError: Destination path does not exist.
        """
        if self._server_url is not None:
            self._generate_server(diagram_type, diagram_path, dst_path)
        else:
            self._generate_local(diagram_type, diagram_path, dst_path)

    def _generate_server(self, diagram_type: str, diagram_path: str, dst_path: str) -> None:
        """Generate image using a plantuml server.

        This is does not require java installed and is usually a lot faster
        as no java startup time needed when using the plantuml.jar file.

        Args:
            diagram_type (str): Diagram type, e.g. svg. See PlantUML -t options.
            diagram_path (str): Path to the PlantUML diagram.
            dst_path (str): Path to the destination of the generated image.

         Raises:
            FileNotFoundError: PlantUML diagram file not found.
            OSError: Destination path does not exist.
            requests.exceptions.RequestException: Error during GET request to PlantUML server.
        """
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

        # Send GET request to the PlantUML server.
        url = self._make_server_url(diagram_type, diagram_path)
        log_verbose(f"Sending GET request {url}")
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            # Save the response content in image file.
            output_file = os.path.splitext(os.path.basename(diagram_path))[0]
            output_file += "." + diagram_type
            output_file = os.path.join(dst_path, output_file)
            with open(output_file, 'wb') as f:
                f.write(response.content)

            log_verbose(f"Diagram saved as {output_file}.")
        else:
            raise requests.exceptions.RequestException(f"{response.status_code} - {response.text}")

    def _generate_local(self, diagram_type, diagram_path, dst_path):
        """Generate image local call to plantuml.jar.

        Args:
            diagram_type (str): Diagram type, e.g. svg. See PlantUML -t options.
            diagram_path (str): Path to the PlantUML diagram.
            dst_path (str): Path to the destination of the generated image.

        Raises:
            FileNotFoundError: PlantUML java jar file not found.
            OSError: Destination path does not exist.
        """
        if self._plantuml_jar is not None:

            if not os.path.exists(dst_path):
                os.makedirs(dst_path)

            plantuml_cmd = ["java" ]

            if sys.platform.startswith("linux"):
                plantuml_cmd.append("-Djava.awt.headless=true")

            plantuml_cmd.extend(
                [
                    "-jar", f"{self._plantuml_jar}",
                    f"{diagram_path}",
                    f"-t{diagram_type}",
                    "-o", self._get_absolute_path(dst_path)
                ]
            )

            try:
                output = subprocess.run(plantuml_cmd, capture_output=True, text=True, check=False)
                if output.stderr:
                    log_error(output.stderr, True)
                print(output.stdout)
            except FileNotFoundError as exc:
                raise FileNotFoundError(f"{self._plantuml_jar} not found.") from exc
        else:
            raise FileNotFoundError("plantuml.jar not found, set PLANTUML environment variable.")

# Functions ********************************************************************

# Main *************************************************************************
