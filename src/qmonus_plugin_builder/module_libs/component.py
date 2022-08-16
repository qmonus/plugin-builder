from __future__ import annotations
import typing
import abc


class BaseHeader(abc.ABC):
    @abc.abstractmethod
    def __setting__(self) -> Setting:
        pass


class Setting(object):
    def __init__(
        self,
        workspace: typing.Optional[str] = None,
        category: typing.Optional[str] = None,
        version: int = 1,
        update: typing.Optional[str] = None,
    ) -> None:
        if workspace == '':
            raise ValueError("workspace must not be empty")

        self.workspace = workspace
        self.category = category
        self.version = version
        self.update = update
