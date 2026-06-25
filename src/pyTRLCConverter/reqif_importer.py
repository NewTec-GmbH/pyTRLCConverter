"""Imports a ReqIF file into TRLC.

    The importer supports two modes:

    - Initial import (bootstrap): when no existing TRLC is provided, a brand-new TRLC
      project is generated from the ReqIF file.
    - Merge import (re-import): when existing TRLC is provided, the existing .trlc files
      are updated in place. (Implemented in a later step.)

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
from typing import Any
from pyTRLCConverter.logger import log_error, log_verbose
from pyTRLCConverter.reqif_reader import ReqifReader, sanitize_identifier
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_generator import TrlcGenerator
from pyTRLCConverter.trlc_helper import (
    get_trlc_symbols,
    get_file_dict_from_symbols,
    is_item_record
)

# Variables ********************************************************************

# Classes **********************************************************************


class ReqifImporter:
    """Imports a ReqIF file into TRLC (initial generation or in-place merge)."""

    SUBCOMMAND = "reqif-import"

    def __init__(self, args: Any) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Initializes the importer.

        Args:
            args (Any): The parsed program arguments.
        """
        self._args = args

    @classmethod
    def register(cls, args_sub_parser: Any) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        """Register the importer specific argument parser.

        Args:
            args_sub_parser (Any): Sub parser collection to add the importer command to.
        """
        parser = args_sub_parser.add_parser(
            cls.SUBCOMMAND,
            help="Import a ReqIF file (.reqif/.reqifz) into TRLC."
        )
        parser.set_defaults(operation_class=cls)

        parser.add_argument(
            "input",
            metavar="INPUT",
            type=str,
            help="Path to the .reqif or .reqifz file to import."
        )

        parser.add_argument(
            "--package",
            type=str,
            default=None,
            required=False,
            help="TRLC package name for the initial import. Defaults to the sanitized input basename."
        )

        parser.add_argument(
            "--gfm",
            action="store_true",
            default=False,
            required=False,
            help="Emit GFM render-config entries for plain string attributes on the initial import."
        )

        parser.add_argument(
            "--id-store",
            type=str,
            default=None,
            required=False,
            help="Path to the JSON identifier store. Seeded on the initial import; required to "
                 "match objects on a merge import."
        )

    def run(self) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Run the import.

        Returns:
            Ret: Status.
        """
        result = Ret.OK
        input_path = self._args.input

        if not os.path.isfile(input_path):
            log_error(f"ReqIF input file not found: {input_path}")
            result = Ret.ERROR
        else:
            reader = ReqifReader()

            if reader.load(input_path) is False:
                result = Ret.ERROR
            elif self._has_existing_trlc() is True:
                result = self._run_merge(reader)
            else:
                result = self._run_initial(reader)

        return result

    def _has_existing_trlc(self) -> bool:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Check whether existing TRLC record objects are provided via --source.

        Returns:
            bool: True if at least one TRLC record object is found, otherwise False.
        """
        has_records = False
        sources = self._args.source

        if sources:
            symbols = get_trlc_symbols(sources, self._args.include)
            if symbols is not None:
                file_dict = get_file_dict_from_symbols(symbols)
                for items in file_dict.values():
                    for item in items:
                        if is_item_record(item):
                            has_records = True
                            break
                    if has_records is True:
                        break

        return has_records

    def _run_initial(self, reader: ReqifReader) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_import_initial
        """Run the initial import (bootstrap a new TRLC project from the ReqIF file).

        Args:
            reader (ReqifReader): The loaded ReqIF reader.

        Returns:
            Ret: Status.
        """
        input_path = self._args.input
        basename = os.path.splitext(os.path.basename(input_path))[0]
        package_name = self._args.package or sanitize_identifier(basename)

        if self._args.out:
            output_dir = self._args.out
        else:
            output_dir = os.path.join(os.path.dirname(input_path), f"{basename}_trlc")

        log_verbose(f"Initial ReqIF import into package '{package_name}' at '{output_dir}'.")

        generator = TrlcGenerator(reader, package_name)

        return generator.generate(output_dir, gfm_format=self._args.gfm)

    def _run_merge(self, reader: ReqifReader) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_import
        """Run the merge import (update existing TRLC files in place).

        Args:
            reader (ReqifReader): The loaded ReqIF reader.

        Returns:
            Ret: Status.
        """
        # The merge import is implemented in a later step.
        del reader
        log_error("Merge import into existing TRLC files is not yet available.")

        return Ret.ERROR


# Functions ********************************************************************

# Main *************************************************************************
