# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate.ps1       # Windows PowerShell

pip install -e .
pip install -r requirements-dev.txt
```

## Common Commands

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_reqif.py

# Run a single test by name
pytest tests/test_reqif.py::test_function_name

# Lint (must be clean — no warnings or errors tolerated)
pylint --rcfile=.pylintrc src/pyTRLCConverter/

# Run the tool directly
pyTRLCConverter --source <trlc-dir> <subcommand>

# Run a conversion example
cd examples/reqif && ./generate_to_reqif.bat
```

## Architecture

### Converter Plugin Pattern

The core design is a **strategy/plugin pattern** around `AbstractConverter` (`src/pyTRLCConverter/abstract_converter.py`).

Every output format implements this interface:

```text
begin() → enter_file() → [convert_section() | convert_record_object()] × N → leave_file() → finish()
```

`BaseConverter` (`base_converter.py`) provides default no-op implementations and shared helpers (argument parsing, translation, render config, empty-value handling). All built-in converters subclass `BaseConverter`, not `AbstractConverter` directly.

Built-in converters registered in `__main__.py`:

- `MarkdownConverter` → `markdown`
- `DocxConverter` → `docx`
- `RstConverter` → `rst`
- `ReqifConverter` → `reqif`
- `DumpConverter` → `dump`

### Project-Specific Extension

A project supplies `--project <module.py>` with a class that subclasses `AbstractConverter` (or `BaseConverter`). The project converter replaces the built-in converter with the same subcommand name. This is the intended extensibility point — do not modify `__main__.py` to add project converters.

### Execution Flow

`__main__.main()` → `ItemWalker.walk_symbols()` drives the converter lifecycle. `ItemWalker` groups TRLC symbols by source file, calls `enter_file`/`leave_file` around per-file sections and records, and skips files listed in `--exclude`. TRLC parsing is done once via `trlc_helper.get_trlc_symbols()`.

### Markdown → Rich-Format Rendering

When a `--renderCfg` JSON file is provided, `RenderConfig` matches record attributes by `(package, type, attribute)` regex triplets and flags them as Markdown-formatted. Converters call `BaseConverter.render_attribute_value()` which uses `marko` to convert Markdown to the target-format-specific AST. Custom `marko` renderers live in `src/pyTRLCConverter/marko/`.

### ReqIF Converter Specifics

`ReqifConverter` builds a document in memory using the `reqif` library, then serialises with `ReqIFUnparser`. Two modes:

- **Multiple-document mode** (default): one `.reqif` per `.trlc` file, written in `leave_file()`.
- **Single-document mode** (`--single-document`): all TRLC files merged into one `.reqif`, written in `finish()`.

TRLC record references become `SPEC-RELATION` entries (not plain attributes); cross-file references require `--single-document`.

TRLC enumeration type attributes become `DATATYPE-DEFINITION-ENUMERATION` entries with `ENUM-VALUE` keys starting at 0 in RSL literal declaration order. The corresponding record field produces an `ATTRIBUTE-VALUE-ENUMERATION`. Optional enum fields with a null value are omitted from the spec-object entirely.

### New Features Workflow

When adding a new converter feature, follow this order to maintain full traceability:

1. **Requirements** — add `SwReq` entries in `trlc/swe-req/swe-req.trlc`.
2. **Architecture** — add or update `SwArchSpec` entries in `trlc/swe-arch/swe-arch.trlc`, referencing the new requirements in `satisfies`.
3. **Source code** — implement the feature; add `# lobster-trace: SwRequirements.<id>` comments to every method that implements a requirement.
4. **Test utilities** — create any needed `.rsl` / `.trlc` fixture files under `tests/utils/`.
5. **Test cases** — add `SwTestCase` entries in `trlc/swe-test/swe-test.trlc`, referencing the new requirements in `verifies`.
6. **Test code** — add `test_*` functions in `tests/test_reqif.py` (or the relevant test module); annotate each with `# lobster-trace: SwTests.<tc_id>` and `record_property("lobster-trace", "SwTests.<tc_id>")`.
7. **Validate** — run `pylint` (must score 10.00/10) and `pytest` (all tests must pass).

### Key Files

| File | Purpose |
| --- | --- |
| `src/pyTRLCConverter/abstract_converter.py` | Converter interface (subclass this for new formats) |
| `src/pyTRLCConverter/base_converter.py` | Shared implementation — subclass for built-in formats |
| `src/pyTRLCConverter/item_walker.py` | Drives the converter lifecycle over TRLC symbols |
| `src/pyTRLCConverter/trlc_helper.py` | TRLC AST parsing and symbol loading |
| `src/pyTRLCConverter/render_config.py` | `--renderCfg` JSON loader and attribute Markdown detection |
| `src/pyTRLCConverter/translator.py` | `--translation` JSON loader for attribute name mapping |
| `src/pyTRLCConverter/reqif_converter.py` | ReqIF output (uses `reqif` library) |

## Coding Standards

- Follow `coding-guidelines/README.md`: PEP8, Google-style docstrings, max line length 120.
- Lint with `.pylintrc` — zero warnings and zero errors required.
- Every function/method must have exactly one `return` statement.
- Every module, class, function, and method must have a docstring.
- Every Python file must start with a module docstring followed by the GPL v3 license header, then section separator comments (`# Imports ***...`, `# Variables ***...`, `# Classes ***...`, `# Functions ***...`, `# Main ***...`).
- Use `log_error()` / `log_verbose()` from `pyTRLCConverter.logger` — never `print()`.

See the `/python-coding-standard` skill for the full workflow and file template.

## ReqIF Output

Target format is ReqIF v1.2, following the ProSTEP ReqIF Implementation Guideline. Schema namespace: `http://www.omg.org/spec/ReqIF/20110401/reqif.xsd`. XHTML attribute values must be wrapped in `<div xmlns="http://www.w3.org/1999/xhtml">`.

See the `/reqif-format` skill for the full element reference and IG compliance checklist.

## TRLC Language

TRLC (Treat Requirements Like Code) is the DSL used for requirement definitions (`.rsl`) and instances (`.trlc`). Type definitions live in `trlc/model/`; requirement objects live in `trlc/swe-req/`, `trlc/swe-arch/`, and `trlc/swe-test/`.

See the `/trlc` skill for the full language reference, syntax rules, and project-specific patterns.

## Traceability

Requirements are traced in TRLC source files and linked to code via `# lobster-trace: SwRequirements.<id>` comments. Do not remove these trace comments when modifying traced functions.
