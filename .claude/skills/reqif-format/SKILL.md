---
name: reqif-format
description: "Apply ReqIF v1.2 format rules and Implementation Guideline (IG) compliance when working on ReqIF output in pyTRLCConverter. Use when: implementing or modifying reqif_converter.py, generating .reqif files, adding new data types or attribute definitions, handling XHTML content, or validating ReqIF output structure."
argument-hint: "Optional: target file or feature area (e.g. reqif_converter.py, xhtml, datatypes)"
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# ReqIF Format Skill (pyTRLCConverter)

Apply this workflow whenever ReqIF output or the `reqif_converter.py` is created or changed.

## Standard References

- **ReqIF v1.2** – OMG standard, schema namespace: `http://www.omg.org/spec/ReqIF/20110401/reqif.xsd`
- **ReqIF Implementation Guideline (IG)** – ProSTEP iViP association, latest version (v9.x). Adds interoperability rules on top of the base OMG spec.
- **Python `reqif` library** – used in this project via `reqif.*` imports (see `src/pyTRLCConverter/reqif_converter.py`).

## ReqIF v1.2 Document Structure

A valid `.reqif` file has this top-level structure (element order is mandatory):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<REQ-IF xmlns="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:xhtml="http://www.w3.org/1999/xhtml"
        xsi:schemaLocation="http://www.omg.org/spec/ReqIF/20110401/reqif.xsd
                            http://www.omg.org/spec/ReqIF/20110401/reqif.xsd">
  <THE-HEADER>
    <REQ-IF-HEADER IDENTIFIER="...">
      <COMMENT>...</COMMENT>
      <CREATION-TIME>...</CREATION-TIME>       <!-- ISO 8601 with timezone -->
      <REPOSITORY-ID>...</REPOSITORY-ID>
      <REQ-IF-TOOL-ID>...</REQ-IF-TOOL-ID>
      <REQ-IF-VERSION>1.2</REQ-IF-VERSION>     <!-- Must be "1.2" for v1.2 -->
      <SOURCE-TOOL-ID>...</SOURCE-TOOL-ID>
      <TITLE>...</TITLE>
    </REQ-IF-HEADER>
  </THE-HEADER>
  <CORE-CONTENT>
    <REQ-IF-CONTENT>
      <DATATYPES>   <!-- Data type definitions -->
      <SPEC-TYPES>  <!-- Spec-object types, relation types, specification types -->
      <SPEC-OBJECTS>
      <SPEC-RELATIONS>
      <SPECIFICATIONS>
      <SPEC-RELATION-GROUPS>   <!-- Optional -->
    </REQ-IF-CONTENT>
  </CORE-CONTENT>
  <TOOL-EXTENSIONS>  <!-- Optional, tool-specific data -->
</REQ-IF>
```

## Data Types (DATATYPES)

All data type definitions require `IDENTIFIER`, `LAST-CHANGE`, and `LONG-NAME` attributes.

| Element | Key Attributes | Notes |
|---|---|---|
| `DATATYPE-DEFINITION-BOOLEAN` | — | Boolean true/false |
| `DATATYPE-DEFINITION-DATE` | — | ISO 8601 datetime |
| `DATATYPE-DEFINITION-ENUMERATION` | child `SPECIFIED-VALUES` with `ENUM-VALUE` entries | Each `ENUM-VALUE` needs `IDENTIFIER`, `LAST-CHANGE`, `LONG-NAME`, `KEY` (integer) |
| `DATATYPE-DEFINITION-INTEGER` | `MIN`, `MAX` (optional) | |
| `DATATYPE-DEFINITION-REAL` | `ACCURACY`, `MIN`, `MAX` (optional) | |
| `DATATYPE-DEFINITION-STRING` | `MAX-LENGTH` | Used for plain string attributes |
| `DATATYPE-DEFINITION-XHTML` | — | Rich text; content must be XHTML-namespaced |

This project uses `DATATYPE-DEFINITION-STRING` (identifier: `datatype-string`, MAX-LENGTH 255) and `DATATYPE-DEFINITION-XHTML` (identifier: `datatype-xhtml`) as the two standard types.

## Spec Types (SPEC-TYPES)

### SPEC-OBJECT-TYPE
Defines the schema for a spec object. Contains `SPEC-ATTRIBUTES` with `ATTRIBUTE-DEFINITION-*` children.

```xml
<SPEC-OBJECT-TYPE IDENTIFIER="..." LAST-CHANGE="..." LONG-NAME="...">
  <SPEC-ATTRIBUTES>
    <ATTRIBUTE-DEFINITION-XHTML IDENTIFIER="..." LAST-CHANGE="..." LONG-NAME="...">
      <TYPE>
        <DATATYPE-DEFINITION-XHTML-REF>datatype-xhtml</DATATYPE-DEFINITION-XHTML-REF>
      </TYPE>
    </ATTRIBUTE-DEFINITION-XHTML>
    <ATTRIBUTE-DEFINITION-STRING IDENTIFIER="..." LAST-CHANGE="..." LONG-NAME="...">
      <TYPE>
        <DATATYPE-DEFINITION-STRING-REF>datatype-string</DATATYPE-DEFINITION-STRING-REF>
      </TYPE>
    </ATTRIBUTE-DEFINITION-STRING>
  </SPEC-ATTRIBUTES>
