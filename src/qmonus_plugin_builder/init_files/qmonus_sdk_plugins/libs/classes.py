##########################
# Automatically generated
##########################

from __future__ import annotations
import typing
from qmonus_plugin_builder.class_libs import component as comp
from qmonus_sdk_plugins.libs.class_globals import *


class User(
    comp.BaseClass,
):
    def __init__(
        self,
        name: str,
        description: str,
        type: str,
        id: typing.Optional[str] = None,
    ):
        # Automatically Generated

        self.name: str = name
        self.description: str = description
        self.type: str = type
        self.id: typing.Optional[str] = id
        pass

    @classmethod
    async def load(
        cls,
        key,
        conn=None,
        shallow=False
    ) -> atom.User:
        raise NotImplementedError

    @classmethod
    async def retrieve(
        cls,
        conn=None,
        shallow=False,
        order_by=[],
        offset=0,
        limit=None,
        *,
        instance=None,
        xid=None,
        xname=None,
        name=None,
        description=None,
        type=None,
        id=None,
    ) -> typing.List[atom.User]:
        raise NotImplementedError



