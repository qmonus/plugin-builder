from __future__ import annotations
import typing
import logging
import pathlib
import json

from .. import exceptions
from ..libs import yaml_utils, file_utils, data_lib
from ..class_libs import component as comp
from . import parser

logger = logging.getLogger(__name__)


def convert_type(type: comp.BaseType) -> str:
    if isinstance(type, comp.CLASS):
        result = f'<AxisAtom.{type.cls.__name__}>'
    elif isinstance(type, comp.STRING):
        result = 'string'
    elif isinstance(type, comp.INTEGER):
        result = 'integer'
    elif isinstance(type, comp.NUMBER):
        result = 'number'
    elif isinstance(type, comp.BOOLEAN):
        result = 'boolean'
    elif isinstance(type, comp.OBJECT):
        result = 'object'
    elif isinstance(type, comp.DATETIME):
        result = 'DateTime'
    elif isinstance(type, comp.MU):
        result = 'MU'
    elif isinstance(type, comp.ARRAY_OF_CLASS):
        result = f'array<AxisAtom.{type.cls.__name__}>'
    elif isinstance(type, comp.ARRAY_OF_MU):
        result = 'array<MU>'
    elif isinstance(type, comp.ARRAY):
        result = 'array'
    else:
        raise ValueError(f"Invalid type: '{str(type.__class__.__name__)}")
    return result


class ClassYAML(object):
    def __init__(
        self,
        category: typing.Optional[str],
        name: str,
        persistence: bool,
        abstract: bool,
        extends: typing.Optional[typing.List[str]],
        api_generation: bool,
        api_auto_response: typing.Optional[bool],
        scope: typing.Optional[str],
        version: int,
        created_at: typing.Optional[str],
        update: typing.Optional[str],
    ) -> None:
        self.category = category
        self.name = name
        self.persistence = persistence
        self.abstract = abstract

        if extends is not None:
            self.extends = extends

        self.api_generation = api_generation

        if api_auto_response is not None:
            self.api_auto_response = api_auto_response

        if scope is not None:
            self.scope = scope

        self.version = version

        if created_at is not None:
            self.created_at = created_at

        if update is not None:
            self.update = update

        self.attributes: typing.Any = {}
        self.methods: typing.Any = {}

    def set_identifier(
        self,
        field_name: str,
        field_type: str,
        field_persistence: bool,
        field_immutable: bool,
        field_default: typing.Optional[str],
        field_metadata: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        field_dbtype: typing.Optional[str],
        field_length: typing.Optional[int],
    ) -> None:
        self.attributes['identifier'] = IdentifierYAML(
            field_name=field_name,
            field_type=field_type,
            field_persistence=field_persistence,
            field_immutable=field_immutable,
            field_default=field_default,
            field_metadata=field_metadata,
            field_dbtype=field_dbtype,
            field_length=field_length,
        )

    def add_local_field(
        self,
        field_name: str,
        field_type: str,
        field_persistence: bool,
        field_nullable: bool,
        field_immutable: bool,
        field_unique: bool,
        field_default: typing.Optional[str],
        field_enum: typing.Optional[typing.List[str]],
        field_format: typing.Optional[str],
        field_metadata: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        field_alias: typing.Optional[str],
        field_fsm: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        field_dbtype: typing.Optional[str],
        field_length: typing.Optional[int],
    ) -> None:
        local_field = LocalFieldYAML(
            field_name=field_name,
            field_type=field_type,
            field_persistence=field_persistence,
            field_nullable=field_nullable,
            field_immutable=field_immutable,
            field_unique=field_unique,
            field_default=field_default,
            field_enum=field_enum,
            field_format=field_format,
            field_metadata=field_metadata,
            field_alias=field_alias,
            field_fsm=field_fsm,
            field_dbtype=field_dbtype,
            field_length=field_length,
        )
        if 'local_fields' not in self.attributes:
            self.attributes['local_fields'] = []
        self.attributes['local_fields'].append(local_field)

    def add_ref_field(
        self,
        field_name: str,
        field_type: str,
        field_persistence: bool,
        field_unique: bool,
        ref_class: str,
        ref_class_field: str,
        field_metadata: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        field_dbtype: typing.Optional[str],
        field_length: typing.Optional[int],
    ) -> None:
        ref_field = RefFieldYAML(
            field_name=field_name,
            field_type=field_type,
            field_persistence=field_persistence,
            field_unique=field_unique,
            ref_class=ref_class,
            ref_class_field=ref_class_field,
            field_metadata=field_metadata,
            field_dbtype=field_dbtype,
            field_length=field_length,
        )
        if 'ref_fields' not in self.attributes:
            self.attributes['ref_fields'] = []
        self.attributes['ref_fields'].append(ref_field)

    def add_class_method(self, method_body: str) -> None:
        class_method = ClassMethodYAML(method_body=method_body)
        if 'class_methods' not in self.methods:
            self.methods['class_methods'] = []
        self.methods['class_methods'].append(class_method)

    def add_instance_method(
        self,
        method_body: str,
        propagation_mode: bool,
        topdown: bool,
        auto_rollback: bool,
        multiplexable_number: int,
        field_order: str,
        timeout: typing.Optional[int],
    ) -> None:
        instance_method = InstanceMethodYAML(
            method_body=method_body,
            propagation_mode=propagation_mode,
            topdown=topdown,
            auto_rollback=auto_rollback,
            multiplexable_number=multiplexable_number,
            field_order=field_order,
            timeout=timeout,
        )
        if 'instance_methods' not in self.methods:
            self.methods['instance_methods'] = []
        self.methods['instance_methods'].append(instance_method)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        _dict: typing.Dict[str, typing.Any] = data_lib.to_primitive(self)
        return _dict

    def dump(self) -> str:
        return yaml_utils.dump(self.to_dict())


