"""Test the ReqIF import requirements."""

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
import json
import os
from pathlib import Path
from pyTRLCConverter.__main__ import main
from pyTRLCConverter.reqif_converter import ReqifConverter
from pyTRLCConverter.trlc_helper import get_trlc_symbols
from tests.reqif_test_utils import _parse_reqif, _collect_identifiers

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************


def _export_reqif(monkeypatch, out_dir, sources, render_cfg=None, id_store=None):
    """Export TRLC sources to a single ReqIF document and return the output file path.

    Args:
        monkeypatch (Any): Used to mock program arguments.
        out_dir (Path): Output directory for the ReqIF document.
        sources (list): List of TRLC source paths.
        render_cfg (str): Optional render configuration file path.
        id_store (str): Optional identifier store file path.

    Returns:
        str: Path to the generated ReqIF output file.
    """
    argv = ["pyTRLCConverter"]
    for source in sources:
        argv += ["--source", source]
    if render_cfg is not None:
        argv += ["--renderCfg", render_cfg]
    argv += ["--out", str(out_dir), "reqif", "--single-document"]
    if id_store is not None:
        argv += ["--id-store", id_store]

    monkeypatch.setattr("sys.argv", argv)
    main()

    return os.path.join(out_dir, ReqifConverter.OUTPUT_FILE_NAME_DEFAULT)


def _import_reqif(monkeypatch, out_dir, reqif_file, package="Req"):
    """Import a ReqIF file into a fresh TRLC project and return the output directory.

    Args:
        monkeypatch (Any): Used to mock program arguments.
        out_dir (Path): Output directory for the generated TRLC project.
        reqif_file (str): Path to the ReqIF file to import.
        package (str): TRLC package name for the generated files.

    Returns:
        Path: The output directory.
    """
    monkeypatch.setattr("sys.argv", [
        "pyTRLCConverter",
        "--out", str(out_dir),
        "reqif-import", str(reqif_file),
        "--package", package
    ])
    main()

    return out_dir


def test_tc_reqif_import_initial(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_import_initial
    """Initial import generates a parseable TRLC project and keeps identifiers immutable.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_import_initial")

    reqif_dir = tmp_path / "reqif"
    imported_dir = tmp_path / "imported"
    reqif2_dir = tmp_path / "reqif2"

    # Export a TRLC file to ReqIF.
    reqif_file = _export_reqif(
        monkeypatch, reqif_dir,
        ["./tests/utils/req.rsl", "./tests/utils/multi_req_with_link.trlc"],
        id_store=str(tmp_path / "ids.json")
    )
    assert capsys.readouterr().err == ""
    original_ids = _collect_identifiers(_parse_reqif(reqif_file))["spec_objects"]
    assert len(original_ids) == 2

    # Import the ReqIF into an empty directory.
    _import_reqif(monkeypatch, imported_dir, reqif_file)
    assert capsys.readouterr().err == ""

    # The expected files have been generated.
    for name in ("Req.rsl", "Req.trlc", "renderCfg.json", "translation.json", "id_store.json"):
        assert os.path.exists(os.path.join(imported_dir, name)) is True

    # The generated TRLC parses without errors.
    symbols = get_trlc_symbols(
        [str(imported_dir / "Req.rsl"), str(imported_dir / "Req.trlc")],
        None
    )
    assert symbols is not None
    assert capsys.readouterr().err == ""

    # Re-export the generated TRLC with the seeded identifier store.
    reqif_file2 = _export_reqif(
        monkeypatch, reqif2_dir,
        [str(imported_dir / "Req.rsl"), str(imported_dir / "Req.trlc")],
        render_cfg=str(imported_dir / "renderCfg.json"),
        id_store=str(imported_dir / "id_store.json")
    )
    assert capsys.readouterr().err == ""

    # The spec-object identifiers are reproduced unchanged on the round-trip.
    roundtrip_ids = _collect_identifiers(_parse_reqif(reqif_file2))["spec_objects"]
    assert roundtrip_ids == original_ids


def test_tc_reqif_import_enum(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_import_enum
    """Initial import converts an enumeration datatype into a TRLC enum type.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_import_enum")

    reqif_dir = tmp_path / "reqif"
    imported_dir = tmp_path / "imported"

    reqif_file = _export_reqif(
        monkeypatch, reqif_dir,
        ["./tests/utils/req_enum.rsl", "./tests/utils/single_req_with_enum.trlc"]
    )
    assert capsys.readouterr().err == ""

    _import_reqif(monkeypatch, imported_dir, reqif_file)
    assert capsys.readouterr().err == ""

    with open(os.path.join(imported_dir, "Req.rsl"), "r", encoding="utf-8") as fd:
        rsl_content = fd.read()

    # The enumeration datatype became a TRLC enum type and is referenced by an attribute.
    assert "enum Status" in rsl_content
    assert "Approved" in rsl_content
    assert "optional    Status" in rsl_content


def test_tc_reqif_import_xhtml(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_import_xhtml
    """Initial import marks an XHTML attribute as xhtml in the render configuration.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_import_xhtml")

    reqif_dir = tmp_path / "reqif"
    imported_dir = tmp_path / "imported"

    reqif_file = _export_reqif(
        monkeypatch, reqif_dir,
        ["./tests/utils/req.rsl", "./tests/utils/single_req_description_xhtml.trlc"],
        render_cfg="./tests/utils/renderCfgXhtml.json"
    )
    assert capsys.readouterr().err == ""

    _import_reqif(monkeypatch, imported_dir, reqif_file)
    assert capsys.readouterr().err == ""

    with open(os.path.join(imported_dir, "renderCfg.json"), "r", encoding="utf-8") as fd:
        render_cfg = json.load(fd)

    formats = {entry.get("format") for entry in render_cfg["renderCfg"]}
    assert "xhtml" in formats


def test_tc_reqif_import_path(record_property, capsys, monkeypatch, tmp_path: Path):
    # lobster-trace: SwTests.tc_reqif_import_path
    """Initial import marks an object-with-local-file attribute as path in the render config.

    Args:
        record_property (Any): Used to inject the test case reference into the test results.
        capsys (Any): Used to capture stdout and stderr.
        monkeypatch (Any): Used to mock program arguments.
        tmp_path (Path): Used to create a temporary output directory.
    """
    record_property("lobster-trace", "SwTests.tc_reqif_import_path")

    reqif_dir = tmp_path / "reqif"
    imported_dir = tmp_path / "imported"

    reqif_file = _export_reqif(
        monkeypatch, reqif_dir,
        ["./tests/utils/req_with_path.rsl", "./tests/utils/single_req_with_path.trlc"],
        render_cfg="./tests/utils/renderCfgPath.json"
    )
    assert capsys.readouterr().err == ""

    _import_reqif(monkeypatch, imported_dir, reqif_file)
    assert capsys.readouterr().err == ""

    with open(os.path.join(imported_dir, "renderCfg.json"), "r", encoding="utf-8") as fd:
        render_cfg = json.load(fd)

    formats = {entry.get("format") for entry in render_cfg["renderCfg"]}
    assert "path" in formats

# Main *************************************************************************
