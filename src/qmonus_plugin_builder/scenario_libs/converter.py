from __future__ import annotations

import logging
import pathlib
import typing

from .. import exceptions
from ..libs import data_lib, file_utils, yaml_utils
from . import component as comp
from . import parser

logger = logging.getLogger(__name__)


class ScenarioYAML(object):
    def __init__(
        self,
        category: typing.Optional[str],
        name: str,
        version: int,
        update: typing.Optional[str],
        uri: str,
        method: str,
        additional_paths: typing.List[str],
        scope: str,
        request_timeout: int,
        connect_timeout: int,
        routing_auto_generation_mode: bool,
    ) -> None:
        self.category = category
        self.name = name
        self.uri = uri
        self.method = method
        self.additional_paths = additional_paths
        self.request_timeout = request_timeout
        self.connect_timeout = connect_timeout
        self.version = version

        if update is not None:
            self.update = update

        self.routing_auto_generation_mode = routing_auto_generation_mode
        self.routing_options = {
            "scope": scope
        }

        self.global_variables: typing.Dict[str, GlobalVariableYAML] = {}
        self.transaction: typing.Any = {}
        self.commands: typing.List[typing.Union[RequestValidationCommandYAML, ScriptCommandYAML, dict]] = []

        # Not supported
        self.variable_groups: typing.Any = []
        self.spec: typing.Any = {
            "response": {
                "normal": {
                    "codes": [200]
                }
            }
        }

    def set_transaction(
        self,
        enable: bool,
        xdomain: str,
        xtype: str,
        xname: str,
        xname_use_counter: bool,
        auto_rollback: bool,
        auto_begin: bool,
        auto_response: bool,
        lock_keys: typing.List[str],
        retry_count: int,
        retry_interval: float,
        timeout: typing.Optional[int],
    ) -> None:
        transaction = TransactionYAML(
            enable=enable,
            xdomain=xdomain,
            xtype=xtype,
            xname=xname,
            xname_use_counter=xname_use_counter,
            auto_rollback=auto_rollback,
            auto_begin=auto_begin,
            auto_response=auto_response,
            lock_keys=lock_keys,
            retry_count=retry_count,
            retry_interval=retry_interval,
            timeout=timeout,
        )
        self.transaction = transaction

    def add_global_variable(
        self,
        name: str,
        description: str,
        initial: typing.Any,
    ) -> None:
        g_yaml = GlobalVariableYAML(
            description=description,
            initial=initial,
        )
        self.global_variables[name] = g_yaml

    def add_request_validation_command(
        self,
        label: typing.Optional[str],
        body: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        resources: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        params: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        headers: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        pre_process_code: typing.Optional[str],
        post_process_code: typing.Optional[str],
    ) -> None:
        command = RequestValidationCommandYAML(
            label=label,
            body=body,
            resources=resources,
            params=params,
            headers=headers,
            pre_process_code=pre_process_code,
            post_process_code=post_process_code,
        )
        self.commands.append(command)

    def add_script_command(
        self,
        label: typing.Optional[str],
        code: typing.Optional[str],
        cancellable: bool,
        cancel_code: typing.Optional[str],
        pre_process_code: typing.Optional[str],
        post_process_code: typing.Optional[str],
    ) -> None:
        command = ScriptCommandYAML(
            label=label,
            code=code,
            cancellable=cancellable,
            cancel_code=cancel_code,
            pre_process_code=pre_process_code,
            post_process_code=post_process_code,
        )
        self.commands.append(command)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        _dict: typing.Dict[str, typing.Any] = data_lib.to_primitive(self)
        _dict['transaction']['async'] = _dict['transaction']['async_']
        del _dict['transaction']['async_']
        return _dict

    def dump(self) -> str:
        dict_ = self.to_dict()
        return yaml_utils.dump(dict_)


class TransactionYAML(object):
    def __init__(
        self,
        enable: bool,
        xdomain: str,
        xtype: str,
        xname: str,
        xname_use_counter: bool,
        auto_rollback: bool,
        auto_begin: bool,
        auto_response: bool,
        lock_keys: typing.List[str],
        retry_count: int,
        retry_interval: float,
        timeout: typing.Optional[int],
    ) -> None:
        self.enable = enable
        self.xname = xname

        # Not supported
        self.async_ = True

        if self.enable:
            self.xname_use_counter = xname_use_counter
            self.xdomain = xdomain
            self.xtype = xtype
            self.auto_rollback = auto_rollback
            self.auto_begin = auto_begin
            self.auto_response = auto_response

            if lock_keys:
                self.lock: typing.Dict[str, typing.Any] = {}
                self.lock['lock_keys'] = lock_keys
                self.lock['retry_count'] = retry_count
                self.lock['retry_interval'] = retry_interval

            if timeout is not None:
                self.timeout = timeout


