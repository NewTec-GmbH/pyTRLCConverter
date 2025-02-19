# pyTRLCConverter <!-- omit in toc -->

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/NewTec-GmbH/pyTRLCConverter/blob/main/LICENSE) [![Repo Status](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip) [![CI](https://github.com/NewTec-GmbH/pyTRLCConverter/actions/workflows/test.yml/badge.svg)](https://github.com/NewTec-GmbH/pyTRLCConverter/actions/workflows/test.yml)
[![Repo Status](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

pyTRLCConverter is a command-line tool to convert TRLC files to different output formats, e.g. Markdown.
Because the definition of TRLC types is project specific, it supports to inject project specific conversion functions for sections and record objects.

- [Overview](#overview)
- [Installation](#installation)
  - [Clone this Project](#clone-this-project)
  - [Setup a virtual Python Environment](#setup-a-virtual-python-environment)
  - [Tool Installation](#tool-installation)
- [Usage](#usage)
  - [Convert to required format](#convert-to-required-format)
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

```bash
pip install -e .
```

## Usage

### Convert to required format

TODO

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

| Library | Description | License |
| ------- | ----------- | ------- |
| [PlantUML](https://github.com/plantuml/plantuml) | Generate UML diagrams. | GPL-3.0 |
| [python-docx](https://github.com/python-openxml/python-docx) | Creation of Microsoft Word 2007+ (.docx) files. | MIT |
| [requests](https://github.com/psf/requests) | HTTP processing | Apache-2.0 |
| [sphinx](https://github.com/sphinx-doc/sphinx) | Using Sphinx for documentation deployment. | BSD |
| [toml](https://github.com/uiri/toml) | Parsing [TOML](https://en.wikipedia.org/wiki/TOML) | MIT |
| [trlc](https://github.com/bmw-software-engineering/trlc) | Treat Requirements Like Code | GPL-3.0 |

see also [requirements.txt](requirements.txt)

## Issues, Ideas And Bugs

If you have further ideas or you found some bugs, great! Create an [issue](https://github.com/NewTec-GmbH/pyTRLCConverter/issues) or if you are able and willing to fix it by yourself, clone the repository and create a pull request.

## License

The whole source code is published under [GPL-3.0](https://github.com/NewTec-GmbH/pyTRLCConverter/blob/main/LICENSE).
Consider the different licenses of the used third party libraries too!

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, shall be licensed as above, without any additional terms or conditions.
