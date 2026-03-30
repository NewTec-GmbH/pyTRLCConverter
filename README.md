# pyTRLCConverter <!-- omit in toc -->

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/NewTec-GmbH/pyTRLCConverter/blob/main/LICENSE) [![Repo Status](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip) [![CI](https://github.com/NewTec-GmbH/pyTRLCConverter/actions/workflows/test.yml/badge.svg)](https://github.com/NewTec-GmbH/pyTRLCConverter/actions/workflows/test.yml)
[![Repo Status](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

pyTRLCConverter is a command-line tool to convert [TRLC (Treat Requirements Like Code)](https://github.com/bmw-software-engineering/trlc) files to different output formats. Since the definition of TRLC types is project-specific, the built-in converters can be extended in an object-oriented manner.

Currently out of the box supported formats:

* Markdown
* docx
* reStructuredText
* ReqIF
* dump

Find the requirements, test cases, coverage and etc. on the [github pages](https://newtec-gmbh.github.io/pyTRLCConverter/).

## Table of Contents <!-- omit in toc -->

- [Overview](#overview)
- [Installation](#installation)
  - [Clone this Project](#clone-this-project)
  - [Setup a virtual Python Environment](#setup-a-virtual-python-environment)
  - [Tool Installation](#tool-installation)
- [Usage](#usage)
  - [Conversion to Markdown format](#conversion-to-markdown-format)
  - [Conversion to docx format](#conversion-to-docx-format)
  - [Conversion to reStructuredText format](#conversion-to-restructuredtext-format)
  - [Conversion to ReqIF format](#conversion-to-reqif-format)
  - [Dump TRLC item list to console](#dump-trlc-item-list-to-console)
  - [Apply attribute name translation](#apply-attribute-name-translation)
  - [Requirement description in Markdown](#requirement-description-in-markdown)
  - [Show tool version](#show-tool-version)
  - [PlantUML](#plantuml)
- [Examples](#examples)
- [Compile into an executable](#compile-into-an-executable)
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

- For Windows CMD shell, use ```.venv\Scripts\activate.bat``` to activate the virtual environment.
- For Linux/Macos, use ```source .venv/bin/activate``` to activate the virtual environment.

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

## Usage

### Conversion to Markdown format

The tool requires two kinds of TRLC input sources for the conversion. These are the requirements (\*.trlc) files and the model (\*.tls) files. These input files are specified using one or more --source  or -s options followed by a file name or directory path. If a path is given, all files with a .trlc or .tls extension are read by the tool.

```bash
pyTRLCConverter --source trlc/model --source trlc/swe-req markdown
```

It will create a Markdown file with the same name as the requirements file (\*.trlc) in the current directory, but with the Markdown extension (.md).

If the requirements are split into several files, a Markdown file will be created for each. To generate a single Markdown file the argument --single-document can be used, which will create an ```output.md``` file by default.

The converter supports additional arguments that are shown by adding the --help option after the markdown subcommand.

```bash
pyTRLCConverter markdown --help

usage: pyTRLCConverter markdown [-h] [-n NAME] [-sd] [-tl TOP_LEVEL]

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Name of the generated output file inside the output folder (default = output.md) in case a single document is generated.
  -sd, --single-document
                        Generate a single document instead of multiple files. The default is to generate multiple files.
  -tl TOP_LEVEL, --top-level TOP_LEVEL
                        Name of the top level heading, required in single document mode. (default = Specification)
```

More examples are shown in the [examples folder](./examples/).

### Conversion to docx format

Similar to the Markdown conversion, minimal required are the requirements (\*.trlc) and the model (\*.tls). Both can be added by file name or just the path where they are located.

```bash
pyTRLCConverter --source trlc/model --source trlc/swe-req docx
```

It will create a docx file with default name ```output.docx``` in the current directory.

If the requirements are split in several files, they will be all part of a single docx file.

The converter supports additional arguments that are shown by adding the --help option after the docx subcommand.

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

The tool requires two kinds of TRLC input sources for the conversion. These are the requirements (\*.trlc) files and the model (\*.tls) files. These input files are specified using one or more --source  or -s options followed by a file name or directory path. If a path is given, all files with a .trlc or .tls extension are read by the tool.

```bash
pyTRLCConverter --source trlc/model --source trlc/swe-req rst
```

If the requirements are split into several files (\*.trlc), a reStructuredText file will be created for each. To generate a single reStructuredText file the argument --single-document can be used, which will create an ```output.md``` file by default.

The converter supports additional arguments that are shown by adding the --help option after the reStructuredText subcommand.

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

The tool requires two kinds of TRLC input sources for the conversion. These are the requirements (*.trlc) files and the model (*.tls) files. These input files are specified using one or more --source or -s options followed by a file name or directory path. If a path is given, all files with a .trlc or .tls extension are read by the tool.

```bash
pyTRLCConverter --source trlc/model --source trlc/swe-req reqif
```

If the requirements are split into several files (*.trlc), a ReqIF file will be created for each. To generate a single ReqIF file the argument --single-document can be used, which will create an `output.reqif` file by default.

The converter supports additional arguments that are shown by adding the --help option after the ReqIF subcommand.

```bash
pyTRLCConverter reqif --help

usage: pyTRLCConverter reqif [-h] [-e EMPTY] [-n NAME] [-sd] [-tl TOP_LEVEL]

options:
  -h, --help            show this help message and exit
  -e EMPTY, --empty EMPTY
                        Every attribute value which is empty will output the string (default = N/A).
  -n NAME, --name NAME  Name of the generated output file inside the output folder (default = output.reqif) in case a single document is generated.
  -sd, --single-document
                        Generate a single document instead of multiple files. The default is to generate multiple files.
  -tl TOP_LEVEL, --top-level TOP_LEVEL
                        Name of the top level section, required in single document mode (default = Specification).
```

Markdown-formatted requirement attributes configured via `--renderCfg` are automatically converted to ReqIF-compatible XHTML content.

Conversion rules:

**Types and spec-objects:**

* Each distinct TRLC record type is mapped to one `SPEC-OBJECT-TYPE`. The type's attributes are reflected as `ATTRIBUTE-DEFINITION-*` entries on the type.
* TRLC `section` headings are mapped to a dedicated `SPEC-OBJECT-TYPE` named `Section` and produce a container `SPEC-OBJECT` in the hierarchy.
* Every TRLC record object produces one `SPEC-OBJECT` of the matching `SPEC-OBJECT-TYPE`.

**Attribute mapping by field type:**

| TRLC field type | ReqIF datatype | ReqIF attribute value |
| --- | --- | --- |
| String / Integer / Boolean / Decimal | `DATATYPE-DEFINITION-XHTML` | `ATTRIBUTE-VALUE-XHTML` — plain text is HTML-escaped and wrapped in `<p>` tags |
| String with Markdown render config | `DATATYPE-DEFINITION-XHTML` | `ATTRIBUTE-VALUE-XHTML` — Markdown is converted to XHTML via `marko` |
| Enumeration | `DATATYPE-DEFINITION-ENUMERATION` | `ATTRIBUTE-VALUE-ENUMERATION` — enum value keys start at 0 and follow the literal declaration order in the RSL model |
| Record reference / array of references | — | Converted to `SPEC-RELATION` entries (see below) |
| Optional field with `null` value | — | Attribute is omitted from the `SPEC-OBJECT` |

**Record name:**

- The TRLC record name is mapped to an explicit `ATTRIBUTE-VALUE-STRING` attribute named `ReqIF.ForeignID` on the owning `SPEC-OBJECT-TYPE`.

**Record references:**

- TRLC record reference fields (single or array) are converted to `SPEC-RELATION-TYPE` and `SPEC-RELATION` entries.
- The relation type name is the TRLC attribute name, for example `derived`.
- The reference field is not emitted as a regular object attribute.
- This preserves traceability links in a form that can be imported by DOORS Next.
- The source and target records must be part of the same generated ReqIF document. Use `--single-document` when references span multiple TRLC files.

### Dump TRLC item list to console

Mainly for development all TRLC items can be dumped to the console.

```bash
pyTRLCConverter --source trlc/model --source trlc/swe-req dump
```

### Apply attribute name translation

The built-in converters display the requirements and their attributes in a table. The first column always contains the attribute name, and the second column contains the attribute value. Since the attribute names must comply with the TRLC standard, they are not always human-readable.

Therefore a translation JSON file can be used to translate the attribute names. Use the ```--translation``` argument to specify the translation file.

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

- "md": [CommonMark's spec v0.31.2](https://spec.commonmark.org/0.31.2/)
- "gfm": [GitHub Flavored Markdown spec v0.29-gfm](https://github.github.com/gfm)

Supported by the formats:

| Format           | CommonMark               | GitHub Flavored          |
| ---------------- | ------------------------ | ------------------------ |
| docx             | X                        | Output as string literal |
| dump             | Output as string literal | Output as string literal |
| markdown         | X                        | X                        |
| reStructuredText | X                        | X                        |
| reqif            | X                        | X                        |

The `reqif` format additionally supports `"xhtml"` as a format specifier in the render configuration. When set, the attribute value is treated as already-valid XHTML and is embedded in the ReqIF output without any conversion. This allows requirement authors to write raw XHTML markup directly in their TRLC string attributes.

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

The package, type and attribute supports regex which makes it easier to set the format for several types. Currently **only Markdown** is supported as format. Always the first match wins.

Use the ```--renderCfg <RENDER-CFG-FILE>``` program argument to specify the configuration file.

### Show tool version

Show the version of the tool to see whether the required one is used.

```bash
pyTRLCConverter --help
```

### PlantUML

With the PlantUML extension the tool supports the automatic diagram generation out of a PlantUML file.

Activate the support by adding the path to the java jar file to the ```PLANTUML``` environment variable.

## Examples

Check out the all the [Examples](./examples).

## Compile into an executable

It is possible to create an executable file that contains the tool and all its dependencies. "PyInstaller" is used for this.
Just run the following command on the root of the folder:

```cmd
pyinstaller --noconfirm --onefile --console --name "pyTRLCConverter" --add-data "./pyproject.toml;."  "./src/pyTRLCConverter/__main__.py"
```

## SW Documentation

More information on the deployment and architecture can be found in the [documentation](./doc/README.md)

For Detailed Software Design run `$ /doc/detailed-design/make html` to generate the detailed design documentation that then can be found
in the folder `/doc/detailed-design/_build/html/index.html`

## Tools

Tools used for development or automations, see [Tools](./tools/README.md).

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

see also [requirements.txt](requirements.txt)

## Issues, Ideas And Bugs

If you have further ideas or you found some bugs, great! Create an [issue](https://github.com/NewTec-GmbH/pyTRLCConverter/issues) or if you are able and willing to fix it by yourself, clone the repository and create a pull request.

## License

The whole source code is published under [GPL-3.0](https://github.com/NewTec-GmbH/pyTRLCConverter/blob/main/LICENSE).
Consider the different licenses of the used third party libraries too!

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, shall be licensed as above, without any additional terms or conditions.
