from __future__ import annotations
import typing
import types
import logging
import inspect
import importlib
import pathlib
import collections

from . import component as comp
from .. import exceptions
from ..libs import file_utils

logger = logging.getLogger(__name__)


def get_files(module_path: pathlib.Path) -> typing.List[pathlib.Path]:
    if not module_path.is_dir():
        raise ValueError(f"Invalid module_path specified: '{str(module_path)}' does not exist.")

    files: typing.List[pathlib.Path] = []
    for file in module_path.glob('plugins/*/modules/**/*.py'):
        if file.name == '__init__.py':
            continue
        logger.info(f"Module file detected: '{str(file)}'")
        files.append(file)

    # Check duplication
    counter = collections.Counter([file.stem for file in files])
    for name, count in counter.items():
        if count != 1:
            raise exceptions.ClassError(f"Duplicate module '{name}' detected")

    return files


def get_modules(module_path: pathlib.Path) -> typing.List[types.ModuleType]:
    paths = get_files(module_path=module_path)
    modules: typing.List[types.ModuleType] = []
    for path in paths:
        module_name = str(path.relative_to(module_path.parent).with_suffix('').as_posix()).replace('/', '.')
        logger.info(f"importing module '{module_name}'")
        module = importlib.import_module(module_name)
        modules.append(module)
    return modules


def get_definitions(module_path: pathlib.Path) -> typing.List[ModuleDefinition]:
    py_modules = get_modules(module_path)
    definitions: typing.List[ModuleDefinition] = []
    for py_module in py_modules:
        module_class: typing.Optional[typing.Type[comp.BaseHeader]] = \
            getattr(py_module, 'ModuleHeader', None)
        if module_class is None:
            raise exceptions.ModuleError(f"'class ModuleHeader(BaseModuleHeader)' does not exist in '{py_module.__name__}'")

        module_instance = module_class()

        # setting
        setting = module_instance.__setting__()
        if setting.workspace is None:
            setting.workspace = _get_default_workspace(py_module)
        if setting.category is None:
            setting.category = _get_default_category(py_module)

        # code
        lines, starting_line_num = inspect.getsourcelines(module_class)
        ending_line_num = starting_line_num + len(lines)
        module_file = pathlib.Path(str(py_module.__file__)).resolve()
        module_text = file_utils.open_file(module_file)
        code = '\n'.join(module_text.split('\n')[ending_line_num - 1:]).lstrip()

        definition = ModuleDefinition(
            name=module_file.stem,
            setting=setting,
            code=code,
        )
        definitions.append(definition)

    return definitions


def _get_default_workspace(module: types.ModuleType) -> str:
    workspace = module.__name__.split('.')[2]
    return workspace


def _get_default_category(module: types.ModuleType) -> str:
    names = module.__name__.split('.')[4:-1]
    category = ".".join(names)
    return category


class ModuleDefinition(object):
    def __init__(
        self,
        name: str,
        setting: comp.Setting,
        code: str,
    ) -> None:
        self.name = name
        self.setting = setting
        self.code = code
