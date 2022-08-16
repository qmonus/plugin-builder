from __future__ import annotations
import typing
import logging
import pathlib

from .. import exceptions
from ..libs import yaml_utils, file_utils, data_lib
from . import component as comp
from . import parser

logger = logging.getLogger(__name__)


class ModuleYAML(object):
    def __init__(
        self,
        category: typing.Optional[str],
        name: str,
        code: str,
        version: int,
        update: typing.Optional[str],
    ) -> None:
        self.category = category
        self.name = name
        self.code = code
        self.version = version

        if update is not None:
            self.update = update

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        _dict: typing.Dict[str, typing.Any] = data_lib.to_primitive(self)
        return _dict

    def dump(self) -> str:
        dict_ = self.to_dict()
        return yaml_utils.dump(dict_)


def to_yaml(mod_def: parser.ModuleDefinition) -> ModuleYAML:
    # Get setting
    setting: comp.Setting = mod_def.setting

    # YAML
    module_yaml = ModuleYAML(
        category=setting.category,
        name=mod_def.name,
        code=mod_def.code,
        version=setting.version,
        update=setting.update,
    )
    return module_yaml


def to_yaml_file(module_path: pathlib.Path, yaml_path: pathlib.Path) -> None:
    definitions = parser.get_definitions(module_path)
    for definition in definitions:
        yaml = to_yaml(definition)
        if definition.setting.workspace is None:
            raise exceptions.FatalError("workspace must not be 'None'")
        dir_path = yaml_path.joinpath(definition.setting.workspace).joinpath('modules')
        file_utils.create_dir(dir_path)
        file_path = dir_path.joinpath(f"{definition.name}.yml")
        logger.info(f"Creating '{str(file_path)}'")
        file_utils.create_file(file_path=file_path, data=yaml.dump())
