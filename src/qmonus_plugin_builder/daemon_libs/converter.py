from __future__ import annotations
import typing
import logging
import pathlib

from .. import exceptions
from ..libs import yaml_utils, file_utils, data_lib
from . import component as comp
from . import parser

logger = logging.getLogger(__name__)


class DaemonYAML(object):
    def __init__(
        self, 
        category: typing.Optional[str],
        name: str,
        unlimited: bool,
        count: int,
        interval: int,
        status: str,
        version: int,
        update: typing.Optional[str],
    ) -> None:
        self.category = category
        self.name = name
        self.status = status
        self.version = version

        if update is not None:
            self.update = update
        
        self.action = {
            'unlimited': unlimited,
            'count': count,
            'interval': interval,
        }

        self.global_variables: typing.Dict[str, GlobalVariableYAML] = {}
        self.commands: typing.List[ScriptCommandYAML] = []
        
        # Not supported
        self.variable_groups: typing.Any = []

    def add_global_variable(self, name: str, description: str, initial: typing.Any) -> None:
        g_yaml = GlobalVariableYAML(
            description=description,
            initial=initial,
        )
        self.global_variables[name] = g_yaml

    def add_script_command(
        self,
        label: typing.Optional[str],
        code: typing.Optional[str],
        pre_process_code: typing.Optional[str],
        post_process_code: typing.Optional[str],
    ) -> None:
        command = ScriptCommandYAML(
            label=label,
            code=code,
            pre_process_code=pre_process_code,
            post_process_code=post_process_code,
        )
        self.commands.append(command)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        _dict: typing.Dict[str, typing.Any] = data_lib.to_primitive(self)
        return _dict

    def dump(self) -> str:
        dict_ = self.to_dict()
        return yaml_utils.dump(dict_)


class GlobalVariableYAML(object):
    def __init__(self, description: str = '', initial: typing.Any = None) -> None:
        self.description = description
        self.initial = initial


class ScriptCommandYAML(object):
    def __init__(
        self,
        label: typing.Optional[str],
        code: typing.Optional[str],
        pre_process_code: typing.Optional[str],
        post_process_code: typing.Optional[str],
    ) -> None:
        self.command = 'script'

        if label is not None:
            self.label = label

        self.kwargs: typing.Any = {}
        if pre_process_code is not None:
            if 'aspect_options' not in self.kwargs:
                self.kwargs['aspect_options'] = {}
            self.kwargs['aspect_options']['pre'] = {
                "process": pre_process_code
            }

        if post_process_code is not None:
            if 'aspect_options' not in self.kwargs:
                self.kwargs['aspect_options'] = {}
            self.kwargs['aspect_options']['post'] = {
                "process": post_process_code
            }

        self.kwargs['code'] = code


def to_yaml(definition: parser.DaemonDefinition) -> DaemonYAML:
    # Get setting
    setting: comp.Setting = definition.setting

    daemon_yaml = DaemonYAML(
        category=setting.category,
        name=definition.name,
        unlimited=setting.unlimited,
        count=setting.count,
        interval=setting.interval,
        status=setting.status,
        version=setting.version,
        update=setting.update,
    )
    
    for global_variable in definition.global_variables:
        daemon_yaml.add_global_variable(
            name=global_variable.name,
            description=global_variable.global_variable.description,
            initial=global_variable.global_variable.initial,
        )

    for command in definition.commands:
        if isinstance(command, comp.Script):
            _setting = command.__setting__()
            code = command.get_code('code')
            pre_process_code = command.get_code('pre_process')
            post_process_code = command.get_code('post_process')
            daemon_yaml.add_script_command(
                label=_setting.label,
                code=code,
                pre_process_code=pre_process_code,
                post_process_code=post_process_code,
            )
        else:
            raise exceptions.CommandError("FatalError: Invalid command type")

    return daemon_yaml


def to_yaml_file(module_path: pathlib.Path, yaml_path: pathlib.Path) -> None:
    definitions = parser.get_definitions(module_path=module_path)
    for definition in definitions:
        yaml = to_yaml(definition)
        if definition.setting.workspace is None:
            raise exceptions.FatalError("workspace must not be 'None'")
        dir_path = yaml_path.joinpath(definition.setting.workspace).joinpath('daemons')
        file_utils.create_dir(dir_path)
        file_path = dir_path.joinpath(f"{definition.name}.yml")
        logger.info(f"Creating '{str(file_path)}'")
        file_utils.create_file(file_path=file_path, data=yaml.dump())
