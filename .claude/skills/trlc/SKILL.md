---
name: trlc
description: "Reference for the TRLC (Treat Requirements Like Code) language when reading, writing, or processing .rsl/.trlc files. Use when: authoring or modifying type definitions (.rsl), writing requirement instances (.trlc), understanding TRLC syntax, adding checks, or mapping TRLC constructs to converter output."
argument-hint: "Optional: specific language feature or file to focus on (e.g. enums, checks, arrays, trlc/swe-req.trlc)"
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# TRLC Language Reference (pyTRLCConverter)

This skill summarises the TRLC Language Reference Manual (LRM) as used in this project.
Full specification: https://bmw-software-engineering.github.io/trlc/lrm.html

---

## File Types

| Extension | Purpose |
| --- | --- |
| `.rsl` | Type definitions: `type`, `enum`, `tuple`, `checks` |
| `.trlc` | Requirement instances: record objects inside optional `section` blocks |

All files in a processing run are loaded together. RSL files are evaluated before TRLC files.
Every file begins with a `package` declaration; imports are optional.

---

## Package and Import

```trlc
package MyPackage
import OtherPackage
import ThirdPackage
```

- **One package declaration per file** — must be the first statement.
- **Imports** make all names from the named package available as `OtherPackage.Name`.
- Without a qualifier, a name must exist in the current package's scope.

---

## Lexical Conventions

### Identifiers
Pattern: `[a-zA-Z][a-zA-Z0-9_]*`

Record object names must be **globally unique** after normalisation (lowercase, underscores stripped).

### Comments
```trlc
// Single-line comment
/* Multi-line comment (non-greedy) */
```

### Keywords
`abs` `abstract` `and` `checks` `else` `elsif` `enum` `error` `exists` `extends`
`false` `fatal` `final` `forall` `freeze` `if` `implies` `import` `in` `not`
`null` `optional` `or` `package` `section` `separator` `then` `true` `tuple`
`type` `warning` `xor`

### Numeric Literals
- Integers: decimal, `0b` binary, `0x` hex; underscores allowed as separators (`1_000`)
- Decimals: `NUMBER.NUMBER` format

### String Literals
| Form | Escaping |
| --- | --- |
| `"text"` | `\"` to embed a double-quote |
| `'''multi-line'''` | No escaping needed |
| `"""multi-line"""` | No escaping needed |

### Markup Strings
A `Markup_String` component accepts inline record references:

```trlc
text = "See [[req_foo, req_bar]] for details."
```

- Only references record objects (not types).
- Forward references are allowed.
- Cross-package names must be qualified: `[[OtherPkg.req_foo]]`.

---

## Built-in Types

| Type | Description |
| --- | --- |
| `Boolean` | `true` or `false` |
| `Integer` | Signed integer |
| `Decimal` | Rational number with power-of-ten denominator |
| `String` | Sequence of characters |
| `Markup_String` | String that may contain `[[record_ref]]` inline links |

`null` is the default value for any `optional` component. `null == null` evaluates to `true`.

---

## RSL: Type Definitions

### Record Types

```trlc
// Basic record
type Requirement "A software requirement" {
    description  String
    priority     Integer
    note         optional String
}

// Abstract record — cannot be instantiated, must be extended
abstract type BaseReq {
    description  String
    status       STATUS
}

// Final record — cannot be extended
final type Constraint extends BaseReq {
    rationale  String
}

// Extension — inherits all components, checks, and freezes from parent
type SwReq extends BaseReq {
    verification_criteria  String
    freeze status = STATUS.valid
}
```

**Rules:**
- `abstract` and `final` are mutually exclusive.
- `extends` references a qualified type name (`Package.TypeName` or `TypeName` in scope).
- Frozen components cannot be overridden by instances; they receive a fixed value.
- Checks defined on a parent type evaluate **before** checks on a child type.

### Enumeration Types

```trlc
enum PRIORITY "Priority levels" {
    low     "Low priority"
    medium
    high    "High priority"
}
```

- Must have **at least one** literal.
- Literals are referenced as `PRIORITY.low` in TRLC files and check expressions.
- Description strings on literals are optional.

### Tuple Types

```trlc
// Without separator — all fields required
tuple Point {
    x  Integer
    y  Integer
}

// With separator — separator appears between fields; trailing fields may be optional
tuple Range {
    lower  Integer
    separator ..
    upper  optional Integer
}
```

