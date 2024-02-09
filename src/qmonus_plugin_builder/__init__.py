__version__ = '1.4.0'

import importlib
import json
import logging
import pathlib
import shutil
import sys
import typing

from . import templates
from .class_libs import component as class_component
from .class_libs import converter as class_converter
from .class_libs import parser as class_parser
from .daemon_libs import converter as daemon_converter
from .libs import file_utils, str_utils
from .module_libs import converter as module_converter
from .module_libs import parser as module_parser
from .scenario_libs import converter as scenario_converter

logger = logging.getLogger(__name__)


def init(project_path: str) -> None:
    root_path = pathlib.Path(project_path).resolve()
    if not root_path.is_dir():
        raise ValueError(f"'{str(root_path)}' is not a directory.")

    qmonus_sdk_plugins_path = root_path.joinpath('qmonus_sdk_plugins').resolve()

    init_files_path = pathlib.Path(__file__).joinpath('../init_files/qmonus_sdk_plugins').resolve()
    shutil.copytree(
        src=init_files_path,
        dst=qmonus_sdk_plugins_path,
        ignore=shutil.ignore_patterns('__pycache__'),
        dirs_exist_ok=True,
    )


def update(project_path: str) -> None:
    qmonus_sdk_plugins_path = pathlib.Path(project_path).joinpath('qmonus_sdk_plugins').resolve()
    if not qmonus_sdk_plugins_path.exists():
        raise ValueError(f"'{str(qmonus_sdk_plugins_path)}' does not exist")
    if not qmonus_sdk_plugins_path.is_dir():
        raise ValueError(f"'{str(qmonus_sdk_plugins_path)}' is not a directory")

    # add path
    sys.path.append(str(qmonus_sdk_plugins_path.parent))

    libs_path = qmonus_sdk_plugins_path.joinpath('libs')
    file_utils.delete_files_in_directory(dir_path=libs_path)

    atom_import_stmts = []
    class_names = []
    class_paths = class_parser.get_files(qmonus_sdk_plugins_path)
    for classes_path in class_paths:
        module_name = '..' + str(classes_path.relative_to(qmonus_sdk_plugins_path)
                                 .with_suffix('').as_posix()).replace('/', '.')
        class_name = classes_path.stem
        import_stmt = f'from {module_name} import {class_name}'
        atom_import_stmts.append(import_stmt)
        class_names.append(classes_path.stem)

    module_import_stmts = []
    paths = module_parser.get_files(qmonus_sdk_plugins_path)
    for path in paths:
        parent_name = '..' + str(path.parent.relative_to(qmonus_sdk_plugins_path)
                                 .with_suffix('').as_posix()).replace('/', '.')
        name = path.stem
        import_stmt = f'from {parent_name} import {name}'
        module_import_stmts.append(import_stmt)

    """Create libs.__init__.py"""
    init_path = libs_path.joinpath('__init__.py')
    logger.info(f"Creating '{str(init_path)}")
    file_utils.create_file(
        file_path=init_path,
        data=str_utils.render(template=templates.INIT_TEMPLATE,
                              variables={}))

    """Create libs.module.py"""
    _path = libs_path.joinpath('module.py')
    logger.info(f"Creating '{str(_path)}")
    file_utils.create_file(
        file_path=_path,
        data=str_utils.render(template=templates.MODULE_TEMPLATE,
                              variables={"import_stmts": module_import_stmts}))

    """Create libs.model.py"""
    # Create temporal model.py
    model_path = libs_path.joinpath('model.py')
    logger.info(f"Creating '{str(model_path)}")
    file_utils.create_file(
        file_path=model_path,
        data=str_utils.render(
            template=templates.MODEL_TEMPLATE,
            variables={
                "class_definitions": []}))

    """Create libs.scenario_context.py"""
    lib_path = libs_path.joinpath('scenario_context.py')
    logger.info(f"Creating '{str(lib_path)}")
    file_utils.create_file(
        file_path=lib_path,
        data=str_utils.render(template=templates.SCENARIO_CONTEXT_TEMPLATE,
                              variables={}))

    """Create libs.daemon_context.py"""
    lib_path = libs_path.joinpath('daemon_context.py')
    logger.info(f"Creating '{str(lib_path)}")
    file_utils.create_file(
        file_path=lib_path,
        data=str_utils.render(template=templates.DAEMON_CONTEXT_TEMPLATE,
                              variables={}))

    """Create libs.class_context.py"""
    lib_path = libs_path.joinpath('class_context.py')
    logger.info(f"Creating '{str(lib_path)}")
    file_utils.create_file(
        file_path=lib_path,
        data=str_utils.render(template=templates.CLASS_CONTEXT_TEMPLATE,
                              variables={}))

    """Create libs.module_context.py"""
    lib_path = libs_path.joinpath('module_context.py')
    logger.info(f"Creating '{str(lib_path)}")
    file_utils.create_file(
        file_path=lib_path,
        data=str_utils.render(template=templates.MODULE_CONTEXT_TEMPLATE,
                              variables={}))

    """Create libs.scenario_globals.py"""
    lib_path = libs_path.joinpath('scenario_globals.py')
    logger.info(f"Creating '{str(lib_path)}")
    file_utils.create_file(
        file_path=lib_path,
        data=str_utils.render(template=templates.SCENARIO_GLOBALS_TEMPLATE,
                              variables={}))

    """Create libs.daemon_globals.py"""
    lib_path = libs_path.joinpath('daemon_globals.py')
    logger.info(f"Creating '{str(lib_path)}")
    file_utils.create_file(
        file_path=lib_path,
        data=str_utils.render(template=templates.DAEMON_GLOBALS_TEMPLATE,
                              variables={}))

    """Create libs.class_globals.py"""
    lib_path = libs_path.joinpath('class_globals.py')
    logger.info(f"Creating '{str(lib_path)}")
    file_utils.create_file(
        file_path=lib_path,
        data=str_utils.render(template=templates.CLASS_GLOBALS_TEMPLATE,
                              variables={}))

    """Create libs.module_globals.py"""
    lib_path = libs_path.joinpath('module_globals.py')
    logger.info(f"Creating '{str(lib_path)}")
    file_utils.create_file(
        file_path=lib_path,
        data=str_utils.render(template=templates.MODULE_GLOBALS_TEMPLATE,
                              variables={}))

    """Create libs.atom.py"""
    class_path = libs_path.joinpath('atom.py')
    logger.info(f"Creating '{str(class_path)}")
    file_utils.create_file(
        file_path=class_path,
        data=str_utils.render(template=templates.ATOM_TEMPLATE,
                              variables={"import_stmts": atom_import_stmts}))

    """Create libs.classes.py"""
    # Create temporal classes.py
    classes_path = libs_path.joinpath('classes.py')
    logger.info(f"Creating '{str(classes_path)}")
    file_utils.create_file(
        file_path=classes_path,
        data=str_utils.render(template=templates.CLASSES_INITIAL_TEMPLATE,
                              variables={"class_names": class_names}))

    # Import atom first
    importlib.import_module('qmonus_sdk_plugins.libs.atom')

    # Create classes.py
    class_definitions = class_parser.get_definitions(qmonus_sdk_plugins_path)
    class_def_dicts = []
    class_def_dict_per_class_name = {}
    for class_definition in class_definitions:
        # extends
        if class_definition.setting.extends:
            extends = [dict(module=f"atom.{cls.__name__}", name=cls.__name__) for cls in class_definition.setting.extends]
        else:
            extends = [dict(module='comp.BaseClass', name='BaseClass')]

        # variables
        variables_without_defaults = []
        variables_with_defaults = []
        if class_definition.setting.identifier is not None:
            name = class_definition.setting.identifier.name
            default = _convert_default(class_definition.setting.identifier.default)
            nullable = True
            type = _convert_type(
                type=class_definition.setting.identifier.type,
                nullable=nullable,
            )

            if default is None and not nullable:
                variables_without_defaults.append({
                    "name": name,
                    "type": type,
                })
            else:
                variables_with_defaults.append({
                    "name": name,
                    "type": type,
                    "default": default,
                })

        for local_field in class_definition.setting.local_fields:
            name = local_field.name
            default = _convert_default(local_field.default)
            nullable = local_field.nullable
            type = _convert_type(
                type=local_field.type,
                nullable=nullable,
            )

            if default is None and not nullable:
                variables_without_defaults.append({
                    "name": name,
                    "type": type,
                })
            else:
                variables_with_defaults.append({
                    "name": name,
                    "type": type,
                    "default": default,
                })

        for ref_field in class_definition.setting.ref_fields:
            name = ref_field.name
            nullable = True
            type = _convert_type(
                type=ref_field.type,
                nullable=nullable,
            )

            if not nullable:
                variables_without_defaults.append({
                    "name": name,
                    "type": type,
                })
            else:
                variables_with_defaults.append({
                    "name": name,
                    "type": type,
                    "default": None,
                })

        class_def_dict = {
            "extends": extends,
            "name": class_definition.name,
            "variables_without_defaults": variables_without_defaults,
            "variables_with_defaults": variables_with_defaults,
            "extend_class_definitions": [],
        }
        class_def_dicts.append(class_def_dict)
        class_def_dict_per_class_name[class_def_dict['name']] = class_def_dict

    for class_def_dict in class_def_dicts:
        for extend in class_def_dict['extends']:
            if class_def_dict_per_class_name.get(extend.get('name')):
                class_def_dict['extend_class_definitions'].append(class_def_dict_per_class_name[extend.get('name')])

    """Recreating libs.classes.py"""
    logger.info(f"Recreating '{str(classes_path)}")
    file_utils.create_file(
        file_path=classes_path,
        data=str_utils.render(
            template=templates.CLASSES_FULL_TEMPLATE,
            variables={"class_definitions": class_def_dicts}))

    """Recreating libs.model.py"""
    model_path = libs_path.joinpath('model.py')
    logger.info(f"Recreating '{str(model_path)}")
    file_utils.create_file(
        file_path=model_path,
        data=str_utils.render(
            template=templates.MODEL_TEMPLATE,
            variables={"class_definitions": class_def_dicts}
        )
    )


