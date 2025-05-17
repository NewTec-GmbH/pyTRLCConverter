"""The main module with the program entry point.
    The main task is to convert requirements, diagrams and etc. which are defined
    by TRLC into markdown format.

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
import importlib
import inspect
import os
import sys
import argparse
from typing import Optional
from pyTRLCConverter.abstract_converter import AbstractConverter
from pyTRLCConverter.dump_converter import DumpConverter
from pyTRLCConverter.item_walker import ItemWalker
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.version import __license__, __repository__, __version__
from pyTRLCConverter.trlc_helper import get_trlc_symbols
from pyTRLCConverter.markdown_converter import MarkdownConverter
from pyTRLCConverter.docx_converter import DocxConverter
from pyTRLCConverter.logger import enable_verbose, log_verbose, is_verbose_enabled, log_error
from pyTRLCConverter.rst_converter import RstConverter

# Variables ********************************************************************

PROG_NAME = "pyTRLCConverter"
PROG_DESC = "A CLI tool to convert TRLC into different formats."
PROG_COPYRIGHT = "Copyright (c) 2024 - 2025 NewTec GmbH - " + __license__
PROG_GITHUB = "Find the project on GitHub: " + __repository__
PROG_EPILOG = PROG_COPYRIGHT + " - " + PROG_GITHUB

# List of built-in converters to use or subclass by a project converter.
BUILD_IN_CONVERTER_LIST = [
    MarkdownConverter,
    DocxConverter,
    DumpConverter,
    RstConverter
]

# Classes **********************************************************************

# Functions ********************************************************************

def _create_args_parser() -> argparse.ArgumentParser:
    # lobster-trace: SwRequirements.sw_req_cli_help
    """ Creater parser for command line arguments.

    Returns:
        argparse.ArgumentParser:  The parser object for command line arguments.
    """
    parser = argparse.ArgumentParser(prog=PROG_NAME,
                                     description=PROG_DESC,
                                     epilog=PROG_EPILOG)

    # lobster-trace: SwRequirements.sw_req_cli_version
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print full command details before executing the command." \
                "Enables logs of type INFO and WARNING."
    )

    # lobster-trace: SwRequirements.sw_req_cli_include
    parser.add_argument(
        "-i",
        "--include",
        type=str,
        default=None,
        required=False,
        action="append",
        help="Add additional directory which to include on demand. Can be specified several times."
    )

    # lobster-trace: SwRequirements.sw_req_cli_source
    parser.add_argument(
        "-s",
        "--source",
        type=str,
        required=True,
        action="append",
        help="The path to the TRLC files folder or a single TRLC file."
    )

    # lobster-trace: SwRequirements.sw_req_cli_exclude
    parser.add_argument(
        "-ex",
        "--exclude",
        type=str,
        default=None,
        required=False,
        action="append",
        help="Add source directory which shall not be considered for conversion. Can be specified several times."
    )

    # lobster-trace: SwRequirements.sw_req_cli_out
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        default="",
        required=False,
        help="Output path, e.g. /out/markdown."
    )

    # lobster-trace: SwRequirements.sw_req_prj_spec_file
    parser.add_argument(
        "-p",
        "--project",
        type=str,
        default=None,
        required=False,
        help="Python module with project specific conversion functions."
    )

    # lobster-trace: SwRequirements.sw_req_cli_translation
    parser.add_argument(
        "-tr",
        "--translation",
        type=str,
        default=None,
        required=False,
        help="Requirement attribute translation JSON file."
    )

    return parser

def main() -> int:
    # lobster-trace: SwRequirements.sw_req_cli
    # lobster-trace: SwRequirements.sw_req_destination_format
    """Main program entry point.

    Returns:
        int: Program status
    """
    ret_status = Ret.OK

    # Create program arguments parser.
    args_parser = _create_args_parser()
    args_sub_parser = args_parser.add_subparsers(required='True')

    # Check if a project specific converter is given and load it.
    project_converter = None

    try:
        project_converter = _get_project_converter()
    except ValueError as exc:
        log_error(exc)
        ret_status = Ret.ERROR

    if ret_status == Ret.OK:

        project_converter_cmd = None

        if project_converter is not None:
            project_converter.register(args_sub_parser)
            project_converter_cmd = project_converter.get_subcommand()

        # Load the built-in converters unless a project converter is replacing built-in.
        # lobster-trace: SwRequirements.sw_req_no_prj_spec
        for converter in BUILD_IN_CONVERTER_LIST:
            if converter.get_subcommand() != project_converter_cmd:
                converter.register(args_sub_parser)

        args = args_parser.parse_args()

        if args is None:
            ret_status = Ret.ERROR

        else:
            enable_verbose(args.verbose)

            # In verbose mode print all program arguments.
            if is_verbose_enabled() is True:
                log_verbose("Program arguments: ")

                for arg in vars(args):
                    log_verbose(f"* {arg} = {vars(args)[arg]}")
                log_verbose("\n")

            # lobster-trace: SwRequirements.sw_req_process_trlc_symbols
            symbols = get_trlc_symbols(args.source, args.include)

            if symbols is None:
                log_error(f"No items found at {args.source}.")
                ret_status = Ret.ERROR
            else:
                try:
                    _create_out_folder(args.out)

                    # Feed the items into the given converter.
                    log_verbose(
                        f"Using converter {args.converter_class.__name__}: {args.converter_class.get_description()}")
                    converter = args.converter_class(args)

                    walker = ItemWalker(args, converter)
                    ret_status = walker.walk_symbols(symbols)

                except (FileNotFoundError, OSError) as exc:
                    log_error(exc)
                    ret_status = Ret.ERROR

    return ret_status

def _get_project_converter() -> Optional[AbstractConverter]:
    # lobster-trace: SwRequirements.sw_req_prj_spec
    # lobster-trace: SwRequirements.sw_req_prj_spec_file
    """Get the project specific converter class from a --project or -p argument.

    Returns:
        AbstractConverter: The project specific converter or None if not found.
    """
    project_module_name = None

    # Check for project option (-p or --project).
    arglist = sys.argv[1:]
    for index, argval in enumerate(arglist):
        if argval.startswith("-p="):
            project_module_name = argval[3:]
        elif argval.startswith("--project="):
            project_module_name = argval[10:]
        elif argval in ('-p', '--project') and (index + 1) < len(arglist):
            project_module_name = arglist[index + 1]

        if project_module_name is not None:
            break

    if project_module_name is not None:
        # Dynamically load the module and search for an AbstractConverter class definition
        sys.path.append(os.path.dirname(project_module_name))
        project_module_name_basename = os.path.basename(project_module_name).replace('.py', '')

        try:
            module = importlib.import_module(project_module_name_basename)
        except ImportError as exc:
            raise ValueError(f"Failed to import module {project_module_name}: {exc}") from exc

        #Filter classes that are defined in the module directly.
        classes = inspect.getmembers(module, inspect.isclass)
        classes = {name: cls for name, cls in classes if cls.__module__ == project_module_name_basename}

        # lobster-trace: SwRequirements.sw_req_prj_spec_interface
        for class_name, class_def in classes.items():
            if issubclass(class_def, AbstractConverter):
                log_verbose(f"Found project specific converter type: {class_name}")
                return class_def

        raise ValueError(f"No AbstractConverter derived class found in {project_module_name_basename}")

    return None

def _create_out_folder(path: str) -> None:
    # lobster-trace: SwRequirements.sw_req_markdown_out_folder
    """Create output folder if it doesn't exist.

    Args:
        path (str): The output folder path which to create.
    """
    if 0 < len(path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                log_error(f"Failed to create folder {path}: {e}")
                raise

# Main *************************************************************************

if __name__ == "__main__":
    sys.exit(main())
