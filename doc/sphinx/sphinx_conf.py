"""Project specific Sphinx configuration of the pyTRLCConverter documentation.

    trlcdoc builds the site (see trlcdoc.yaml, html: conf). Its generic conf.py sets the
    project values, the theme, logo, favicon and PlantUML, and executes this file at its
    end. All names of that conf.py are available here without import, e.g. PROJECT_ROOT,
    html_static_path, os and json, see the trlcdoc configuration reference, chapter 8.2.
    Build paths from PROJECT_ROOT: this file runs in the generated Sphinx folder.
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

# The names of the trlcdoc conf.py are unknown to code checkers.
# pylint: skip-file

# Variables ********************************************************************

# API reference of the SW detailed design, generated from the source code.
# https://sphinx-autoapi.readthedocs.io/en/latest/tutorials.html#python
autoapi_dirs = [str(PROJECT_ROOT / 'src')]
autoapi_root = 'api'
autoapi_ignore = ['*/marko/*']      # Exclude internal marko renderers from public API docs
autoapi_add_toctree_entry = False   # Included manually in sw_detail_design.rst
autoapi_member_order = 'groupwise'  # Classes, then functions, then attributes
autoapi_options = [
    'members',                  # Show module/class members
    'undoc-members',            # Include members without docstrings
    'private-members',          # Include private members (starting with _)
    'special-members',          # Include special members (starting and ending with __)
    'show-inheritance',         # Show base classes on class pages
    'show-inheritance-diagram', # Show inheritance diagrams for classes
    'show-module-summary'       # Summary table at the top of each module page
]
suppress_warnings = ['autoapi.python_import_resolution', 'autoapi.not_readable']

inheritance_graph_attrs = {
    'rankdir': 'TB',  # Top-to-bottom layout (use 'LR' for left-to-right)
    'size': '"8.0, 12.0"',
    'bgcolor': 'transparent',
}
inheritance_edge_attrs = {
    'arrowsize': '1.5',
}

# Read the Docs theme with NewTec colors, the project stylesheet and the version selector.
# Append to html_static_path, trlcdoc's _static folder holds the s5defs.txt roles.
html_static_path.append(str(PROJECT_ROOT / 'doc' / 'sphinx' / '_static'))
html_css_files = ['pytrlcconverter.css']
html_js_files = ['version_selector.js']
html_theme_options = {
    'style_nav_header_background': '#0C2C40',   # NewTec black
}

# Classes **********************************************************************

# Functions ********************************************************************


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

        if latest_target not in versions:
            if docs_base_path:
                latest_url = f"{docs_base_path}/{latest_target}/"
            else:
                latest_url = f"/{latest_target}/"
            version_links.insert(0, ('latest', latest_url))

    return current_version, version_links


def write_version_selector_data(app: Any) -> None:
    """Create selector data consumed by the version selector JavaScript.

    The data is written into the _static folder of the generated Sphinx sources,
    from where Sphinx copies it into the site.

    Args:
        app (Any): The sphinx application.
    """
    selector_file = Path(app.srcdir) / '_static' / 'version_selector_data.js'
    selector_data = {
        'current': current_version,
        'versions': [{'label': slug, 'url': url} for slug, url in versions_for_selector]
    }
    selector_file.write_text(f"window.PYTRLC_DOCS_VERSION_SELECTOR = {json.dumps(selector_data)};\n",
                             encoding='utf-8')


def setup(app: Any) -> None:
    """Register the project hooks, called by trlcdoc after its own setup.

    Args:
        app (Any): The sphinx application.
    """
    app.connect('builder-inited', write_version_selector_data)

# Main *************************************************************************


current_version, versions_for_selector = _build_version_links()
html_context = {
    'current_version': current_version,
    'version': current_version,
    'versions': versions_for_selector
}