def _convert_default(default: typing.Optional[str]) -> typing.Optional[str]:
    _default: typing.Optional[str]
    if isinstance(default, str):
        _default = f'{json.dumps(default)}'
    else:
        _default = default

    return _default


def _convert_type(
    type: class_component.BaseType,
    nullable: bool,
) -> str:
    if isinstance(type, class_component.CLASS):
        result = f'{type.cls.__name__}'
    elif isinstance(type, class_component.STRING):
        result = 'str'
    elif isinstance(type, class_component.INTEGER):
        result = 'int'
    elif isinstance(type, class_component.NUMBER):
        result = 'float'
    elif isinstance(type, class_component.BOOLEAN):
        result = 'bool'
    elif isinstance(type, class_component.OBJECT):
        result = 'dict'
    elif isinstance(type, class_component.DATETIME):
        result = 'datetime.datetime'
    elif isinstance(type, class_component.MU):
        result = 'typing.Any'
    elif isinstance(type, class_component.ARRAY_OF_CLASS):
        result = f'typing.List[{type.cls.__name__}]'
    elif isinstance(type, class_component.ARRAY_OF_MU):
        result = 'typing.List[typing.Any]'
    elif isinstance(type, class_component.ARRAY):
        result = 'typing.List[typing.Any]'
    else:
        raise ValueError(f"Invalid type: '{str(type.__class__.__name__)}")

    if nullable:
        result = f'typing.Optional[{result}]'

    return result


def dump(project_path: str, yaml_path: str) -> None:
    update(project_path=project_path)

    qmonus_sdk_plugins_path = pathlib.Path(project_path).joinpath('qmonus_sdk_plugins').resolve()
    _yaml_path = pathlib.Path(yaml_path).resolve()

    class_converter.to_yaml_file(module_path=qmonus_sdk_plugins_path, yaml_path=_yaml_path)
    scenario_converter.to_yaml_file(module_path=qmonus_sdk_plugins_path, yaml_path=_yaml_path)
    module_converter.to_yaml_file(module_path=qmonus_sdk_plugins_path, yaml_path=_yaml_path)
    daemon_converter.to_yaml_file(module_path=qmonus_sdk_plugins_path, yaml_path=_yaml_path)
