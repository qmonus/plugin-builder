from __future__ import annotations

import abc
import typing
from dataclasses import asdict, dataclass
from enum import Enum
from http import HTTPStatus

from ..libs import dictionary, inspect_utils

SCOPE_LOCAL = 'local'
SCOPE_PUBLIC = 'public'
SCOPE_SECURE = 'secure'


@dataclass
class Spec:
    @dataclass
    class Request:
        @dataclass
        class PropertieAttributeSchema:
            class Type(Enum):
                STRING = 'string'
                INT = 'integer'
                ARRAY = 'array'
                # TODO add other type
            type: Spec.Request.PropertieAttributeSchema.Type
            pattern: typing.Optional[str] = None
            format: typing.Optional[str] = None
            default: typing.Optional[typing.Any] = None
            example: typing.Optional[typing.Any] = None
            description: typing.Optional[str] = None
            items: typing.Optional[dict] = None

        @dataclass
        class Headers:
            properties: typing.Dict[str, Spec.Request.PropertieAttributeSchema]
            type: str = 'object'
            required: typing.Optional[typing.List[str]] = None
            dollar_sign_schema: typing.Optional[str] = None

        @dataclass
        class Params:
            properties: typing.Dict[str, Spec.Request.PropertieAttributeSchema]
            type: str = 'object'
            dollar_sign_schema: typing.Optional[str] = None

        @dataclass
        class Resources:
            properties: typing.Dict[str, Spec.Request.PropertieAttributeSchema]
            type: str = 'object'
            required: typing.Optional[typing.List[str]] = None
            dollar_sign_schema: typing.Optional[str] = None

        headers: typing.Optional[Spec.Request.Headers] = None
        params: typing.Optional[Spec.Request.Params] = None
        resources: typing.Optional[Spec.Request.Resources] = None

    @dataclass
    class Response:
        @dataclass
        class Normal:
            codes: typing.Union[typing.List[int], typing.Tuple[int]] = (HTTPStatus.OK.value,)

        normal: typing.Optional[Spec.Response.Normal] = Normal()

    request: typing.Optional[Spec.Request] = None
    response: typing.Optional[Spec.Response] = Response()

    def to_dict(self, empty_the_value_of_none: bool = True) -> dict:
        dict_of_self = dictionary.rename_now_key_to_new_key(asdict(self), now_key='dollar_sign_schema', new_key='$schema')
        dict_of_self = dictionary.enum_to_value(dict_of_self)
        if empty_the_value_of_none:
            return dictionary.empty_the_select_value(dict_of_self, select_value=None)
        return dict_of_self


class BaseHeader(abc.ABC):
    @abc.abstractmethod
    def __setting__(self) -> Setting:
        pass


class Setting(object):
    def __init__(
        self,
        method: typing.Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        uri: str,
        transaction: typing.Optional[Transaction] = None,
        scope: typing.Literal['local', 'public', 'secure'] = 'local',
        request_timeout: int = 60,
        connect_timeout: int = 60,
        routing_auto_generation_mode: bool = True,
        additional_paths: typing.Optional[typing.List[str]] = None,
        workspace: typing.Optional[str] = None,
        category: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        version: int = 1,
        update: typing.Optional[str] = None,
        spec: Spec = Spec(),
    ) -> None:
        if transaction is None:
            transaction = Transaction(enable=False)

        if additional_paths is None:
            additional_paths = []

        if workspace == '':
            raise ValueError("workspace must not be empty")

        self.method = method
        self.uri = uri
        self.scope = scope
        self.request_timeout = request_timeout
        self.connect_timeout = connect_timeout
        self.routing_auto_generation_mode = routing_auto_generation_mode
        self.additional_paths = additional_paths
        self.transaction = transaction
        self.workspace = workspace
        self.category = category
        self.name = name
        self.version = version
        self.update = update
        self.spec = spec.to_dict()


