"""Configuration file for the Sphinx documentation builder.

    For the full list of built-in configuration values, see the documentation:
    https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# pyTRLCConverter - A tool to convert PlantUML diagrams to image files.
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
import shutil
import fnmatch

from urllib.parse import urlparse
from sphinx.errors import ConfigError

# pylint: skip-file

# Variables ********************************************************************

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyTRLCConverter'
copyright = '2025, NewTec GmbH'
author = 'NewTec GmbH'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # https://www.sphinx-doc.org/en/master/usage/markdown.html
    'myst_parser',

    # https://github.com/sphinx-contrib/plantuml
    'sphinxcontrib.plantuml'
]

templates_path = ['_templates']
exclude_patterns = []

# Support restructured text and Markdown
source_suffix = ['.rst', '.md']

rst_prolog = """
.. include:: <s5defs.txt>

"""

# -- MyST parser configuration ---------------------------------------------------

# Configure MyST parser to generate GitHub-style anchors
myst_heading_anchors = 6

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'haiku'
html_static_path = ['_static']
html_style = 'custom.css'

# Copy favorite icon to static path.
html_favicon = '../../../doc/images/favicon.ico'

# Copy logo to static path.
html_logo = '../../../doc/images/NewTec_Logo.png'

# PlantUML is called OS depended and the java jar file is provided by environment variable.
plantuml_env = os.getenv('PLANTUML')
plantuml = []

# Classes **********************************************************************

# Functions ********************************************************************

# List of files to copy to the output directory.
#
# The source is relative to the sphinx directory.
# The destination is relative to the output directory.
files_to_copy = [
    {
        'source': '../createTestReport/out/coverage',
        'destination': 'coverage',
        'exclude': []
    },
    {
        'source': '../req2rst/out/sw-requirements/rst',
        'destination': '.',
        'exclude': ['*.rst']
    },
    {
        'source': '../tc2rst/out/sw-tests/rst',
        'destination': '.',
        'exclude': ['*.rst']
    }
]

def setup(app: any) -> None:
    """Setup sphinx.

    Args:
        app (any): The sphinx application.
    """
    app.connect('builder-inited', copy_files)

def copy_files(app: any) -> None:
    """Copy files to the output directory.

    Args:
        app (any): The sphinx application.
    """
    for files in files_to_copy:
        source = os.path.abspath(files['source'])
        destination = os.path.join(app.outdir, files['destination'])

        if not os.path.exists(destination):
            os.makedirs(destination)
        
        for filename in os.listdir(source):
            if not any(fnmatch.fnmatch(filename, pattern) for pattern in files['exclude']):
                full_file_name = os.path.join(source, filename)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, destination)

# Main *************************************************************************

if plantuml_env is None:
    raise ConfigError(
        "The environment variable PLANTUML is not defined to either the location "
        "of plantuml.jar or server URL.\n"
        "Set plantuml to either <path>/plantuml.jar or a server URL.")

if  urlparse(plantuml_env).scheme in ['http', 'https']:
    plantuml = [plantuml_env]
else:
    if os.path.isfile(plantuml_env):
        plantuml = ['java', '-jar', plantuml_env]
    else:
        raise ConfigError(
            f"The environment variable PLANTUML points to a not existing file {plantuml_env}."
        )