class IdentifierYAML(object):
    def __init__(
        self,
        field_name: str,
        field_type: str,
        field_persistence: bool,
        field_immutable: bool,
        field_default: typing.Optional[str],
        field_metadata: typing.Optional[typing.Dict[typing.Any, typing.Any]], 
        field_dbtype: typing.Optional[str],
        field_length: typing.Optional[int],
    ) -> None:
        self.field_name = field_name
        self.field_type = field_type
        self.field_persistence = field_persistence
        self.field_immutable = field_immutable

        if field_default is not None:
            self.field_default = field_default

        if field_metadata is not None:
            self.field_metadata = field_metadata

        if field_dbtype is not None:
            self.field_dbtype = field_dbtype

        if field_length is not None:
            self.field_length = field_length


class LocalFieldYAML(object):
    def __init__(
        self,
        field_name: str,
        field_type: str,
        field_persistence: bool,
        field_nullable: bool,
        field_immutable: bool,
        field_unique: bool,
        field_default: typing.Optional[str],
        field_enum: typing.Optional[typing.List[str]],
        field_format: typing.Optional[str],
        field_metadata: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        field_alias: typing.Optional[str],
        field_fsm: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        field_dbtype: typing.Optional[str],
        field_length: typing.Optional[int],
    ) -> None:
        self.field_name = field_name
        self.field_type = field_type
        self.field_persistence = field_persistence
        self.field_nullable = field_nullable
        self.field_immutable = field_immutable
        self.field_unique = field_unique

        if field_default is not None:
            self.field_default = field_default

        if field_enum is not None:
            self.field_enum = field_enum

        if field_format is not None:
            self.field_format = field_format

        if field_metadata is not None:
            self.field_metadata = field_metadata

        if field_alias is not None:
            self.field_alias = field_alias

        if field_fsm is not None:
            self.field_fsm = field_fsm

        if field_dbtype is not None:
            self.field_dbtype = field_dbtype

        if field_length is not None:
            self.field_length = field_length


class RefFieldYAML(object):
    def __init__(
        self,
        field_name: str,
        field_type: str,
        field_persistence: bool,
        field_unique: bool,
        ref_class: str,
        ref_class_field: str,
        field_metadata: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        field_dbtype: typing.Optional[str],
        field_length: typing.Optional[int],
    ) -> None:
        self.field_name = field_name
        self.field_type = field_type
        self.field_persistence = field_persistence
        self.field_unique = field_unique
        self.ref_class = ref_class
        self.ref_class_field = ref_class_field

        if field_metadata is not None:
            self.field_metadata = field_metadata

        if field_dbtype is not None:
            self.field_dbtype = field_dbtype

        if field_length is not None:
            self.field_length = field_length


class ClassMethodYAML(object):
    def __init__(self, method_body: str) -> None:
        self.method_body = method_body


class InstanceMethodYAML(object):
    def __init__(
        self,
        method_body: str,
        propagation_mode: bool,
        topdown: bool,
        auto_rollback: bool,
        multiplexable_number: int,
        field_order: str,
        timeout: typing.Optional[int],
    ) -> None:
        self.method_body = method_body
        self.propagation_mode = propagation_mode
        self.topdown = topdown
        self.auto_rollback = auto_rollback
        self.multiplexable_number = multiplexable_number
        self.field_order = field_order

        if timeout is not None:
            self.timeout = timeout


