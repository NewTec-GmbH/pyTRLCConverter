---
name: python-coding-standard
description: "Apply pyTRLCConverter Python coding standards. Use when: writing or refactoring Python code, making code PEP8 compliant, resolving pylint warnings/errors using .pylintrc, enforcing one return per function/method, adding missing docstrings, and aligning file section separators."
argument-hint: "Optional: target file(s) or module name"
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# Python Coding Standard (pyTRLCConverter)

Apply this workflow whenever Python code is created or changed.

## Goals

- Keep code PEP8 compliant.
- Use Python typing.
- Keep pylint warning and error free, using the repository `.pylintrc`.
- Ensure each function and method has exactly one `return` statement.
- Ensure all modules, classes, functions, and methods have docstrings including parameter and return descriptions.
- Keep the same section separator comments used in existing Python files.
- Include the GPL license header in every Python file.
- All pytest tests must run successfully.

## Required File Structure

### File Header (License)

Every Python file must start with:

1. Module docstring with description and optional author
2. GPL v3 license header (copyright notice and license details)
3. Blank line
4. Section separators for imports, variables, classes, etc.

Example:

```python
"""Module description here.

    Author: Your Name (your.email@newtec.de)
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

# Variables ********************************************************************

# Classes **********************************************************************

# Functions ********************************************************************

# Main *************************************************************************
```

Use these sections in this order. Update the copyright year and author as needed.

Inside classes, use additional section headers where appropriate (for example helper groups) and keep the same separator style used in existing files.

## Procedure

1. **License and docstring**: Start every file with module docstring, then the GPL v3 license header (see Required File Structure above).
2. Read and follow `.pylintrc` before making changes.
3. Match existing repository style for spacing, naming, typing, and formatting.
4. Add or complete docstrings for:
   - module
   - class
   - function
   - method
5. Refactor functions/methods so each has only one `return`.
6. Keep logic readable by using intermediate variables instead of multiple early returns.
7. Preserve behavior while refactoring.
8. Ensure imports are clean and ordered, and remove unused imports.
9. Validate code with pylint using the repository config.
10. Run pytest to ensure all tests pass with the code changes.

## Validation Commands

Run pylint with the repository config:

```powershell
pylint --rcfile=.pylintrc $ARGUMENTS
```

Run all pytest tests:

```powershell
pytest
```

Or to run tests for specific modules:

```powershell
pytest tests/<test_module>.py
```

Treat any pylint warning, error, or pytest failure as a required fix.

## Completion Checklist

- GPL license header is present at the top of every Python file.
- Module docstring is present with description and optional author.
- `.pylintrc` was considered and applied.
- PEP8 style is respected.
- Pylint reports no warnings and no errors for changed files.
- All pytest tests pass without failures.
- Each function/method has one `return` statement.
- All required docstrings are present and meaningful.
- File section separators match repository conventions.
- No unrelated refactoring was introduced.