class GlobalVariableYAML(object):
    def __init__(self, description: str = '', initial: typing.Any = None) -> None:
        self.description = description
        self.initial = initial


class RequestValidationCommandYAML(object):
    def __init__(
        self,
        label: typing.Optional[str],
        pre_process_code: typing.Optional[str],
        post_process_code: typing.Optional[str],
        body: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        resources: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        params: typing.Optional[typing.Dict[typing.Any, typing.Any]],
        headers: typing.Optional[typing.Dict[typing.Any, typing.Any]],
    ) -> None:
        self.command = 'request_validation'

        if label is not None:
            self.label = label

        self.kwargs: typing.Dict[typing.Any, typing.Any] = {}
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

        if body is not None:
            self.kwargs['body'] = body

        if resources is not None:
            self.kwargs['resources'] = resources

        if params is not None:
            self.kwargs['params'] = params

        if headers is not None:
            self.kwargs['headers'] = headers


class ScriptCommandYAML(object):
    def __init__(
        self,
        label: typing.Optional[str],
        code: typing.Optional[str],
        cancellable: bool,
        cancel_code: typing.Optional[str],
        pre_process_code: typing.Optional[str],
        post_process_code: typing.Optional[str],
    ) -> None:
        self.command = 'script'

        if label is not None:
            self.label = label

        self.kwargs: typing.Dict[str, typing.Any] = {}
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
        self.kwargs['cancellation'] = {}
        self.kwargs['cancellation']['cancellable'] = cancellable

        if cancel_code is not None:
            self.kwargs['cancellation']['actions'] = [
                {
                    "action_type": "script",
                    "code": cancel_code
                }
            ]


def to_yaml(scenario_def: parser.ScenarioDefinition) -> ScenarioYAML:
    # Get setting
    setting: comp.Setting = scenario_def.setting
    transaction = setting.transaction

    scenario_yaml = ScenarioYAML(
        category=setting.category,
        name=scenario_def.name,
        version=setting.version,
        update=setting.update,
        uri=setting.uri,
        method=setting.method,
        additional_paths=setting.additional_paths,
        scope=setting.scope,
        request_timeout=setting.request_timeout,
        connect_timeout=setting.connect_timeout,
        routing_auto_generation_mode=setting.routing_auto_generation_mode,
    )

    scenario_yaml.set_transaction(
        enable=transaction.enable,
        xdomain=transaction.xdomain,
        xtype=transaction.xtype,
        xname=transaction.xname,
        xname_use_counter=transaction.xname_use_counter,
        auto_rollback=transaction.auto_rollback,
        auto_begin=transaction.auto_begin,
        auto_response=transaction.auto_response,
        lock_keys=transaction.lock_keys,
        retry_count=transaction.retry_count,
        retry_interval=transaction.retry_interval,
        timeout=transaction.timeout,
    )

    for global_variable in scenario_def.global_variables:
        scenario_yaml.add_global_variable(
            name=global_variable.name,
            description=global_variable.global_variable.description,
            initial=global_variable.global_variable.initial,
        )

    for command in scenario_def.commands:
        if isinstance(command, comp.RequestValidation):
            pre_process_code = command.get_code('pre_process')
            post_process_code = command.get_code('post_process')
            scenario_yaml.add_request_validation_command(
                label=command.__setting__().label,
                body=command.body(),
                resources=command.resources(),
                params=command.params(),
                headers=command.headers(),
                pre_process_code=pre_process_code,
                post_process_code=post_process_code,
            )
        elif isinstance(command, comp.Script):
            code = command.get_code('code')
            cancel_code = command.get_code('cancel_code')
            pre_process_code = command.get_code('pre_process')
            post_process_code = command.get_code('post_process')
            scenario_yaml.add_script_command(
                label=command.__setting__().label,
                code=code,
                cancellable=command.__setting__().cancellable,
                cancel_code=cancel_code,
                pre_process_code=pre_process_code,
                post_process_code=post_process_code,
            )
        elif isinstance(command, comp.BaseCommand) and hasattr(command, 'to_dict'):
            scenario_yaml.commands.append(command.to_dict())
        else:
            raise exceptions.CommandError("FatalError: Invalid command type")

    return scenario_yaml


def to_yaml_file(module_path: pathlib.Path, yaml_path: pathlib.Path) -> None:
    definitions = parser.get_definitions(module_path=module_path)
    for definition in definitions:
        yaml = to_yaml(definition)
        if definition.setting.workspace is None:
            raise exceptions.FatalError("workspace must not be 'None'")
        dir_path = yaml_path.joinpath(definition.setting.workspace).joinpath('scenarios')
        file_utils.create_dir(dir_path)
        file_path = dir_path.joinpath(f"{definition.name}.yml")
        logger.info(f"Creating '{str(file_path)}'")
        file_utils.create_file(file_path=file_path, data=yaml.dump())