</SPEC-OBJECT-TYPE>
```

### SPEC-RELATION-TYPE
Defines a named relation category (e.g. "derived", "satisfies"). Contains optional `SPEC-ATTRIBUTES`.

### SPECIFICATION-TYPE
Defines the schema of a specification document. Contains optional `SPEC-ATTRIBUTES`.

## Spec Objects (SPEC-OBJECTS)

Each `SPEC-OBJECT` represents one requirement or section node.

```xml
<SPEC-OBJECT IDENTIFIER="..." LAST-CHANGE="..." LONG-NAME="...">
  <VALUES>
    <ATTRIBUTE-VALUE-XHTML>
      <DEFINITION>
        <ATTRIBUTE-DEFINITION-XHTML-REF>...</ATTRIBUTE-DEFINITION-XHTML-REF>
      </DEFINITION>
      <THE-VALUE><div xmlns="http://www.w3.org/1999/xhtml"><p>content</p></div></THE-VALUE>
    </ATTRIBUTE-VALUE-XHTML>
    <ATTRIBUTE-VALUE-STRING THE-VALUE="...">
      <DEFINITION>
        <ATTRIBUTE-DEFINITION-STRING-REF>...</ATTRIBUTE-DEFINITION-STRING-REF>
      </DEFINITION>
    </ATTRIBUTE-VALUE-STRING>
  </VALUES>
  <TYPE>
    <SPEC-OBJECT-TYPE-REF>...</SPEC-OBJECT-TYPE-REF>
  </TYPE>
</SPEC-OBJECT>
```

## Spec Relations (SPEC-RELATIONS)

Links between two spec objects with a typed relation.

```xml
<SPEC-RELATION IDENTIFIER="..." LAST-CHANGE="..." LONG-NAME="...">
  <TYPE>
    <SPEC-RELATION-TYPE-REF>...</SPEC-RELATION-TYPE-REF>
  </TYPE>
  <SOURCE>
    <SPEC-OBJECT-REF>...</SPEC-OBJECT-REF>
  </SOURCE>
  <TARGET>
    <SPEC-OBJECT-REF>...</SPEC-OBJECT-REF>
  </TARGET>
</SPEC-RELATION>
```

## Specifications and Hierarchy (SPECIFICATIONS)

A `SPECIFICATION` organises spec objects into a tree via `SPEC-HIERARCHY` nodes. Each leaf must reference a `SPEC-OBJECT`.

```xml
<SPECIFICATION IDENTIFIER="..." LAST-CHANGE="..." LONG-NAME="...">
  <TYPE>
    <SPECIFICATION-TYPE-REF>...</SPECIFICATION-TYPE-REF>
  </TYPE>
  <CHILDREN>
    <SPEC-HIERARCHY IDENTIFIER="..." IS-EDITABLE="false" IS-TABLE-INTERNAL="false"
                    LAST-CHANGE="..." LONG-NAME="...">
      <OBJECT>
        <SPEC-OBJECT-REF>...</SPEC-OBJECT-REF>
      </OBJECT>
      <CHILDREN>
        <!-- nested SPEC-HIERARCHY elements -->
      </CHILDREN>
    </SPEC-HIERARCHY>
  </CHILDREN>
  <VALUES/>
