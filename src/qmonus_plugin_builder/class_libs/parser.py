from __future__ import annotations
import types
import typing
import logging
import inspect
import importlib
import pathlib
import re
import collections

from ..libs import inspect_utils, sort_lib
from .. import exceptions
from . import component as comp

logger = logging.getLogger(__name__)


def _sort_class_definitions(
    class_definitions: typing.List[ClassDefinition],
) -> typing.List[ClassDefinition]:
    graph: typing.Dict[str, typing.List[str]] = {}
    map: typing.Dict[str, ClassDefinition] = {}
    for class_definition in class_definitions:
        class_name = class_definition.name
        parent_class_names = [cls.__name__ for cls in class_definition.setting.extends] \
                             if class_definition.setting.extends is not None else []
        graph[class_name] = parent_class_names
        map[class_name] = class_definition

    sorted_class_names = sort_lib.topological_sort(graph)

    sorted_class_definitions: typing.List[ClassDefinition] = []
    for sorted_class_name in sorted_class_names:
        sorted_class_definitions.append(map[sorted_class_name])
    
    return sorted_class_definitions


def get_files(module_path: pathlib.Path) -> typing.List[pathlib.Path]:
    if not module_path.is_dir():
        raise ValueError(f"Invalid module_path specified: '{str(module_path)}' does not exist.")

    files: typing.List[pathlib.Path] = []
    for file in module_path.glob('plugins/*/classes/**/*.py'):
        if file.name == '__init__.py':
            continue
        logger.info(f"Class file detected: '{str(file)}'")
        files.append(file)
    
    # Check duplication
    counter = collections.Counter([file.stem for file in files])
    for name, count in counter.items():
        if count != 1:
            raise exceptions.ClassError(f"Duplicate class '{name}' detected")

    sorted_files = sorted(files, key=lambda x: str(x))
    return sorted_files


def get_modules(module_path: pathlib.Path) -> typing.List[types.ModuleType]:
    paths = get_files(module_path=module_path)
    modules: typing.List[types.ModuleType] = []
    for path in paths:
        module_name = str(path.relative_to(module_path.parent).with_suffix('').as_posix()).replace('/', '.')
        logger.info(f"importing class module '{module_name}'")
        module = importlib.import_module(module_name)
        modules.append(module)
    return modules


def get_definitions(module_path: pathlib.Path) -> typing.List[ClassDefinition]:
    modules = get_modules(module_path)
    definitions: typing.List[ClassDefinition] = []
    for module in modules:
        class_name = module.__name__.split('.')[-1]
        class_: typing.Optional[typing.Type[comp.BaseClass]] = getattr(module, class_name, None)
        if class_ is None:
            raise exceptions.ClassError(f"'{class_name}' does not exist in '{module.__name__}'")

        if len(class_.__bases__) != 1:
            raise exceptions.ClassError(f"Base class name must be 'classes.{class_name}' for '{class_name}'")

        if class_.__bases__[0].__name__ != class_name:
            raise exceptions.ClassError(f"Base class name must be 'classes.{class_name}' for '{class_name}'")

        if not issubclass(class_.__bases__[0], comp.BaseClass):
            raise exceptions.ClassError(f"Invalid base class '{class_.__bases__[0]}' for 'Class' in '{module.__name__}'")

        class_instance = class_()

        # setting
        setting = class_instance.__setting__()
        if setting.workspace is None:
            setting.workspace = _get_default_workspace(module)
        if setting.category is None:
            setting.category = _get_default_category(module)

        class_methods: typing.List[ClassMethodDefinition] = []
        instance_methods: typing.List[InstanceMethodDefinition] = []
        for k, v in vars(class_).items():
            # class method
            if isinstance(v, classmethod):
                class_method = getattr(class_instance, k)
                code = inspect.getsource(class_method)
                code = inspect_utils.outdent(code)
                is_coroutine = inspect.iscoroutinefunction(class_method)
                method_body = _remove_decorator(code=code, is_coroutine=is_coroutine)
                class_methods.append(ClassMethodDefinition(method_body=method_body))

            # instance method
            elif inspect.ismethod(v) and isinstance(v.__self__, comp.InstanceMethod):
                instance_method = getattr(class_instance, k)
                code = inspect.getsource(instance_method)
                code = inspect_utils.outdent(code)
                is_coroutine = inspect.iscoroutinefunction(instance_method)
                method_body = _remove_decorator(code=code, is_coroutine=is_coroutine)
                instance: comp.InstanceMethod = instance_method.__self__
                instance_methods.append(
                    InstanceMethodDefinition(
                        method_body=method_body,
                        instance_method=instance))

        definition = ClassDefinition(
            name=class_name,
            setting=setting,
            class_methods=class_methods,
            instance_methods=instance_methods,
        )
        definitions.append(definition)

    sorted_class_definitions = _sort_class_definitions(definitions)
    return sorted_class_definitions


def _remove_decorator(code: str, is_coroutine: bool) -> str:
    # TODO: Find better solution
    if is_coroutine:
        new_code = re.sub(r"@(.|\n)+?\n(?=async)", "", code, 1)
    else:
        new_code = re.sub(r"@(.|\n)+?\n(?=def)", "", code, 1)
    return new_code


def _get_default_workspace(module: types.ModuleType) -> str:
    workspace = module.__name__.split('.')[2]
    return workspace


def _get_default_category(module: types.ModuleType) -> str:
    names = module.__name__.split('.')[4:-1]
    category = ".".join(names)
    return category


class ClassDefinition(object):
    def __init__(
        self,
        name: str,
        setting: comp.Setting,
        class_methods: typing.List[ClassMethodDefinition],
        instance_methods: typing.List[InstanceMethodDefinition],
    ) -> None:
        self.name = name
        self.setting = setting
        self.class_methods = class_methods
        self.instance_methods = instance_methods


class ClassMethodDefinition(object):
    def __init__(self, method_body: str) -> None:
        self.method_body = method_body


class InstanceMethodDefinition(object):
    def __init__(
        self,
        method_body: str,
        instance_method: comp.InstanceMethod,
    ) -> None:
        self.method_body = method_body
        self.instance_method = instance_method
