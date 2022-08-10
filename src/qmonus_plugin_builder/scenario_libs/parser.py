from __future__ import annotations
import typing
import types
import inspect
import logging
import importlib
import pathlib
import collections

from .. import exceptions
from . import component as comp

logger = logging.getLogger(__name__)


def get_files(module_path: pathlib.Path) -> typing.List[pathlib.Path]:
    if not module_path.is_dir():
        raise ValueError(f"Invalid module_path specified: '{str(module_path)}' does not exist.")

    files: typing.List[pathlib.Path] = []
    for file in module_path.glob('plugins/*/scenarios/**/*.py'):
        if file.name == '__init__.py':
            continue
        logger.info(f"Scenario file detected: '{str(file)}'")
        files.append(file)

    # Check duplication
    counter = collections.Counter([file.stem for file in files])
    for name, count in counter.items():
        if count != 1:
            raise exceptions.ScenarioError(f"Duplicate scenario '{name}' detected")

    return files


def get_modules(module_path: pathlib.Path) -> typing.List[types.ModuleType]:
    paths = get_files(module_path=module_path)
    modules: typing.List[types.ModuleType] = []
    for path in paths:
        module_name = str(path.relative_to(module_path.parent).with_suffix('').as_posix()).replace('/', '.')
        logger.info(f"importing scenario module '{module_name}'")
        module = importlib.import_module(module_name)
        modules.append(module)
    return modules


def get_definitions(module_path: pathlib.Path) -> typing.List[ScenarioDefinition]:
    modules = get_modules(module_path)
    definitions: typing.List[ScenarioDefinition] = []
    for module in modules:
        header_class: typing.Optional[typing.Type[comp.BaseHeader]] = \
            getattr(module, 'ScenarioHeader', None)
        if header_class is None:
            raise exceptions.ScenarioError(f"'class ScenarioHeader' does not exist in '{module.__name__}'")

        header = header_class()
        setting = header.__setting__()
        if setting.name is None:
            setting.name = _get_default_name(module)
        if setting.workspace is None:
            setting.workspace = _get_default_workspace(module)
        if setting.category is None:
            setting.category = _get_default_category(module)

        global_variable_definitions: typing.List[GlobalVariableDefinition] = []
        for k, v in vars(module).items():
            if isinstance(v, comp.GlobalVariable):
                global_variable_definition = GlobalVariableDefinition(
                    name=k,
                    global_variable=v,
                )
                global_variable_definitions.append(global_variable_definition)

        _commands: typing.List[comp.BaseCommand] = []
        for k, v in vars(module).items():
            if inspect.isclass(v):
                if issubclass(v, comp.BaseCommand):
                    _commands.append(v())
        commands: typing.List[comp.BaseCommand] = \
            sorted(_commands, key=lambda x: int(x.__class__.__name__.replace('Command', '')))

        for index, command in enumerate(commands):
            if command.__class__.__name__ != f'Command{index}':
                _err = f"Invalid command name '{command.__class__.__name__}' in '{module.__name__.split('.')[-1]}'. " \
                       f"Corrent name is 'Command{index}'."
                raise exceptions.ScenarioError(_err)
        
        definition = ScenarioDefinition(
            name=setting.name,
            setting=setting,
            global_variables=global_variable_definitions,
            commands=commands,
        )
        definitions.append(definition)

    return definitions


def _get_default_name(module: types.ModuleType) -> str:
    module_file = pathlib.Path(str(module.__file__)).resolve()
    name = module_file.stem
    return name


def _get_default_workspace(module: types.ModuleType) -> str:
    workspace = module.__name__.split('.')[2]
    return workspace


def _get_default_category(module: types.ModuleType) -> str:
    names = module.__name__.split('.')[4:-1]
    category = ".".join(names)
    return category


class ScenarioDefinition(object):
    def __init__(
        self,
        name: str,
        setting: comp.Setting,
        global_variables: typing.List[GlobalVariableDefinition],
        commands: typing.List[comp.BaseCommand],
    ) -> None:
        self.name = name
        self.setting = setting
        self.global_variables = global_variables
        self.commands = commands


class GlobalVariableDefinition(object):
    def __init__(self, name: str, global_variable: comp.GlobalVariable) -> None:
        self.name = name
        self.global_variable = global_variable
