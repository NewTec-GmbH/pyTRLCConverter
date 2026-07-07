# pyTRLCConverter <!-- omit in toc -->

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/NewTec-GmbH/pyTRLCConverter/blob/main/LICENSE) [![Repo Status](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip) [![CI](https://github.com/NewTec-GmbH/pyTRLCConverter/actions/workflows/test.yml/badge.svg)](https://github.com/NewTec-GmbH/pyTRLCConverter/actions/workflows/test.yml)
[![Repo Status](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

pyTRLCConverter is a command-line tool to convert [TRLC (Treat Requirements Like Code)](https://github.com/bmw-software-engineering/trlc) files to different output formats. Since the definition of TRLC types is project-specific, the built-in converters can be extended in an object-oriented manner.

Currently out of the box supported formats:

- Markdown
- docx
- reStructuredText
- ReqIF
- dump

Find the requirements, test cases, coverage and etc. on the [github pages](https://newtec-gmbh.github.io/pyTRLCConverter/).

## Table of Contents <!-- omit in toc -->

- [Overview](#overview)
- [Installation](#installation)
  - [Clone this Project](#clone-this-project)
  - [Setup a virtual Python Environment](#setup-a-virtual-python-environment)
  - [Tool Installation](#tool-installation)
  - [Install from PyPI](#install-from-pypi)
- [Usage](#usage)
  - [Conversion to Markdown format](#conversion-to-markdown-format)
  - [Conversion to docx format](#conversion-to-docx-format)
  - [Conversion to reStructuredText format](#conversion-to-restructuredtext-format)
  - [Conversion to ReqIF format](#conversion-to-reqif-format)
  - [ReqIF import and round-trip](#reqif-import-and-round-trip)
  - [Dump TRLC item list to console](#dump-trlc-item-list-to-console)
  - [Apply attribute name translation](#apply-attribute-name-translation)
  - [Requirement description in Markdown](#requirement-description-in-markdown)
  - [Show tool version](#show-tool-version)
  - [PlantUML](#plantuml)
- [Examples](#examples)
- [Compile into an executable](#compile-into-an-executable)
- [Publish to PyPI](#publish-to-pypi)
- [SW Documentation](#sw-documentation)
- [Tools](#tools)
- [Used Libraries](#used-libraries)
- [Issues, Ideas And Bugs](#issues-ideas-and-bugs)
- [License](#license)
- [Contribution](#contribution)

## Overview

![context](https://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/NewTec-GmbH/pyTRLCConverter/refs/heads/main/doc/architecture/context_diagram.puml)

Find the requirements, test cases, coverage and etc. deployed on [github pages](https://newtec-gmbh.github.io/pyTRLCConverter).

## Installation

Follow these steps to setup an editable pyTRLCConverter workspace using a virtual python environment.

### Clone this Project

```bash
git clone https://github.com/NewTec-GmbH/pyTRLCConverter.git
cd pyTRLCConverter
```

### Setup a virtual Python Environment

```bash
python -m venv .venv
.venv\Scripts\activate.ps1 # <- Windows Power Shell version
```

Note:

- For Windows CMD shell, use `.venv\Scripts\activate.bat` to activate the virtual environment.
- For Linux/Macos, use `source .venv/bin/activate` to activate the virtual environment.

### Tool Installation

The *developers* might like to install it in editable mode together with additional needed
development tools like `pytest`.

```bash
pip install -e .
pip install -r requirements-dev.txt
```

The *users* of the tool install it as usual.

```bash
pip install .
```

### Install from PyPI

End users can install the latest stable release directly from PyPI without cloning the repository:

```bash
pip install pyTRLCConverter
```

## Usage

### Conversion to Markdown format

The tool requires two kinds of TRLC input sources for the conversion. These are the requirements (`*.trlc`) files and the model (`*.tls`) files. These input files are specified using one or more `--source` or `-s` options followed by a file name or directory path. If a path is given, all files with a `.trlc` or `.tls` extension are read by the tool.

```bash
pyTRLCConverter --source trlc/model --source trlc/swe-req markdown
```

It will create a Markdown file with the same name as the requirements file (`*.trlc`) in the current directory, but with the Markdown extension (`.md`).

If the requirements are split into several files, a Markdown file will be created for each. To generate a single Markdown file the argument `--single-document` can be used, which will create an `output.md` file by default.

The converter supports additional arguments that are shown by adding the `--help` option after the markdown subcommand.

```bash
pyTRLCConverter markdown --help

usage: pyTRLCConverter markdown [-h] [-e EMPTY] [-n NAME] [-sd] [-tl TOP_LEVEL] [--render-plantuml]

options:
  -h, --help            show this help message and exit
  -e EMPTY, --empty EMPTY
                        Every attribute value which is empty will output the string (default = N/A).
  -n NAME, --name NAME  Name of the generated output file inside the output folder (default = output.md) in case a single document is generated.
  -sd, --single-document
                        Generate a single document instead of multiple files. The default is to generate multiple files.
  -tl TOP_LEVEL, --top-level TOP_LEVEL
                        Name of the top level heading, required in single document mode (default = Specification).
  --render-plantuml     Render plantuml fenced code blocks as SVG image references. Without this option plantuml blocks are passed through unchanged.
```

More examples are shown in the [examples folder](./examples/).

### Conversion to docx format

Similar to the Markdown conversion, minimal required are the requirements (`*.trlc`) and the model (`*.tls`). Both can be added by file name or just the path where they are located.

```bash
pyTRLCConverter --source trlc/model --source trlc/swe-req docx
```

It will always create a single `output.docx` file in the current directory, regardless of how many TRLC source files are provided.

The converter supports additional arguments that are shown by adding the `--help` option after the docx subcommand.

```bash
pyTRLCConverter docx --help

usage: pyTRLCConverter docx [-h] [-t TEMPLATE] [-n NAME]

options:
  -h, --help            show this help message and exit
  -t TEMPLATE, --template TEMPLATE
                        Load the given docx file as a template to append to.
  -n NAME, --name NAME  Name of the generated output file inside the output folder (default = output.docx).
```

### Conversion to reStructuredText format

The tool requires two kinds of TRLC input sources for the conversion. These are the requirements (`*.trlc`) files and the model (`*.tls`) files. These input files are specified using one or more `--source` or `-s` options followed by a file name or directory path. If a path is given, all files with a `.trlc` or `.tls` extension are read by the tool.

```bash
pyTRLCConverter --source trlc/model --source trlc/swe-req rst
```

If the requirements are split into several files (`*.trlc`), a reStructuredText file will be created for each. To generate a single reStructuredText file the argument `--single-document` can be used, which will create an `output.rst` file by default.

The converter supports additional arguments that are shown by adding the `--help` option after the reStructuredText subcommand.

```bash
pyTRLCConverter rst --help

usage: pyTRLCConverter rst [-h] [-e EMPTY] [-n NAME] [-sd] [-tl TOP_LEVEL]

options:
  -h, --help            show this help message and exit
  -e EMPTY, --empty EMPTY
                        Every attribute value which is empty will output the string (default = N/A).
  -n NAME, --name NAME  Name of the generated output file inside the output folder (default = output.rst) in case a single document is generated.
  -sd, --single-document
                        Generate a single document instead of multiple files. The default is to generate multiple files.
  -tl TOP_LEVEL, --top-level TOP_LEVEL
                        Name of the top level heading, required in single document mode (default = Specification).
```

More examples are shown in the [examples folder](./examples/).

### Conversion to ReqIF format

The tool requires two kinds of TRLC input sources for the conversion. These are the requirements (`*.trlc`) files and the model (`*.tls`) files. These input files are specified using one or more `--source` or `-s` options followed by a file name or directory path. If a path is given, all files with a `.trlc` or `.tls` extension are read by the tool.

```bash
pyTRLCConverter --source trlc/model --source trlc/swe-req reqif
```

If the requirements are split into several files (`*.trlc`), a ReqIF file will be created for each. To generate a single ReqIF file the argument `--single-document` can be used, which will create an `output.reqif` file by default.

The converter supports additional arguments that are shown by adding the `--help` option after the ReqIF subcommand.

```bash
pyTRLCConverter reqif --help

usage: pyTRLCConverter reqif [-h] [-e EMPTY] [-n NAME] [-sd] [-tl TOP_LEVEL] [--reqifz] [--meta-data META_DATA] [--export-map EXPORT_MAP]

options:
  -h, --help            show this help message and exit
  -e EMPTY, --empty EMPTY
                        Every attribute value which is empty will output the string (default = ).
  -n NAME, --name NAME  Name of the generated output file inside the output folder (default = output.reqif) in case a single document is generated.
  -sd, --single-document
                        Generate a single document instead of multiple files. The default is to generate multiple files.
  -tl TOP_LEVEL, --top-level TOP_LEVEL
                        Name of the top level heading, required in single document mode (default = Specification).
  --reqifz              Archive the ReqIF output as a ZIP file with the .reqifz extension. The default is to write plain .reqif files.
  --meta-data META_DATA
                        Path to a JSON ReqIF metadata store used to keep the identifiers of ReqIF Identifiable elements immutable across consecutive exports and to reproduce additional ReqIF metadata. On the initial conversion the file is created; on subsequent conversions the stored identifiers and metadata are reused and new elements are added.
  --export-map EXPORT_MAP
                        Path to a JSON file that lists TRLC attributes which shall be excluded from the export.
```

**ReqIF metadata store (immutable identifiers):**

The ReqIF standard requires the identifier of every `Identifiable` element to stay immutable across consecutive exports and imports. By default each conversion generates fresh (readable) identifiers. To keep them stable, pass `--meta-data <file.json>`:

- On the **initial** conversion the JSON file does not exist yet; the generated identifiers are stored in it, keyed by a stable logical key. This covers the `SPEC-OBJECT`, `SPEC-HIERARCHY`, `SPEC-RELATION`, `SPEC-OBJECT-TYPE`, `ATTRIBUTE-DEFINITION`, `DATATYPE-DEFINITION-ENUMERATION`, `ENUM-VALUE`, `SPECIFICATION` and ReqIF header identifiers. The store also holds additional ReqIF metadata, such as the `SPECIFICATION-TYPE` identity and each attribute's original ReqIF datatype.
- On **subsequent** conversions the file is loaded and the stored identifiers and metadata are reused for already known elements. New elements receive new identifiers which are written back to the file.

When the store was seeded by a `reqif-import` of a foreign ReqIF file (see [ReqIF import](#reqif-import-and-round-trip)), re-exporting reproduces that file's identifiers, long names and datatypes, so the receiving tool (e.g. DOORS Next) does not flag the round-tripped elements as modified.

Markdown-formatted requirement attributes configured via `--renderCfg` are automatically converted to ReqIF-compatible XHTML content.

Conversion rules:

**Types and spec-objects:**

- Each distinct TRLC record type is mapped to one `SPEC-OBJECT-TYPE`. The type's attributes are reflected as `ATTRIBUTE-DEFINITION-*` entries on the type.
- TRLC `section` headings are mapped to a dedicated `SPEC-OBJECT-TYPE` named `Section` and produce a container `SPEC-OBJECT` in the hierarchy.
- Every TRLC record object produces one `SPEC-OBJECT` of the matching `SPEC-OBJECT-TYPE`.

**Attribute mapping by field type:**

| TRLC field type                     | ReqIF datatype                    | ReqIF attribute value              |
| ----------------------------------- | --------------------------------- | ---------------------------------- |
| String (plain, no render config)    | `DATATYPE-DEFINITION-STRING`      | `ATTRIBUTE-VALUE-STRING`           |
| String with Markdown / XHTML config | `DATATYPE-DEFINITION-XHTML`       | `ATTRIBUTE-VALUE-XHTML`            |
| Integer / Decimal / Boolean         | native scalar datatype            | `ATTRIBUTE-VALUE-*` (native value) |
| Enumeration (single or array)       | `DATATYPE-DEFINITION-ENUMERATION` | `ATTRIBUTE-VALUE-ENUMERATION`      |
| Record reference / array            | —                                 | `SPEC-RELATION` (see below)        |
| Optional field with `null` value    | —                                 | omitted from the `SPEC-OBJECT`     |

Notes:

- Enumeration value keys start at 0 and follow the literal declaration order in the RSL model; array (`[0 .. *]`) enum fields are flagged multi-valued and emit all selected values.
- The `SPEC-OBJECT-TYPE`, `DATATYPE-DEFINITION-ENUMERATION` and `ENUM-VALUE` long names use the TRLC quoted long name (the type/enumeration/literal description) when present, so ReqIF long names that are not valid TRLC identifiers (for example `Figure.Image`) are reproduced.
- A plain string attribute becomes `ATTRIBUTE-VALUE-STRING`; only attributes configured as `md`, `gfm`, `xhtml` or `path` in the render configuration become XHTML.
- When a metadata store recorded an attribute's original datatype, that datatype is reproduced instead of the rule above — including `DATATYPE-DEFINITION-DATE`, for which TRLC has no native type.

**Record foreign id:**

- Each `SPEC-OBJECT` carries a `ReqIF.ForeignID` `ATTRIBUTE-VALUE-STRING` holding the exporting system's identifier: the record's `ForeignID` field value when present, otherwise the TRLC record name. The `ForeignID` field itself is not additionally emitted.

**Record references:**

- TRLC record reference fields (single or array) are converted to `SPEC-RELATION-TYPE` and `SPEC-RELATION` entries.
- The relation type name is the TRLC attribute name, for example `derived`.
- The reference field is not emitted as a regular object attribute.
- This preserves traceability links in a form that can be imported by DOORS Next.
- The source and target records must be part of the same generated ReqIF document. Use `--single-document` when references span multiple TRLC files.

### ReqIF import and round-trip

The `reqif-import` subcommand imports a `.reqif` or `.reqifz` file into TRLC, which enables a round-trip exchange with a foreign requirements tool (for example DOORS Next).

```bash
pyTRLCConverter --out ./out reqif-import input.reqif --package Req --meta-data meta_data.json
```

- **Initial import (bootstrap)** — no existing TRLC. A new TRLC project is generated from the ReqIF file: `<package>.rsl`, `<package>.trlc` (following the SPEC-HIERARCHY), and the companion `renderCfg.json`, `translation.json` and `meta_data.json`. The metadata store is seeded with the source identifiers, long names and datatypes.
- **Merge import (re-import)** — existing TRLC provided via `--source`. The existing `.trlc` files are updated in place; objects are matched via the metadata store (`--meta-data`, required) and comments, formatting and non-exchanged attributes are preserved.
- **`--import-filter <file.json>`** restricts which spec-object types and attributes the initial import brings in.

Because the initial import seeds `meta_data.json`, re-exporting the generated TRLC with the same `--meta-data` reproduces the source ReqIF's identifiers, long names and datatypes, so the round-tripped elements are not flagged as modified. See [`examples/reqif`](./examples/reqif/README.md) for a full walkthrough.

### Dump TRLC item list to console

Mainly for development all TRLC items can be dumped to the console.

```bash
pyTRLCConverter --source trlc/model --source trlc/swe-req dump
```

### Apply attribute name translation

The built-in converters display the requirements and their attributes in a table. The first column always contains the attribute name, and the second column contains the attribute value. Since the attribute names must comply with the TRLC standard, they are not always human-readable.

Therefore a translation JSON file can be used to translate the attribute names. Use the `--translation` argument to specify the translation file.

Translation file example:

```json
{
    "SwRequirement": {
        "desc": "Description"
    }
}
```

See the [example](./examples/simple_req_translation/) for more information.

### Requirement description in Markdown

When requirements include lists or need bold/italic emphasis, TRLC currently supports plain text only. pyTRLCConverter lets you write requirement descriptions in Markdown and converts them to the chosen target format (e.g., reStructuredText). To enable this, you must explicitly specify in a JSON configuration which attribute contains Markdown-formatted content.

Two Markdown specifications are supported:

- `"md"`: [CommonMark's spec v0.31.2](https://spec.commonmark.org/0.31.2/)
- `"gfm"`: [GitHub Flavored Markdown spec v0.29-gfm](https://github.github.com/gfm)

Supported by the formats:

| Format           | CommonMark               | GitHub Flavored          | XHTML | Inline PlantUML            |
| ---------------- | ------------------------ | ------------------------ | ----- | -------------------------- |
| docx             | X                        | X                        | -     | Embedded PNG               |
| dump             | Output as string literal | Output as string literal | -     | -                          |
| markdown         | X                        | X                        | -     | SVG (opt-in, see below)    |
| reStructuredText | X                        | X                        | -     | SVG via `.. image::`       |
| reqif            | X                        | X                        | X     | SVG via `<object>` element |

The `reqif` format additionally supports `"xhtml"` as a format specifier in the render configuration. When set, the attribute value is treated as already-valid XHTML and is embedded in the ReqIF output without any conversion. This allows requirement authors to write raw XHTML markup directly in their TRLC string attributes.

For the `markdown` format, inline PlantUML rendering is opt-in: pass `--render-plantuml` to the `markdown` subcommand to replace ```` ```plantuml```` blocks with SVG image references. Without this flag, PlantUML blocks are passed through unchanged — useful when the Markdown is consumed by a renderer that supports PlantUML natively (e.g. GitLab, some Sphinx extensions).

Configuration example:

```json
{
    "renderCfg": [{
        "package": ".*",
        "type": "Info",
        "attribute": "description",
        "format": "md"
    }]
}
```

The package, type and attribute fields support regex, which makes it easier to set the format for several types. Always the first match wins.

Use the `--renderCfg <RENDER-CFG-FILE>` program argument to specify the configuration file.

### Show tool version

Show the installed tool version.

```bash
pyTRLCConverter --version
```

### PlantUML

With the PlantUML extension the tool supports automatic diagram generation from PlantUML files.

Activate the support by setting the `PLANTUML` environment variable to either the path to a local `plantuml.jar` file or the URL of a PlantUML server.

| Environment Variable  | Description                                                                                                                                                     | Default |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `PLANTUML`            | Path to `plantuml.jar` or URL of PlantUML server.                                                                                                               | -       |
| `PLANTUML_VERIFY_SSL` | Set to `false` to disable SSL certificate verification for PlantUML server requests. Useful for internal servers with self-signed or corporate CA certificates. | `true`  |

## Examples

Check out the all the [Examples](./examples/README.md).

## Compile into an executable

It is possible to create an executable file that contains the tool and all its dependencies. "PyInstaller" is used for this.
Just run the following command on the root of the folder:

```cmd
pyinstaller --noconfirm --onefile --console --name "pyTRLCConverter" --add-data "./pyproject.toml;."  "./src/pyTRLCConverter/__main__.py"
```

## Publish to PyPI

Releasing a new version to [PyPI](https://pypi.org/project/pyTRLCConverter/) is automated via the `deploy.yml` GitHub Actions workflow. Creating and publishing a GitHub release triggers the following steps automatically:

1. Build the source distribution and wheel with `python -m build`.
2. Upload the artifacts to PyPI using OIDC trusted publishing (no API token required).

> **One-time setup:** Before the first automated release, configure a Trusted Publisher on PyPI (no API token needed). Go to the `pyTRLCConverter` project on PyPI → Manage → Publishing → Add a new publisher, and set Owner `NewTec-GmbH`, Repository `pyTRLCConverter`, Workflow `deploy.yml`.

To trigger a release:

1. Create and push a version tag, then publish a GitHub release for that tag.
2. The `publish-pypi` job in `deploy.yml` runs automatically and uploads the distribution to PyPI.

To test the build locally before releasing:

```bash
python -m pip install build twine
python -m build
twine check dist/*.whl dist/*.tar.gz
```

## SW Documentation

More information on the deployment and architecture can be found in the [documentation](./doc/README.md)

## Tools

Tools used for development or automation, see [Tools](./tools/README.md).

## Used Libraries

Used 3rd party libraries which are not part of the standard Python package:

| Library                                                      | Description                                              | License    |
| ------------------------------------------------------------ | -------------------------------------------------------- | ---------- |
| [Marko](https://github.com/frostming/marko)                  | A markdown parser with high extensibility.               | MIT        |
| [ReqIF](https://github.com/strictdoc-project/reqif)          | ReqIF is a Python library for working with ReqIF format. | Apache-2.0 |
| [PlantUML](https://github.com/plantuml/plantuml)             | Generate UML diagrams.                                   | GPL-3.0    |
| [python-docx](https://github.com/python-openxml/python-docx) | Creation of Microsoft Word 2007+ (.docx) files.          | MIT        |
| [requests](https://github.com/psf/requests)                  | HTTP processing                                          | Apache-2.0 |
| [sphinx](https://github.com/sphinx-doc/sphinx)               | Using Sphinx for documentation deployment.               | BSD        |
| [toml](https://github.com/uiri/toml)                         | Parsing [TOML](https://en.wikipedia.org/wiki/TOML)       | MIT        |
| [trlc](https://github.com/bmw-software-engineering/trlc)     | Treat Requirements Like Code                             | GPL-3.0    |

See also [requirements.txt](requirements.txt).

## Issues, Ideas And Bugs

If you have further ideas or you found some bugs, great! Create an [issue](https://github.com/NewTec-GmbH/pyTRLCConverter/issues) or if you are able and willing to fix it by yourself, clone the repository and create a pull request.

## License

The whole source code is published under [GPL-3.0](https://github.com/NewTec-GmbH/pyTRLCConverter/blob/main/LICENSE).
Consider the different licenses of the used third party libraries too!

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, shall be licensed as above, without any additional terms or conditions.
