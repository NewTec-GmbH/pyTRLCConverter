"""Converter to ReqIF format.

    Author: Andreas Merkle (andreas.merkle@newtec.de)
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
import html
import os
import re
import zipfile
from datetime import datetime, timezone
from typing import Any, Optional
from marko import Markdown
from reqif.object_lookup import ReqIFObjectLookup
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
from trlc.ast import Array_Aggregate, Implicit_Null, Record_Object, Record_Reference, String_Literal, Expression
from pyTRLCConverter.base_converter import BaseConverter
from pyTRLCConverter.ret import Ret
from pyTRLCConverter.trlc_helper import TrlcAstWalker
from pyTRLCConverter.logger import log_error, log_verbose
from pyTRLCConverter.version import __version__

# pylint: disable=too-many-lines

# Variables ********************************************************************

# Classes **********************************************************************


# pylint: disable-next=too-many-instance-attributes
class ReqifConverter(BaseConverter):
    """ReqifConverter provides functionality for converting to ReqIF format."""

    OUTPUT_FILE_NAME_DEFAULT = "output.reqif"
    TOP_LEVEL_DEFAULT = "Specification"

    DATATYPE_XHTML_IDENTIFIER = "datatype-xhtml"
    DATATYPE_STRING_IDENTIFIER = "datatype-string"
    SECTION_TYPE_KEY = "section"
    SPECIFICATION_TYPE_IDENTIFIER = "specification-type-trlc"
    XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"

    SYSTEM_ATTRIBUTE_PREFIX = "ReqIF."
    ATTRIBUTE_KEY_RECORD_FOREIGN_ID = "foreignID"

    def __init__(self, args: Any) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif
        """
        Initializes the converter.

        Args:
            args (Any): The parsed program arguments.
        """
        super().__init__(args)

        self._out_path = args.out
        self._markdown_renderer_md = Markdown()
        self._markdown_renderer_gfm = Markdown(extensions=["gfm"])

        self._spec_objects = []
        self._spec_relations = []
        self._root_hierarchies = []
        self._hierarchy_stack = []
        self._attribute_definitions_by_type = {}
        self._spec_object_type_info = {}
        self._spec_relation_type_info = {}
        self._pending_relations = []
        self._spec_object_identifier_by_record = {}
        self._id_counter = 0
        self._document_title = ReqifConverter.TOP_LEVEL_DEFAULT

    @staticmethod
    def get_subcommand() -> str:
        # lobster-trace: SwRequirements.sw_req_reqif
        """
        Return subcommand token for this converter.

        Returns:
            str: Parser subcommand token
        """
        return "reqif"

    @staticmethod
    def get_description() -> str:
        # lobster-trace: SwRequirements.sw_req_reqif
        """
        Return converter description.

        Returns:
            str: Converter description
        """
        return "Convert into ReqIF format."

    @classmethod
    def register(cls, args_parser: Any) -> None:
        # lobster-trace: SwRequirements.sw_req_reqif_multiple_doc_mode
        # lobster-trace: SwRequirements.sw_req_reqif_single_doc_mode
        # lobster-trace: SwRequirements.sw_req_reqif_top_level_default
        # lobster-trace: SwRequirements.sw_req_reqif_top_level_custom
        # lobster-trace: SwRequirements.sw_req_reqif_out_file_name_default
        # lobster-trace: SwRequirements.sw_req_reqif_out_file_name_custom
        """
        Register converter specific argument parser.

        Args:
            args_parser (Any): Argument parser
        """
        super().register(args_parser)

        assert BaseConverter._parser is not None

        BaseConverter._parser.add_argument(
            "-e",
            "--empty",
            type=str,
            default=BaseConverter.EMPTY_ATTRIBUTE_DEFAULT,
            required=False,
            help="Every attribute value which is empty will output the string "
                 f"(default = {BaseConverter.EMPTY_ATTRIBUTE_DEFAULT})."
        )

        BaseConverter._parser.add_argument(
            "-n",
            "--name",
            type=str,
            default=ReqifConverter.OUTPUT_FILE_NAME_DEFAULT,
            required=False,
            help="Name of the generated output file inside the output folder "
                 f"(default = {ReqifConverter.OUTPUT_FILE_NAME_DEFAULT}) in "
                 "case a single document is generated."
        )

        BaseConverter._parser.add_argument(
            "-sd",
            "--single-document",
            action="store_true",
            required=False,
            default=False,
            help="Generate a single document instead of multiple files. The default is to generate multiple files."
        )

        BaseConverter._parser.add_argument(
            "-tl",
            "--top-level",
            type=str,
            default=ReqifConverter.TOP_LEVEL_DEFAULT,
            required=False,
            help="Name of the top level heading, required in single document mode "
                 f"(default = {ReqifConverter.TOP_LEVEL_DEFAULT})."
        )

        BaseConverter._parser.add_argument(
            "--reqifz",
            action="store_true",
            required=False,
            default=False,
            help="Archive the ReqIF output as a ZIP file with the .reqifz extension. "
                 "The default is to write plain .reqif files."
        )

    def begin(self) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_single_doc_mode
        """
        Begin the conversion process.

        Returns:
            Ret: Status
        """
        result = BaseConverter.begin(self)

        if result == Ret.OK:
            self._empty_attribute_value = self._args.empty
            log_verbose(f"Empty attribute value: {self._empty_attribute_value}")

            if self._args.single_document is True:
                log_verbose("Single document mode.")
                self._reset_document_state(self._args.top_level)
            else:
                log_verbose("Multiple document mode.")

        return result

    def enter_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_multiple_doc_mode
        """Enter a file and reset document state in multiple document mode.

        Args:
            file_name (str): File name

        Returns:
            Ret: Status
        """
        if self._args.single_document is False:
            file_title = os.path.splitext(os.path.basename(file_name))[0]
            self._reset_document_state(file_title)

        return Ret.OK

    def leave_file(self, file_name: str) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_multiple_doc_mode
        """Leave a file and write the ReqIF document in multiple document mode.

        Args:
            file_name (str): File name

        Returns:
            Ret: Status
        """
        if self._args.single_document is False:
            out_file_name = self._file_name_trlc_to_reqif(file_name)
            return self._write_document(out_file_name)

        return Ret.OK

    def convert_section(self, section: str, level: int) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_section
        """Process the given section item by creating a section spec-object.

        Args:
            section (str): The section name
            level (int): The section indentation level

        Returns:
            Ret: Status
        """
        assert len(section) > 0

        spec_object = self._create_spec_object(
            item_name=section,
            type_key=ReqifConverter.SECTION_TYPE_KEY,
            type_long_name="Section",
            attribute_value_map={}
        )

        self._append_hierarchy(spec_object.identifier, level, section, is_container=True)

        return Ret.OK

    def convert_record_object_generic(self, record: Record_Object, level: int, translation: Optional[dict]) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_record
        """Convert a record object generically to a ReqIF spec-object.

        Args:
            record (Record_Object): The record object.
            level (int): The record level.
            translation (Optional[dict]): Translation dictionary for the record object.
                                          If None, no translation is applied.

        Returns:
            Ret: Status
        """
        trlc_ast_walker = self._get_trlc_ast_walker()
        attribute_value_map = {
            ReqifConverter.ATTRIBUTE_KEY_RECORD_FOREIGN_ID: {
                "long_name": f"{ReqifConverter.SYSTEM_ATTRIBUTE_PREFIX}ForeignID",
                "value": record.name,
                "attribute_type": SpecObjectAttributeType.STRING
            }
        }
        type_key = self._get_record_type_key(record)

        for name, value in record.field.items():
            if self._queue_spec_relations_from_expression(record, value, name) is True:
                continue

            walker_result = trlc_ast_walker.walk(value)

            attribute_value = ""
            if isinstance(walker_result, list):
                attribute_value = "\n".join([str(item) for item in walker_result])
            else:
                attribute_value = str(walker_result)

            if len(attribute_value) == 0:
                attribute_value = self._empty_attribute_value

            attribute_name = self._translate_attribute_name(translation, name)
            rendered_value = self._render(
                package_name=record.n_package.name,
                type_name=record.n_typ.name,
                attribute_name=name,
                attribute_value=attribute_value
            )

            attribute_value_map[f"field_{name}"] = {
                "long_name": attribute_name,
                "value": rendered_value,
                "attribute_type": SpecObjectAttributeType.XHTML
            }

        spec_object = self._create_spec_object(
            item_name=record.name,
            type_key=type_key,
            type_long_name=record.n_typ.name,
            attribute_value_map=attribute_value_map
        )
        self._spec_object_identifier_by_record[id(record)] = spec_object.identifier

        self._append_hierarchy(spec_object.identifier, level + 1, record.name, is_container=False)

        return Ret.OK

    def finish(self) -> Ret:
        # lobster-trace: SwRequirements.sw_req_reqif_single_doc_mode
        """Finish the conversion process and write the output in single document mode.

        Returns:
            Ret: Status
        """
        if self._args.single_document is True:
            return self._write_document(self._args.name)

        return Ret.OK

    def _write_document(self, file_name: str) -> Ret:
        """Build the ReqIF bundle and write it to the output file.

        When --reqifz is active the output is a ZIP archive with the .reqifz
        extension that contains the .reqif file.

        Args:
            file_name (str): Output file name (without path prefix).

        Returns:
            Ret: Status
        """
        reqif_file_name = os.path.splitext(os.path.basename(file_name))[0] + ".reqif"

        if self._args.reqifz:
            out_file_name = os.path.splitext(file_name)[0] + ".reqifz"
        else:
            out_file_name = file_name

        if 0 < len(self._out_path):
            out_file_name = os.path.join(self._out_path, out_file_name)

        try:
            bundle = self._build_reqif_bundle()
            reqif_xml = ReqIFUnparser.unparse(bundle)

            if self._args.reqifz:
                with zipfile.ZipFile(out_file_name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr(reqif_file_name, reqif_xml)
            else:
                with open(out_file_name, "w", encoding="utf-8") as fd:
                    fd.write(reqif_xml)

            return Ret.OK

        except (OSError, IOError, ValueError) as exc:
            log_error(f"Failed to write ReqIF output file {out_file_name}: {exc}")
            return Ret.ERROR

    def _build_reqif_bundle(self) -> ReqIFBundle:
        """Assemble a complete ReqIFBundle from the accumulated spec objects, hierarchies and attribute definitions.

        Returns:
            ReqIFBundle: The assembled ReqIF bundle ready for unparsing.
        """
        last_change = self._get_reqif_timestamp()

        data_type = ReqIFDataTypeDefinitionXHTML(
            identifier=ReqifConverter.DATATYPE_XHTML_IDENTIFIER,
            last_change=last_change,
            long_name="XHTML"
        )

        string_data_type = ReqIFDataTypeDefinitionString(
            identifier=ReqifConverter.DATATYPE_STRING_IDENTIFIER,
            last_change=last_change,
            long_name="String",
            max_length="255"
        )

        spec_object_type_list = [
            ReqIFSpecObjectType.create(
                identifier=type_info["identifier"],
                long_name=type_info["long_name"],
                last_change=last_change,
                attribute_definitions=list(self._attribute_definitions_by_type.get(type_key, {}).values())
            )
            for type_key, type_info in self._spec_object_type_info.items()
        ]

        spec_relation_type_list = [
            ReqIFSpecRelationType(
                identifier=relation_type_info["identifier"],
                last_change=last_change,
                long_name=relation_type_info["long_name"],
                is_self_closed=True,
                attribute_definitions=None
            )
            for relation_type_info in self._spec_relation_type_info.values()
        ]

        specification_type = ReqIFSpecificationType(
            identifier=ReqifConverter.SPECIFICATION_TYPE_IDENTIFIER,
            last_change=last_change,
            long_name="TRLC Specification",
            spec_attributes=[]
        )

        specification = ReqIFSpecification(
            identifier=self._new_identifier("specification"),
            long_name=self._document_title,
            last_change=last_change,
            specification_type=ReqifConverter.SPECIFICATION_TYPE_IDENTIFIER,
            values=[],
            children=self._root_hierarchies
        )

        req_if_header = ReqIFReqIFHeader(
            identifier=self._new_identifier("req-if-header"),
            comment="Generated by pyTRLCConverter",
            creation_time=last_change,
            repository_id="",
            req_if_tool_id=f"pyTRLCConverter {__version__}",
            req_if_version="1.0",
            source_tool_id=f"pyTRLCConverter {__version__}",
            title=self._document_title
        )

        namespace_info = ReqIFNamespaceInfo.create_default()
        namespace_info.schema_namespace = ReqifConverter.XSI_NAMESPACE
        namespace_info.schema_location = (
            f"{ReqIFNamespaceInfo.REQIF_XSD} {ReqIFNamespaceInfo.REQIF_XSD}"
        )

        content = ReqIFReqIFContent(
            data_types=[data_type, string_data_type],
            spec_types=[*spec_object_type_list, *spec_relation_type_list, specification_type],
            spec_objects=self._spec_objects,
            spec_relations=self._build_spec_relations(),
            specifications=[specification]
        )

        return ReqIFBundle(
            namespace_info=namespace_info,
            req_if_header=req_if_header,
            core_content=ReqIFCoreContent(req_if_content=content),
            tool_extensions_tag_exists=False,
            lookup=ReqIFObjectLookup.empty(),
            exceptions=[]
        )

    def _reset_document_state(self, title: str) -> None:
        """Reset all per-document state and pre-register the dedicated section type.

        Args:
            title (str): The document title used as the specification long-name.
        """
        self._spec_objects = []
        self._spec_relations = []
        self._root_hierarchies = []
        self._hierarchy_stack = []
        self._attribute_definitions_by_type = {}
        self._spec_object_type_info = {}
        self._spec_relation_type_info = {}
        self._pending_relations = []
        self._spec_object_identifier_by_record = {}
        self._id_counter = 0
        self._document_title = title

        self._ensure_spec_object_type(ReqifConverter.SECTION_TYPE_KEY, "Section")

    def _append_hierarchy(self, spec_object_identifier: str, level: int, long_name: str,
                          is_container: bool) -> None:
        """Append a new ReqIFSpecHierarchy node at the given nesting level.

        The internal hierarchy stack is pruned so the new node is correctly
        attached either as a child of the current parent or as a root entry.

        Args:
            spec_object_identifier (str): Identifier of the spec-object this hierarchy node references.
            level (int): TRLC nesting level (0 = top-level).
            long_name (str): Display name for the hierarchy node.
            is_container (bool): If True, keep the new hierarchy node on the stack as a parent.
        """
        hierarchy_level = max(1, level + 1)

        while len(self._hierarchy_stack) >= hierarchy_level:
            self._hierarchy_stack.pop()

        hierarchy = ReqIFSpecHierarchy(
            identifier=self._new_identifier("hierarchy"),
            spec_object=spec_object_identifier,
            level=hierarchy_level,
            children=[],
            long_name=long_name,
            ref_then_children_order=True,
            last_change=self._get_reqif_timestamp(),
            editable=False,
            is_table_internal=False,
            is_self_closed=False
        )

        if len(self._hierarchy_stack) > 0:
            self._hierarchy_stack[-1].add_child(hierarchy)
        else:
            self._root_hierarchies.append(hierarchy)

        if is_container is True:
            self._hierarchy_stack.append(hierarchy)

    def _create_spec_object(self,
                            item_name: str,
                            type_key: str,
                            type_long_name: str,
                            attribute_value_map: dict[str, dict[str, Any]]) -> ReqIFSpecObject:
        """Create a ReqIFSpecObject for the given ReqIF type and field attributes.

        Args:
            item_name (str): Name of the TRLC item used as the spec-object long-name.
            type_key (str): Internal key of the ReqIF spec-object type.
            type_long_name (str): Human-readable long-name of the ReqIF spec-object type.
            attribute_value_map (dict[str, dict[str, Any]]): Mapping from field key to
                ``{"long_name": ..., "value": ...}`` for each dynamic field attribute.

        Returns:
            ReqIFSpecObject: The created and registered spec-object.
        """
        self._ensure_spec_object_type(type_key, type_long_name)

        attributes = []

        for key in sorted(attribute_value_map):
            attribute_info = attribute_value_map[key]
            attribute_type = attribute_info.get("attribute_type", SpecObjectAttributeType.XHTML)

            if attribute_type == SpecObjectAttributeType.STRING:
                attributes.append(
                    self._create_string_attribute(
                        type_key,
                        key,
                        attribute_info["long_name"],
                        attribute_info["value"]
                    )
                )
            else:
                attributes.append(
                    self._create_xhtml_attribute(
                        type_key,
                        key,
                        attribute_info["long_name"],
                        attribute_info["value"]
                    )
                )

        spec_object = ReqIFSpecObject(
            identifier=self._new_identifier("spec-object"),
            attributes=attributes,
            spec_object_type=self._get_spec_object_type_identifier(type_key),
            long_name=item_name,
            last_change=self._get_reqif_timestamp()
        )

        self._spec_objects.append(spec_object)

        return spec_object

    def _create_xhtml_attribute(self, type_key: str, definition_key: str, long_name: str,
                                xhtml_value: str) -> SpecObjectAttribute:
        """Create a SpecObjectAttribute of type XHTML, ensuring the corresponding attribute definition exists.

        Args:
            type_key (str): Internal key of the owning ReqIF spec-object type.
            definition_key (str): Internal dictionary key used to look up or create the attribute definition.
            long_name (str): Human-readable attribute name registered in the spec-object type.
            xhtml_value (str): XHTML-wrapped content string.

        Returns:
            SpecObjectAttribute: The created attribute.
        """
        definition_identifier = self._ensure_attribute_definition(
            type_key,
            definition_key,
            long_name,
            SpecObjectAttributeType.XHTML
        )

        return SpecObjectAttribute(
            attribute_type=SpecObjectAttributeType.XHTML,
            definition_ref=definition_identifier,
            value=xhtml_value
        )

    def _create_string_attribute(self, type_key: str, definition_key: str, long_name: str,
                                 value: str) -> SpecObjectAttribute:
        """Create a SpecObjectAttribute of type STRING for the given ReqIF spec-object type.

        Args:
            type_key (str): Internal key of the owning ReqIF spec-object type.
            definition_key (str): Internal dictionary key used to look up or create the attribute definition.
            long_name (str): Human-readable attribute name registered in the spec-object type.
            value (str): String attribute value.

        Returns:
            SpecObjectAttribute: The created attribute.
        """
        definition_identifier = self._ensure_attribute_definition(
            type_key,
            definition_key,
            long_name,
            SpecObjectAttributeType.STRING
        )

        return SpecObjectAttribute(
            attribute_type=SpecObjectAttributeType.STRING,
            definition_ref=definition_identifier,
            value=value
        )

    def _ensure_spec_object_type(self, type_key: str, long_name: str) -> str:
        """Return the identifier of an existing ReqIF spec-object type, or create and register a new one.

        Args:
            type_key (str): Internal dictionary key for the spec-object type.
            long_name (str): Human-readable name to assign when creating a new type.

        Returns:
            str: The spec-object type identifier.
        """
        if type_key in self._spec_object_type_info:
            return self._spec_object_type_info[type_key]["identifier"]

        sanitized_name = self._sanitize_identifier_token(type_key)
        type_identifier = f"spec-object-type-{sanitized_name}"

        self._spec_object_type_info[type_key] = {
            "identifier": type_identifier,
            "long_name": long_name
        }
        self._attribute_definitions_by_type[type_key] = {}

        return type_identifier

    def _get_spec_object_type_identifier(self, type_key: str) -> str:
        """Return the identifier of the requested ReqIF spec-object type.

        Args:
            type_key (str): Internal dictionary key for the spec-object type.

        Returns:
            str: The spec-object type identifier.
        """
        type_info = self._spec_object_type_info.get(type_key)
        assert type_info is not None
        return type_info["identifier"]

    def _ensure_attribute_definition(self, type_key: str, definition_key: str, long_name: str,
                                     attribute_type: SpecObjectAttributeType) -> str:
        """Return the identifier of an existing attribute definition, or create and register a new one.

        Args:
            type_key (str): Internal key of the owning ReqIF spec-object type.
            definition_key (str): Internal dictionary key for the attribute definition.
            long_name (str): Human-readable name to assign when creating a new definition.
            attribute_type (SpecObjectAttributeType): ReqIF attribute type.

        Returns:
            str: The attribute definition identifier.
        """
        attribute_definitions = self._attribute_definitions_by_type.setdefault(type_key, {})

        if definition_key in attribute_definitions:
            definition = attribute_definitions[definition_key]
            assert isinstance(definition, SpecAttributeDefinition)
            return definition.identifier

        type_identifier = self._ensure_spec_object_type(type_key, type_key)
        sanitized_name = self._sanitize_identifier_token(definition_key)
        definition_identifier = f"attribute-{type_identifier}-{sanitized_name}"

        definition = SpecAttributeDefinition(
            attribute_type=attribute_type,
            identifier=definition_identifier,
            datatype_definition=self._get_datatype_identifier(attribute_type),
            long_name=long_name,
            last_change=self._get_reqif_timestamp(),
            multi_valued=None
        )

        attribute_definitions[definition_key] = definition

        return definition_identifier

    def _get_record_type_key(self, record: Record_Object) -> str:
        """Return the ReqIF type key for the given TRLC record.

        Args:
            record (Record_Object): The record object.

        Returns:
            str: ReqIF type key derived from the TRLC record type.
        """
        return record.n_typ.name

    def _queue_spec_relation(self, source_record: Record_Object, record_reference: Record_Reference,
                             relation_name: str) -> None:
        """Queue a ReqIF spec relation derived from a TRLC record reference.

        Args:
            source_record (Record_Object): Source record containing the reference.
            record_reference (Record_Reference): Referenced target record.
            relation_name (str): TRLC field name that defines the relation type.
        """
        assert record_reference.target is not None

        self._ensure_spec_relation_type(relation_name, relation_name)
        self._pending_relations.append(
            {
                "source_record": id(source_record),
                "target_record": id(record_reference.target),
                "relation_type_key": relation_name,
                "long_name": relation_name
            }
        )

    def _queue_spec_relations_from_expression(self, source_record: Record_Object, expression: Expression,
                                              relation_name: str) -> bool:
        """Queue ReqIF spec relations from a TRLC expression if it consists of record references.

        Args:
            source_record (Record_Object): Source record containing the reference expression.
            expression (Expression): TRLC field expression to inspect.
            relation_name (str): TRLC field name that defines the relation type.

        Returns:
            bool: True if the expression was handled as one or more record references.
        """
        if isinstance(expression, Record_Reference):
            self._queue_spec_relation(source_record, expression, relation_name)
            return True

        if isinstance(expression, Array_Aggregate):
            has_record_references = False

            for item in expression.value:
                item_is_relation = self._queue_spec_relations_from_expression(
                    source_record,
                    item,
                    relation_name
                )
                has_record_references = has_record_references or item_is_relation

            return has_record_references

        return False

    def _ensure_spec_relation_type(self, relation_type_key: str, long_name: str) -> str:
        """Return the identifier of an existing ReqIF spec-relation type, or create and register a new one.

        Args:
            relation_type_key (str): Internal dictionary key for the spec-relation type.
            long_name (str): Human-readable relation type name.

        Returns:
            str: The spec-relation type identifier.
        """
        if relation_type_key in self._spec_relation_type_info:
            return self._spec_relation_type_info[relation_type_key]["identifier"]

        relation_type_identifier = f"spec-relation-type-{self._sanitize_identifier_token(relation_type_key)}"
        self._spec_relation_type_info[relation_type_key] = {
            "identifier": relation_type_identifier,
            "long_name": long_name
        }

        return relation_type_identifier

    def _build_spec_relations(self) -> list[ReqIFSpecRelation]:
        """Build ReqIF spec relations from queued TRLC record references.

        Returns:
            list[ReqIFSpecRelation]: Resolved ReqIF spec relations.
        """
        self._spec_relations = []

        for pending_relation in self._pending_relations:
            source_identifier = self._spec_object_identifier_by_record.get(pending_relation["source_record"])
            target_identifier = self._spec_object_identifier_by_record.get(pending_relation["target_record"])

            if source_identifier is None or target_identifier is None:
                log_error(
                    "Failed to create ReqIF relation because the source or target record is not part of the output.",
                    False
                )
                continue

            relation_type_identifier = self._ensure_spec_relation_type(
                pending_relation["relation_type_key"],
                pending_relation["long_name"]
            )

            self._spec_relations.append(
                ReqIFSpecRelation(
                    identifier=self._new_identifier("spec-relation"),
                    relation_type_ref=relation_type_identifier,
                    source=source_identifier,
                    target=target_identifier,
                    last_change=self._get_reqif_timestamp(),
                    long_name=pending_relation["long_name"]
                )
            )

        return self._spec_relations

    @staticmethod
    def _get_datatype_identifier(attribute_type: SpecObjectAttributeType) -> str:
        """Return the datatype definition identifier for the given ReqIF attribute type.

        Args:
            attribute_type (SpecObjectAttributeType): ReqIF attribute type.

        Returns:
            str: Matching datatype definition identifier.
        """
        if attribute_type == SpecObjectAttributeType.STRING:
            return ReqifConverter.DATATYPE_STRING_IDENTIFIER

        if attribute_type == SpecObjectAttributeType.XHTML:
            return ReqifConverter.DATATYPE_XHTML_IDENTIFIER

        raise NotImplementedError(attribute_type)

    @staticmethod
    def _sanitize_identifier_token(value: str) -> str:
        """Sanitize an identifier token for stable ReqIF identifiers.

        Args:
            value (str): Raw identifier token.

        Returns:
            str: Sanitized lowercase token.
        """
        sanitized_value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
        return sanitized_value if len(sanitized_value) > 0 else "item"

    def _file_name_trlc_to_reqif(self, file_name_trlc: str) -> str:
        """Convert a TRLC file name to a ReqIF file name.

        Args:
            file_name_trlc (str): TRLC file name

        Returns:
            str: ReqIF file name
        """
        file_name = os.path.basename(file_name_trlc)
        file_name = os.path.splitext(file_name)[0] + ".reqif"

        return file_name

    def _on_implict_null(self, _: Implicit_Null) -> str:
        """
        Process the given implicit null value.

        Returns:
            str: The configured empty attribute value.
        """
        return self._empty_attribute_value

    def _on_record_reference(self, record_reference: Record_Reference) -> str:
        """
        Process the given record reference value.

        Args:
            record_reference (Record_Reference): The record reference value.

        Returns:
            str: String representation of the referenced record.
        """
        return str(record_reference.to_python_object())

    def _on_string_literal(self, string_literal: String_Literal) -> str:
        """
        Process the given string literal value.

        Args:
            string_literal (String_Literal): The string literal value.

        Returns:
            str: The string literal value.
        """
        return string_literal.to_string()

    def _other_dispatcher(self, expression: Expression) -> str:
        """
        Dispatcher for all other expressions.

        Args:
            expression (Expression): The expression to process.

        Returns:
            str: The processed expression.
        """
        return expression.to_string()

    def _get_trlc_ast_walker(self) -> TrlcAstWalker:
        """
        Create and configure a TrlcAstWalker for traversing TRLC record field values.

        Returns:
            TrlcAstWalker: The configured TRLC AST walker.
        """
        trlc_ast_walker = TrlcAstWalker()
        trlc_ast_walker.add_dispatcher(
            Implicit_Null,
            None,
            self._on_implict_null,
            None
        )
        trlc_ast_walker.add_dispatcher(
            Record_Reference,
            None,
            self._on_record_reference,
            None
        )
        trlc_ast_walker.add_dispatcher(
            String_Literal,
            None,
            self._on_string_literal,
            None
        )
        trlc_ast_walker.set_other_dispatcher(self._other_dispatcher)

        return trlc_ast_walker

    def _render(self, package_name: str, type_name: str, attribute_name: str, attribute_value: str) -> str:
        # lobster-trace: SwRequirements.sw_req_reqif_render_md
        # lobster-trace: SwRequirements.sw_req_reqif_render_gfm
        """Render an attribute value to an XHTML-wrapped string based on the render configuration.

        If the attribute is configured as CommonMark Markdown, it is converted via marko.
        If configured as GFM, it is converted with the GFM extension.
        Otherwise plain text is HTML-escaped and wrapped.

        Args:
            package_name (str): TRLC package name of the record.
            type_name (str): TRLC type name of the record.
            attribute_name (str): Attribute field name.
            attribute_value (str): Raw attribute value string.

        Returns:
            str: XHTML-wrapped content string.
        """
        if self._render_cfg.is_format_md(package_name, type_name, attribute_name) is True:
            return self._markdown_to_xhtml(attribute_value, gfm_mode=False)

        if self._render_cfg.is_format_gfm(package_name, type_name, attribute_name) is True:
            return self._markdown_to_xhtml(attribute_value, gfm_mode=True)

        return self._plain_text_to_xhtml(attribute_value)

    def _plain_text_to_xhtml(self, plain_text: str) -> str:
        """Convert plain text to an XHTML-wrapped string.

        Blank-line-separated paragraphs are wrapped in ``<p>`` tags; single
        newlines within a paragraph become ``<br/>`` elements.

        Args:
            plain_text (str): Plain text to convert.

        Returns:
            str: XHTML-wrapped content string.
        """
        escaped = html.escape(plain_text)

        paragraph_list = []

        for paragraph in escaped.split("\n\n"):
            paragraph_linebreaks = paragraph.replace("\n", "<br/>")
            paragraph_list.append(f"<p>{paragraph_linebreaks}</p>")

        return self._wrap_xhtml("".join(paragraph_list))

    def _markdown_to_xhtml(self, markdown_text: str, gfm_mode: bool) -> str:
        """Convert Markdown text to an XHTML-wrapped string using marko.

        Args:
            markdown_text (str): Markdown source text.
            gfm_mode (bool): If True, use the GFM extension; otherwise use CommonMark.

        Returns:
            str: XHTML-wrapped HTML string.
        """
        renderer = self._markdown_renderer_gfm if gfm_mode else self._markdown_renderer_md
        html_text = renderer.convert(markdown_text).strip()

        if len(html_text) == 0:
            html_text = "<p></p>"

        return self._wrap_xhtml(html_text)

    @staticmethod
    def _wrap_xhtml(fragment: str) -> str:
        """Wrap an HTML fragment in a ReqIF-compatible XHTML div element.

        Args:
            fragment (str): Inner HTML fragment.

        Returns:
            str: XHTML-wrapped string.
        """
        return "<div xmlns=\"http://www.w3.org/1999/xhtml\">" + fragment + "</div>"

    @staticmethod
    def _get_reqif_timestamp() -> str:
        """Return the current UTC time as a ReqIF-compatible ISO 8601 timestamp.

        Returns:
            str: ISO 8601 timestamp string (UTC, no microseconds).
        """
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _new_identifier(self, prefix: str) -> str:
        """Generate a unique identifier by combining the given prefix with an auto-incrementing counter.

        Args:
            prefix (str): Identifier prefix (e.g. ``"spec-object"`` or ``"hierarchy"``)

        Returns:
            str: Unique identifier string.
        """
        self._id_counter += 1
        return f"{prefix}-{self._id_counter}"