class Transaction(object):
    def __init__(
        self,
        enable: bool,
        xdomain: str = '',
        xtype: str = '',
        xname: str = '',
        xname_use_counter: bool = False,
        auto_rollback: bool = True,
        auto_begin: bool = True,
        auto_response: bool = False,
        lock_keys: typing.Optional[typing.List[str]] = None,
        retry_count: int = 0,
        retry_interval: float = 0,
        timeout: typing.Optional[int] = None,
        async_: bool = True,
    ) -> None:
        if lock_keys is None:
            lock_keys = []

        self.enable = enable
        self.xdomain = xdomain
        self.xtype = xtype
        self.xname = xname
        self.xname_use_counter = xname_use_counter
        self.auto_rollback = auto_rollback
        self.auto_begin = auto_begin
        self.auto_response = auto_response
        self.lock_keys = lock_keys
        self.retry_count = retry_count
        self.retry_interval = retry_interval
        self.timeout = timeout
        self.async_ = async_


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


class RequestValidationSetting(object):
    def __init__(self, label: typing.Optional[str] = None) -> None:
        self.label = label


class RequestValidation(BaseCommand):
    @abc.abstractmethod
    def __setting__(self) -> RequestValidationSetting:
        pass

    def resources(self) -> typing.Optional[typing.Dict[typing.Any, typing.Any]]:
        """path schema (optional)"""
        return None

    def params(self) -> typing.Optional[typing.Dict[typing.Any, typing.Any]]:
        """query parameter schema (optional)"""
        return None

    def headers(self) -> typing.Optional[typing.Dict[typing.Any, typing.Any]]:
        """header schema (optional)"""
        return None

    def body(self) -> typing.Optional[typing.Dict[typing.Any, typing.Any]]:
        """body schema (optional)"""
        return None

    async def pre_process(self) -> None:
        """pre process code (optional)"""
        pass

    async def post_process(self) -> None:
        """post process code (optional)"""
        pass


class ScriptSetting(object):
    def __init__(
        self,
        label: typing.Optional[str] = None,
        cancellable: bool = True,
    ) -> None:
        self.label = label
        self.cancellable = cancellable


class Script(BaseCommand):
    @abc.abstractmethod
    def __setting__(self) -> ScriptSetting:
        pass

    @abc.abstractmethod
    async def code(self) -> None:
        """code (required)"""
        pass

    async def cancel_code(self) -> None:
        """cancel code (optional)"""
        pass

    async def pre_process(self) -> None:
        """pre process code (optional)"""
        pass

    async def post_process(self) -> None:
        """post process code (optional)"""
        pass


class BreakpointSetting(object):
    def __init__(
        self,
        abort_in_kwargs: bool = True,
        immediate_cancel_in_kwargs: bool = True,
    ) -> None:
        self.abort_in_kwargs = abort_in_kwargs
        self.immediate_cancel_in_kwargs = immediate_cancel_in_kwargs


class Breakpoint(BaseCommand):
    @abc.abstractmethod
    def __setting__(self) -> BreakpointSetting:
        pass

    def to_dict(self) -> dict:
        return dict(
            command='breakpoint',
            kwargs=dict(
                abort=self.__setting__().abort_in_kwargs,
                immediate_cancel=self.__setting__().immediate_cancel_in_kwargs,
            ),
        )


class ServeSetting(object):
    def __init__(
        self,
        path_in_kwargs: typing.Optional[str] = None,
        method_in_kwargs: typing.Optional[str] = None,
        xname_key_in_kwargs: typing.Optional[str] = None,
    ) -> None:
        self.path_in_kwargs = path_in_kwargs
        self.method_in_kwargs = method_in_kwargs
        self.xname_key_in_kwargs = xname_key_in_kwargs


class Serve(BaseCommand):
    @abc.abstractmethod
    def __setting__(self) -> ServeSetting:
        pass

    async def pre_process(self) -> None:
        """pre process code (optional)"""
        pass

    def to_dict(self) -> dict:
        return dict(
            command='serve',
            kwargs=dict(
                path=self.__setting__().path_in_kwargs,
                method=self.__setting__().method_in_kwargs,
                xname_key=self.__setting__().xname_key_in_kwargs,
                aspect_options=dict(pre=dict(process=self.get_code('pre_process'))),
            ),
        )


class SleepSetting(object):
    def __init__(
        self,
        seconds_in_kwargs: typing.Optional[int] = None,
    ) -> None:
        self.seconds_in_kwargs = seconds_in_kwargs


class Sleep(BaseCommand):
    @abc.abstractmethod
    def __setting__(self) -> SleepSetting:
        pass

    def to_dict(self) -> dict:
        return dict(
            command='sleep',
            kwargs=dict(
                seconds=self.__setting__().seconds_in_kwargs
            ),
        )