**Rules:**
- Valid separators: any identifier, `@`, `:`, `;`.
- Once a separator is declared, it appears between **every** adjacent pair of fields in instances.
- Once one field is `optional`, all following fields must also be `optional`.
- Tuples with separators cannot contain nested tuples that also use separators.

### Arrays

Declare an array component using bracket notation on the type:

```trlc
derived  optional  Requirement  [0 .. *]   // zero or more, unbounded upper
tags               String        [1 .. 5]   // one to five elements
```

- `[lower .. upper]` or `[lower .. *]` (unbounded).
- Array components are always initialised as a list in TRLC instances using `[v1, v2, ...]`.

### Record References

A component whose type is a record type name holds a reference to another record object:

```trlc
type SwReq extends BaseReq {
    derived  optional  BaseReq  [0 .. *]   // array of references
    parent   optional  BaseReq             // single reference
}
```

Cross-file references require `--single-document` mode in the converter.

---

## RSL: Checks

```trlc
checks Requirement {
    description != "",
    error "Description must not be empty",
    "Provide a non-empty description string.",
    description
}

checks Requirement {
    len(description) >= 10,
    warning "Description is very short"
}
```

**Structure of one check entry:**

```
expression ,
[warning | error | fatal]  "message" ,
["detail string"] ,
[component_name]
```

- **`error`** is the default severity (may be omitted).
- **`warning`** — diagnostic emitted, evaluation continues.
- **`fatal`** — evaluation stops after this check.
- The optional trailing component name anchors the message to a specific field in IDEs.
- Multiple check entries are separated by commas inside the `checks { }` block.
- Checks on parent types evaluate before checks on child types.

---

## Expressions in Checks

### Operators (highest to lowest precedence)

| Precedence | Operators |
| --- | --- |
| Highest | `**` (exponentiation), `abs`, `not` |
| Multiplying | `*` `/` `%` |
| Adding | `+` `-` |
| Relational | `==` `!=` `<` `<=` `>` `>=` `in` `not in` |
| Logical | `and` `or` `xor` `implies` |

**Notes:**
- `and`, `or`, `implies` use **short-circuit** evaluation.
- `/` on integers is **floor division**: `5/2 = 2`, `-5/2 = -3`.
- `%` satisfies `x = y*N + (x % y)`; remainder has the same sign as the divisor.
- `x in a..b` is equivalent to `x >= a and x <= b`.
- `"sub" in someString` tests substring membership.
- `element in someArray` tests array membership.

### Built-in Functions

| Function | Signature | Returns |
| --- | --- | --- |
| `len` | `len(String\|Array)` | `Integer` |
| `startswith` | `startswith(String, String)` | `Boolean` |
| `endswith` | `endswith(String, String)` | `Boolean` |
| `matches` | `matches(String, regex_String)` | `Boolean` |
| `oneof` | `oneof(Boolean, ...)` | `Boolean` — true if **exactly one** argument is true |
| `Integer` | `Integer(value)` | Type conversion to `Integer` |
| `Decimal` | `Decimal(value)` | Type conversion to `Decimal` |

### Quantifiers (Arrays)

```trlc
(forall x in tags     => len(x) > 0)   // vacuously true for empty array
(exists x in derived  => x != null)    // vacuously false for empty array
```

- Variable `x` is scoped to the predicate; it cannot shadow a component name.

### Conditional Expressions

```trlc
if priority == PRIORITY.high then
    len(description) >= 50
elsif priority == PRIORITY.medium then
    len(description) >= 20
else
    true
```

All branches must produce the same type.

---

## TRLC: Requirement Instances

### Record Object

```trlc
package SwRequirements
import AbstractRequirements

SwReq sw_req_cli {
    description          = "The software shall be a CLI application."
    verification_criteria = "All features accessible via command line."
    valid_status         = AbstractRequirements.VALID_STATUS.valid
}
```

- The type name comes first, then the object name, then `{ ... }`.
- Every non-optional, non-frozen component must be assigned.
- Values must match the declared type (string → `"..."`, enum → `Package.ENUM.literal`, etc.).

### Sections

```trlc
section "Functional Requirements" {

    section "General" {

        SwReq sw_req_foo {
            description = "..."
        }
    }

    SwReq sw_req_bar {
        description = "..."
    }
}
```

