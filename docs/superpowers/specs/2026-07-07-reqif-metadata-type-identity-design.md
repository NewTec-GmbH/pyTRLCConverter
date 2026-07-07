# ReqIF metadata store & type-system identity preservation

Date: 2026-07-07
Status: Approved (design)

## Motivation

An import → export ReqIF round-trip with pyTRLCConverter must let DOORS NG re-import
the exported file without flagging the taken-over elements as modified. Today the
converter preserves only the `SPEC-OBJECT` and `SPEC-HIERARCHY` identifiers. The
type system (`SPEC-OBJECT-TYPE`, `ATTRIBUTE-DEFINITION`,
`DATATYPE-DEFINITION-ENUMERATION`, `ENUM-VALUE`), the `SPECIFICATION` and the
`SPECIFICATION-TYPE` receive freshly generated identifiers, and the
`SPECIFICATION-TYPE` long-name is a hardcoded constant. As a result DOORS treats the
whole type system as new.

This change preserves those identifiers (and the `SPECIFICATION-TYPE` long-name)
across the round-trip.

## Rename: identifier store → ReqIF metadata

The persistent `--id-store` file is repurposed from a pure identifier map into a
general ReqIF metadata store. It is renamed accordingly:

| Before | After |
| --- | --- |
| CLI argument `--id-store` | `--meta-data` |
| Module `reqif_identifier_store.py` | `reqif_meta_data.py` |
| Class `ReqifIdentifierStore` | `ReqifMetaData` |
| Generated file `id_store.json` | `meta_data.json` |
| Prose "identifier store" | "ReqIF metadata store" |

The TRLC requirement/architecture/test object identifiers (e.g.
`sw_req_reqif_identifier_store_init`) and their `lobster-trace` targets are kept
unchanged to preserve traceability history; only their descriptive text is updated.
This is a breaking CLI change: `--id-store` is replaced, not aliased. In-repo
usages (examples, docs) are updated in the same change.

## Metadata file schema (version 2)

```json
{
  "version": 2,
  "next_id": 148,
  "identifiers": { "<logical key>": "<identifier>", ... },
  "metadata": {
    "specification-type-identifier": "_dd4baa34-...",
    "specification-type-long-name": "Document.ERP"
  }
}
```

`load()` tolerates a missing `metadata` object (version 1 files load unchanged).
`SCHEMA_VERSION` becomes 2. The `identifiers` and `next_id` fields keep their
meaning.

## Stable logical keys

Both the import (seeding) and the export (lookup) compute these keys from TRLC
names, so deterministic sanitization keeps them aligned:

- `spec-object-type:<TrlcType>`
- `attribute-definition:<TrlcType>.<TrlcField>` — the synthetic ForeignID attribute
  uses `attribute-definition:<TrlcType>.ReqIF.ForeignID`
- `enum-datatype:<TrlcEnum>`
- `enum-value:<TrlcEnum>.<TrlcLiteral>`
- `specification:<SpecLongName>` — already the export key; the import must now seed it

## Export changes (`reqif_converter.py`)

`ReqifMetaData` gains `resolve(key, default_identifier)`: returns the stored
identifier if the key exists (a seeded original UUID or a previously stored value),
otherwise stores and returns `default_identifier`.

The `SPEC-OBJECT-TYPE`, `ATTRIBUTE-DEFINITION`, `DATATYPE-DEFINITION-ENUMERATION` and
`ENUM-VALUE` identifier generation is routed through `resolve`, passing the current
readable slug (e.g. `spec-object-type-requirement`) as `default_identifier`. This
keeps greenfield exports (no metadata file, or unseeded keys) byte-for-byte
unchanged while reusing seeded originals on a round-trip.

`SPECIFICATION-TYPE` uses the metadata `specification-type-identifier` and
`specification-type-long-name` when present, else today's constant identifier and
`"TRLC Specification"`.

The `SPECIFICATION` identifier already resolves through the metadata store on the
existing `specification:<title>` key; no export change beyond the import seeding it.

## Import changes (`trlc_generator.py`)

The `ReqifReader` already exposes the source identifiers (types, attribute
definitions, enum datatypes and values keyed by identifier). During the initial
import the metadata store is additionally seeded with:

- each spec-object type → its original `SPEC-OBJECT-TYPE` identifier
- each attribute → its original `ATTRIBUTE-DEFINITION` identifier
- each enum datatype and value → their original identifiers
- the specification → its original `SPECIFICATION` identifier
- `metadata`: the original `SPECIFICATION-TYPE` identifier and long-name

The `SPECIFICATION` long-name already reaches the export as the first TRLC section
(`spec.long_name`); no change needed there.

## Scope / non-goals

- Enum-value keys already match (source uses 0-based consecutive keys, as the export
  emits); no key preservation needed.
- `SPEC-ATTRIBUTES` ordering is not preserved (DOORS matches by identifier).
- String vs XHTML datatype fidelity (Group C) is a separate change.
- The merge-import path is unaffected.
- Without `--meta-data`, behaviour is unchanged.

## Testing

- Round-trip test (extends the `test_tc_reqif_import_initial` pattern): export →
  import with `--meta-data` seeding → re-export, then assert that the
  `SPEC-OBJECT-TYPE`, `ATTRIBUTE-DEFINITION`, `DATATYPE-DEFINITION-ENUMERATION`,
  `ENUM-VALUE`, `SPECIFICATION` and `SPECIFICATION-TYPE` identifiers and the
  `SPECIFICATION-TYPE` long-name are identical across the round-trip.
- Existing tests updated for the `--meta-data` / `meta_data.json` rename.

## Traceability

- Requirement: `sw_req_reqif_import_type_identity` (derived from
  `sw_req_reqif_import`).
- Architecture: bullet on `sw_arch_component_reqif_importer` and
  `sw_arch_component_reqif_converter`; add the new requirement to their `satisfies`.
- Test case: `tc_reqif_import_type_identity`.