def to_yaml(cls_def: parser.ClassDefinition) -> ClassYAML:
    # Get setting
    setting: comp.Setting = cls_def.setting

    # YAML
    class_yaml = ClassYAML(
        category=setting.category,
        name=cls_def.name,
        persistence=setting.persistence,
        abstract=setting.abstract,
        extends=[extend.__name__ for extend in cls_def.setting.extends] if cls_def.setting.extends else None,
        api_generation=setting.api_generation,
        api_auto_response=setting.api_auto_response,
        scope=setting.scope,
        version=setting.version,
        created_at=setting.created_at,
        update=setting.update,
    )

    # identifier
    if cls_def.setting.identifier:
        class_yaml.set_identifier(
            field_name=cls_def.setting.identifier.name,
            field_type=convert_type(type=cls_def.setting.identifier.type),
            field_persistence=cls_def.setting.identifier.persistence,
            field_immutable=cls_def.setting.identifier.immutable,
            field_default=cls_def.setting.identifier.default,
            field_metadata=cls_def.setting.identifier.metadata,
            field_dbtype=cls_def.setting.identifier.dbtype,
            field_length=cls_def.setting.identifier.length,
        )

    # local_field
    for local_field in cls_def.setting.local_fields:
        field_format: typing.Optional[str]
        if isinstance(local_field.format, dict):
            field_format = json.dumps(local_field.format)
        else:
            field_format = local_field.format

        field_fsm: typing.Optional[typing.Dict[typing.Any, typing.Any]]
        if local_field.fsm is not None:
            field_fsm = {}
            for k, fsm in local_field.fsm.items():
                field_fsm[k] = {}
                field_fsm[k]['execution_method'] = fsm.execution_method
                if fsm.success_transition is not None:
                    field_fsm[k]['success_transition'] = fsm.success_transition
                if fsm.failure_transition is not None:
                    field_fsm[k]['failure_transition'] = fsm.failure_transition
                if fsm.status_value is not None:
                    field_fsm[k]['status_value'] = fsm.status_value
                if fsm.status_type is not None:
                    field_fsm[k]['status_type'] = fsm.status_type
                if fsm.pre_statuses is not None:
                    field_fsm[k]['pre_statuses'] = fsm.pre_statuses
        else:
            field_fsm = None

        class_yaml.add_local_field(
            field_name=local_field.name,
            field_type=convert_type(type=local_field.type),
            field_persistence=local_field.persistence,
            field_nullable=local_field.nullable,
            field_immutable=local_field.immutable,
            field_unique=local_field.unique,
            field_default=local_field.default,
            field_enum=local_field.enum,
            field_format=field_format,
            field_metadata=local_field.metadata,
            field_alias=local_field.alias,
            field_fsm=field_fsm,
            field_dbtype=local_field.dbtype,
            field_length=local_field.length,
        )

    # ref_field
    for ref_field in cls_def.setting.ref_fields:
        class_yaml.add_ref_field(
            field_name=ref_field.name,
            field_type=convert_type(type=ref_field.type),
            field_persistence=ref_field.persistence,
            field_unique=ref_field.unique,
            ref_class=ref_field.ref_class.__name__,
            ref_class_field=ref_field.ref_class_field,
            field_metadata=ref_field.metadata,
            field_dbtype=ref_field.dbtype,
            field_length=ref_field.length,
        )

    # class method
    for cls_method in cls_def.class_methods:
        class_yaml.add_class_method(method_body=cls_method.method_body)

    # instance method
    for instance_method in cls_def.instance_methods:
        class_yaml.add_instance_method(
            method_body=instance_method.method_body,
            propagation_mode=instance_method.instance_method.propagation_mode,
            topdown=instance_method.instance_method.topdown,
            auto_rollback=instance_method.instance_method.auto_rollback,
            multiplexable_number=instance_method.instance_method.multiplexable_number,
            field_order=instance_method.instance_method.field_order,
            timeout=instance_method.instance_method.timeout,
        )

    return class_yaml


def to_yaml_file(module_path: pathlib.Path, yaml_path: pathlib.Path) -> None:
    definitions = parser.get_definitions(module_path)
    for definition in definitions:
        yaml = to_yaml(definition)
        if definition.setting.workspace is None:
            raise exceptions.FatalError("workspace must not be 'None'")
        dir_path = yaml_path.joinpath(definition.setting.workspace).joinpath('classes')
        file_utils.create_dir(dir_path)
        file_path = dir_path.joinpath(f"{definition.name}.yml")
        logger.info(f"Creating '{str(file_path)}'")
        file_utils.create_file(file_path=file_path, data=yaml.dump())