- Sections are purely organisational; they do not create objects.
- Sections can be arbitrarily nested.
- A section heading becomes a `SPEC-OBJECT` of type `section` in ReqIF output.

### Array Values

```trlc
SwReq sw_req_complex {
    description = "..."
    derived     = [sw_req_foo, SwRequirements.sw_req_bar]
    tags        = ["safety", "functional"]
}
```

### Optional Components

Omit an optional component entirely to leave it `null`:

```trlc
SwReq sw_req_simple {
    description  = "..."
    valid_status = AbstractRequirements.VALID_STATUS.valid
    // note is optional — omit to leave it null
}
```

### Tuple Values

Without separator:
```trlc
position = (10, 20)
```

With separator (e.g. `separator ..`):
```trlc
range = 1 .. 10
```

---

## Project-Specific Patterns

In this repository the TRLC model lives in [trlc/model/](trlc/model/):

| File | Package | Content |
| --- | --- | --- |
| [abs-req.rsl](trlc/model/abs-req.rsl) | `AbstractRequirements` | Abstract base type, `VALID_STATUS` enum |
| [swe-req.rsl](trlc/model/swe-req.rsl) | `SwRequirements` | `SwReq`, `SwReqNonFunc`, `SwConstraint` extending `AbstractRequirements.Requirement` |
| [swe-arch.rsl](trlc/model/swe-arch.rsl) | `SwArchitecture` | Architecture-level types |
| [swe-test.rsl](trlc/model/swe-test.rsl) | `SwTests` | Test case types |
| [generic.rsl](trlc/model/generic.rsl) | `Generic` | Shared utility types (`Info`, `PlantUML`, etc.) |

Requirement instances live in [trlc/swe-req/](trlc/swe-req/), [trlc/swe-arch/](trlc/swe-arch/), [trlc/swe-test/](trlc/swe-test/).

Traceability comments in Python code use:
```python
# lobster-trace: SwRequirements.<object_name>
```

---

## TRLC → Converter Mapping

| TRLC Construct | Python API (`trlc_helper`) | Notes |
| --- | --- | --- |
| `section "..."` | `trlc.ast.Section` | Nested sections supported |
| Record object | `trlc.ast.Record_Object` | `.name`, `.field` dict |
| String field | `trlc.ast.String_Literal` | `.value` |
| Integer field | `trlc.ast.Integer_Literal` | `.value` |
| Boolean field | `trlc.ast.Boolean_Literal` | `.value` |
| Enum field | `trlc.ast.Enum_Literal` | `.value` (the literal name string) |
| Array field | Python `list` | Elements are the above literal types |
| Record reference | `trlc.ast.Record_Reference` | `.target` → the referenced `Record_Object` |
| `null` / omitted optional | `None` | Check `if value is None` |

The converter lifecycle (`begin → enter_file → convert_section/convert_record_object → leave_file → finish`) is driven by `ItemWalker` in [src/pyTRLCConverter/item_walker.py](src/pyTRLCConverter/item_walker.py).

---

## Quick Reference — Common Patterns

```trlc
// Enum with description
enum STATUS {
    draft     "Not yet reviewed"
    approved
    rejected
}

// Abstract base with optional array reference
abstract type Req {
    description  String
    status       STATUS
    note         optional  String
    derived      optional  Req  [0 .. *]
}

// Concrete extension with freeze
type SwReq extends Req {
    verification  String
    freeze status = STATUS.draft
}

// Check: non-empty string
checks Req {
    description != "",
    error "description must not be empty",
    description
}

// Check: conditional length
checks SwReq {
    len(verification) >= 10,
    warning "verification criteria seems too short"
}

// Instance
SwReq sw_req_001 {
    description  = "The system shall do X."
    verification = "Verified by test TC-001."
    derived      = [sw_req_000]
}
```

---

## Completion Checklist

When authoring or modifying TRLC files:

- Every `.rsl` and `.trlc` file starts with a `package` declaration.
- Enum types have at least one literal.
- Abstract types are not instantiated directly.
- Final types are not extended.
- All non-optional, non-frozen components are assigned in every record instance.
- Record object names are unique across the entire project (globally unique after normalisation).
- Cross-package names use the `Package.Name` qualified form.
- Array components are initialised with `[...]` syntax (even for a single element: `[item]`).
- Checks use the correct severity (`warning` / `error` / `fatal`).
- After edits, run `pyTRLCConverter` to confirm the TRLC files parse without errors.
