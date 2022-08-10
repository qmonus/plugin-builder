from __future__ import annotations
import abc
import typing

from ..libs import inspect_utils


# Header
class BaseHeader(abc.ABC):
    @abc.abstractmethod
    def __setting__(self) -> Setting:
        pass


class Setting(object):
    def __init__(
        self,
        unlimited: bool = True,
        count: int = -1,
        interval: int = 60,
        status: typing.Literal['active', 'inactive'] = 'inactive',
        workspace: typing.Optional[str] = None,
        category: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        version: int = 1,
        update: typing.Optional[str] = None,
    ) -> None:
        if workspace == '':
            raise ValueError("workspace must not be empty")

        self.workspace = workspace
        self.category = category
        self.name = name
        self.unlimited = unlimited
        self.count = count
        self.interval = interval
        self.status = status
        self.version = version
        self.update = update


# Global Variables
def global_variable(description: str = '', initial: typing.Any = None) -> typing.Any:
    return GlobalVariable(description=description, initial=initial)


class GlobalVariable(object):
    def __init__(
        self,
        description: str,
        initial: typing.Any,
    ) -> None:
        self.description = description
        self.initial = initial


# Commands
class BaseCommand(abc.ABC):
    @typing.final
    def get_code(self, method_name: str) -> typing.Optional[str]:
        cls_dict = vars(self.__class__)
        if method_name in cls_dict:
            code = inspect_utils.get_function_code(cls_dict[method_name])
        else:
            code = None
        return code


class ScriptSetting(object):
    def __init__(
        self,
        label: typing.Optional[str] = None,
    ) -> None:
        self.label = label


class Script(BaseCommand):
    @abc.abstractmethod
    def __setting__(self) -> ScriptSetting:
        pass

    @abc.abstractmethod
    async def code(self) -> None:
        """code (required)"""
        pass

    async def pre_process(self) -> None:
        """pre process code (optional)"""
        pass

    async def post_process(self) -> None:
        """post process code (optional)"""
        pass
