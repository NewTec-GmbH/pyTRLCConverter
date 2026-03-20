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
import json

from typing import Any
from urllib.parse import urlparse
from sphinx.errors import ConfigError

# pylint: skip-file

# Variables ********************************************************************

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pyTRLCConverter'
copyright = '2024 - 2026, NewTec GmbH'
author = 'NewTec GmbH'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # https://www.sphinx-doc.org/en/master/usage/markdown.html
    'myst_parser',
    'sphinx_rtd_theme',
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

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_js_files = ['version_selector.js']

# Copy favorite icon to static path.
html_favicon = '../../../doc/images/favicon.ico'

# Copy logo to static path.
html_logo = '../../../doc/images/NewTec_Logo.png'

# PlantUML is called OS depended and the java jar file is provided by environment variable.
plantuml_env = os.getenv('PLANTUML')
plantuml = []


def _build_version_links() -> tuple[str, list[tuple[str, str]]]:
    """Build documentation version selector entries for the RTD theme.

    It divides between local and deployed documentation based on the presence of environment variables.

    Environment parameters:
        DOCS_VERSION: Current docs version shown as active entry.
            Falls back to ``local`` if not set.
        DOCS_VERSIONS: Comma-separated list of versions shown in the selector.
            Defaults to ``latest,unstable``.
        DOCS_LATEST_TARGET: Version folder used for the ``latest`` selector entry.
            Defaults to ``latest``.
        DOCS_BASE_PATH: Base URL path for generated links.
            If not set, it is derived from GITHUB_REPOSITORY.

    Returns:
        tuple[str, list[tuple[str, str]]]:
            Current version and a list of ``(label, url)`` selector entries.
    """
    current_version = os.getenv('DOCS_VERSION') or 'local'
    version_links = []

    # Local documentation does not have version selector entries, as it is only used for development and testing.
    if current_version == 'local':
        version_links.append(('local', '.'))

    # For deployed documentation, build the version selector entries based on environment variables.
    else:
        configured_versions = os.getenv('DOCS_VERSIONS', 'unstable')
        latest_target = os.getenv('DOCS_LATEST_TARGET', 'latest').strip() or 'latest'
        versions = [version.strip() for version in configured_versions.split(',') if version.strip()]

        if current_version not in versions:
            versions.insert(0, current_version)

        docs_base_path = os.getenv('DOCS_BASE_PATH', '')
        if not docs_base_path:
            repository = os.getenv('GITHUB_REPOSITORY', '')
            if '/' in repository:
                docs_base_path = f"/{repository.split('/', maxsplit=1)[1]}"

        docs_base_path = docs_base_path.rstrip('/')
        for version in versions:
            if docs_base_path:
                version_links.append((version, f"{docs_base_path}/{version}/"))
            else:
                version_links.append((version, f"/{version}/"))

        if docs_base_path:
            latest_url = f"{docs_base_path}/{latest_target}/"
        else:
            latest_url = f"/{latest_target}/"

        version_links.insert(0, ('latest', latest_url))

    return current_version, version_links

current_version, versions_for_selector = _build_version_links()
html_context = {
    'current_version': current_version,
    'version': current_version,
    'versions': versions_for_selector
}

# Classes **********************************************************************

# Functions ********************************************************************

# List of files to copy to the output directory.
#
# The source is relative to the sphinx directory.
# The destination is relative to the output directory.
files_to_copy = [
    {
        'source': '../testReport/out/coverage',
        'destination': 'coverage',
        'exclude': []
    },
    {
        'source': '../trlc2other/out',
        'destination': '.',
        'exclude': ['*.rst']
    }
]

def setup(app: Any) -> None:
    """Setup sphinx.

    Args:
        app (Any): The sphinx application.
    """
    app.connect('builder-inited', write_version_selector_data)
    app.connect('builder-inited', copy_files)


def write_version_selector_data(app: Any) -> None:
    """Create selector data consumed by local version selector JavaScript.

    Args:
        app (Any): The sphinx application.
    """
    static_dir = os.path.join(os.path.dirname(__file__), '_static')
    selector_file = os.path.join(static_dir, 'version_selector_data.js')

    selector_data = {
        'current': current_version,
        'versions': [{'label': slug, 'url': url} for slug, url in versions_for_selector]
    }

    with open(selector_file, 'w', encoding='utf-8') as file:
        file.write(
            f"window.PYTRLC_DOCS_VERSION_SELECTOR = {json.dumps(selector_data)};\n"
        )

def copy_files(app: Any) -> None:
    """Copy files to the output directory.

    Args:
        app (Any): The sphinx application.
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