</SPECIFICATION>
```

## XHTML Content Rules (IG)

Per the ReqIF IG, XHTML content inside `THE-VALUE` must:

1. Be wrapped in `<div xmlns="http://www.w3.org/1999/xhtml">...</div>` — the `xmlns` declaration is mandatory on the `div`.
2. Use only XHTML 1.0 Strict elements (no HTML5-only tags).
3. Be well-formed XML (all tags closed, attributes quoted).
4. Not contain bare text — wrap all text in block elements (`<p>`, `<ul>`, `<table>`, etc.).
5. Escape special characters (`<`, `>`, `&`) in text nodes as XML entities.
6. Tables must use `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>` — no `border` attributes.
7. Images must use a fully qualified URI; relative paths are not portable.

This project converts Markdown to XHTML using `marko` (`Markdown()` and `Markdown(extensions=["gfm"])`).

## Implementation Guideline (IG) Compliance Rules

Key rules from the ProSTEP ReqIF IG that apply to generated output:

| Rule | Requirement |
|---|---|
| **IG-001** | `REQ-IF-VERSION` in `REQ-IF-HEADER` must be `1.2` for v1.2 files. |
| **IG-002** | All `IDENTIFIER` values must be unique within the document. Prefer stable, reproducible IDs (e.g. derived from record name + type). |
| **IG-003** | `LAST-CHANGE` and `CREATION-TIME` must use ISO 8601 format with UTC offset (e.g. `2026-03-26T16:43:32+00:00`). |
| **IG-004** | Every attribute value element must reference an `ATTRIBUTE-DEFINITION` that is defined in the `SPEC-OBJECT-TYPE` of its parent `SPEC-OBJECT`. |
| **IG-005** | Every `SPEC-OBJECT-TYPE-REF`, `SPEC-RELATION-TYPE-REF`, `SPECIFICATION-TYPE-REF`, `DATATYPE-DEFINITION-*-REF` must resolve to an existing `IDENTIFIER` in the same document. |
| **IG-006** | `SPEC-HIERARCHY` nodes must form a tree (no cycles). Each `SPEC-OBJECT` may appear in the hierarchy multiple times but must exist in `SPEC-OBJECTS`. |
| **IG-007** | XHTML `THE-VALUE` content must be valid, namespace-qualified XHTML (see XHTML rules above). |
| **IG-008** | File encoding must be UTF-8; the XML declaration must state `encoding="UTF-8"`. |
| **IG-009** | Empty attribute values should either be omitted or use a designated placeholder string — do not emit empty `THE-VALUE` elements for non-XHTML types. |
| **IG-010** | `ENUM-VALUE` keys within a single `DATATYPE-DEFINITION-ENUMERATION` must be unique integers. |
| **IG-011** | `SPEC-RELATION-GROUPS` (if present) must reference valid `SPEC-RELATION-TYPE`, and their member relations must be in `SPEC-RELATIONS`. |

## Mapping TRLC → ReqIF in This Project

| TRLC Construct | ReqIF Element | Notes |
|---|---|---|
| Section heading | `SPEC-OBJECT` (type: `section`) | No attributes, `LONG-NAME` = section title |
| Record object | `SPEC-OBJECT` (type: record type name) | Attributes per record fields |
| Record field (string/text) | `ATTRIBUTE-VALUE-XHTML` | Markdown → XHTML via `marko` |
| Record field (plain string) | `ATTRIBUTE-VALUE-STRING` | When no Markdown rendering needed |
| Record reference (`derived`) | `SPEC-RELATION` | Source = current record, Target = referenced record |
| File (multi-doc mode) | `SPECIFICATION` | One `.reqif` file per `.trlc` file |
| All files (single-doc mode) | Single `SPECIFICATION` | Top-level title from `--top-level` arg |

Identifier format used in this project: `spec-object-{counter}`, `hierarchy-{counter}`, etc. (sequential integers assigned in `_id_counter`).

## Python `reqif` Library Patterns

The project uses the `reqif` pip package. Key classes:

```python
from reqif.reqif_bundle import ReqIFBundle
from reqif.unparser import ReqIFUnparser
from reqif.models.reqif_core_content import ReqIFCoreContent
from reqif.models.reqif_data_type import ReqIFDataTypeDefinitionString, ReqIFDataTypeDefinitionXHTML
from reqif.models.reqif_namespace_info import ReqIFNamespaceInfo
from reqif.models.reqif_reqif_header import ReqIFReqIFHeader
from reqif.models.reqif_req_if_content import ReqIFReqIFContent
from reqif.models.reqif_spec_hierarchy import ReqIFSpecHierarchy
from reqif.models.reqif_spec_object import ReqIFSpecObject, SpecObjectAttribute
from reqif.models.reqif_spec_object_type import ReqIFSpecObjectType, SpecAttributeDefinition
from reqif.models.reqif_spec_relation import ReqIFSpecRelation
from reqif.models.reqif_spec_relation_type import ReqIFSpecRelationType
from reqif.models.reqif_specification import ReqIFSpecification
from reqif.models.reqif_specification_type import ReqIFSpecificationType
from reqif.models.reqif_types import SpecObjectAttributeType
```

Serialize a bundle to a `.reqif` file:

```python
output = ReqIFUnparser.unparse(bundle)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(output)
```

## Validation

Validate a generated `.reqif` file against the schema:

```powershell
# Using xmllint (if available)
xmllint --schema .venv/Lib/site-packages/reqif/reqif_schema/reqif.xsd output.reqif --noout
```

Run the project's ReqIF tests:

```powershell
pytest tests/test_reqif.py
```

Run the example to verify end-to-end output:

```powershell
cd examples/reqif
./generate_to_reqif.bat
```

Treat any schema validation error or pytest failure as a required fix.

## Completion Checklist

- `REQ-IF-VERSION` is set to `1.2` in `REQ-IF-HEADER`.
- All `IDENTIFIER` values are unique within the document.
- `LAST-CHANGE` and `CREATION-TIME` use ISO 8601 with timezone.
- Every `*-REF` element resolves to an existing `IDENTIFIER`.
- XHTML `THE-VALUE` is wrapped in `<div xmlns="http://www.w3.org/1999/xhtml">`.
- XHTML content is well-formed and uses only XHTML 1.0 Strict elements.
- File is UTF-8 encoded with `encoding="UTF-8"` in the XML declaration.
- Elements appear in the required document order: DATATYPES → SPEC-TYPES → SPEC-OBJECTS → SPEC-RELATIONS → SPECIFICATIONS.
- All pytest tests in `tests/test_reqif.py` pass.
- Python code changes also satisfy the `python-coding-standard` skill.
