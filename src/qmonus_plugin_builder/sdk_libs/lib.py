from __future__ import annotations
import typing as _typing
import logging as _logging

# modules
import io as io
import re as re
import time as time
import uuid as uuid
import json as json
import datetime as datetime
import copy as copy
import base64 as base64
import ipaddress as ipaddress
import urllib as urllib
import asyncio as asyncio
import sqlalchemy as sqlalchemy
import jsonschema as jsonschema


class _Any(object):
    def __getattr__(self, name: _typing.Any) -> _typing.Any:
        return _Any()

    def __call__(self, *arg: _typing.Any, **kwarg: _typing.Any) -> _typing.Any:
        return _Any()

    def __await__(self) -> _typing.Any:
        yield
        return self


logger = _logging.getLogger(__name__)
options: _typing.Any = _Any()
MU: _typing.Any = _Any()
QmonusAccount: _typing.Any = _Any()
HTTPHeaders: _typing.Any = _Any()


def faker(*args: _typing.Any, **kwargs: _typing.Any) -> _typing.Any:
    raise NotImplementedError


# Built-in object
class _HTTPResponse(object):
    """dummy response class for callout"""
    def __init__(self) -> None:
        self.code: int
        self.body: bytes
    
    def __getattr__(self, name: _typing.Any) -> _typing.Any:
        raise NotImplementedError


async def callout(
    path: _typing.Optional[str] = None,
    method: str = 'GET',
    body: _typing.Any = None,
    headers: _typing.Any = None,
    url: _typing.Optional[str] = None,
    endpoint: str = f"{options.default_apigw_host}:{options.default_apigw_port}",
    static_route: _typing.Any = None,
    xid: _typing.Any = None,
    xname: _typing.Any = None,
    scenario_resume_index: _typing.Any = None,
    scenario_iteration: _typing.Any = False,
    connect_timeout: int = options.callout_connect_timeout,
    request_timeout: int = options.callout_request_timeout,
    retry_interval: float = 0,
    retry_count: int = 0,
    retry_codes: _typing.Any = [599],
    delay: _typing.Any = 0,
    authentication: _typing.Any = None,
    lambda_termination: _typing.Any = True,
    validate_cert: _typing.Any = True,
    ca_certs: _typing.Any = None,
    client_key: _typing.Any = None,
    client_cert: _typing.Any = None,
    response_jsonify: _typing.Any = False,
    via_apigw: _typing.Any = True,
    auto_url_encode: _typing.Any = False,
) -> _HTTPResponse:
    raise NotImplementedError


async def status_poll(*args: _typing.Any, **kwargs: _typing.Any) -> _typing.Any:
    """deprecated"""
    raise NotImplementedError


def genkey(
    length: _typing.Any = 64,
    continuity: _typing.Any = 3,
    exclude: _typing.Any = None,
) -> str:
    raise NotImplementedError


def encrypt(key: str, origin: str) -> str:
    raise NotImplementedError


def decrypt(key: str, origin: str) -> str:
    raise NotImplementedError


def queryjoin(origin: _typing.Any, **kwargs: _typing.Any) -> _typing.Any:
    raise NotImplementedError


async def multi(coroutines: _typing.Any = []) -> _typing.Any:
    raise NotImplementedError


async def futureization(f: _typing.Any, *args: _typing.Any, loop: _typing.Any = None) -> _typing.Any:
    """deprecated"""
    raise NotImplementedError


Awaitable: _typing.Any = _Any()


bg: _typing.Any = _Any()


async def rendering(tag: _typing.Any, *args: _typing.Any, **kwargs: _typing.Any) -> _typing.Any:
    raise NotImplementedError


class Template(object):
    def __init__(self, **kwargs: _typing.Any) -> None:
        raise NotImplementedError

    def __getattr__(self, name: _typing.Any) -> _typing.Any:
        raise NotImplementedError

    async def validate(self, **kwargs: _typing.Any) -> bool:
        raise NotImplementedError

    async def render(self, **kwargs: _typing.Any) -> _typing.Any:
        raise NotImplementedError

    @classmethod
    async def exists(cls, tag: _typing.Any) -> bool:
        raise NotImplementedError

    @classmethod
    async def load(cls, tag: _typing.Any) -> Template:
        raise NotImplementedError


where_statement: _typing.Any = _Any()


rowtodict: _typing.Any = _Any()


from sqlalchemy import (
    and_ as and_,
    or_ as or_,
    not_ as not_,
    join as join,
)
select = _Any() # for sqlalchemy 1.4 style


async def scp(*args: _typing.Any, **kwargs: _typing.Any) -> _typing.Any:
    raise NotImplementedError


async def sendmail(*args: _typing.Any, **kwargs: _typing.Any) -> _typing.Any:
    raise NotImplementedError


async def get_service_config(service: _typing.Any) -> _typing.Any:
    raise NotImplementedError


task: _typing.Any = _Any()


waitfor: _typing.Any = _Any()


transaction_active_check: _typing.Any = _Any()


get_transactions: _typing.Any = _Any()


waitfor_transaction: _typing.Any = _Any()


async def allocate_counter(*args: _typing.Any, **kwargs: _typing.Any) -> _typing.Any:
    """deprecated"""
    raise NotImplementedError


Counter: _typing.Any = _Any()


ElementTree: _typing.Any = _Any()


dict2xml: _typing.Any = _Any() # deprecated


magic: _typing.Any = _Any()


pubsub: _typing.Any = _Any()


qprint: _typing.Any = _Any()


deserialize: _typing.Any = _Any()


flattening: _typing.Any = _Any()


slack: _typing.Any = _Any()


gRPC: _typing.Any = _Any()


Parse: _typing.Any = _Any()


MessageToJson: _typing.Any = _Any()


neo4j: _typing.Any = _Any() # deprecated


nodetodict: _typing.Any = _Any() # deprecated


class Error(Exception):
    def __init__(
        self,
        code: int,
        reason: str = '',
        body: _typing.Any = None,
        moreInfo: _typing.Any = None,
    ) -> None:
        self.code = code
        self.reason = reason
        self.body = body


class Cache(object):
    def __init__(self, key: _typing.Any, timeout: _typing.Any = 3, ttl: _typing.Any = 10) -> None:
        raise NotImplementedError

    async def __aenter__(self) -> _typing.Any:
        raise NotImplementedError

    async def __aexit__(self, exc_type: _typing.Any, exc: _typing.Any, tb: _typing.Any) -> _typing.Any:
        raise NotImplementedError

    @classmethod
    async def put(cls, key: _typing.Any, value: _typing.Any, ttl: _typing.Any = 60) -> _typing.Any:
        raise NotImplementedError

    @classmethod
    async def get(cls, key: _typing.Any) -> _typing.Any:
        raise NotImplementedError

    @classmethod
    async def exists(cls, key: _typing.Any) -> bool:
        raise NotImplementedError

    @classmethod
    async def delete(cls, key: _typing.Any) -> _typing.Any:
        raise NotImplementedError


clock: _typing.Any = _Any()


Scenario: _typing.Any = _Any()


Daemon: _typing.Any = _Any()


Format: _typing.Any = _Any()


Geo: _typing.Any = _Any()


SQL: _typing.Any = _Any()


Redis: _typing.Any = _Any()


Model: _typing.Any = _Any()


Plugins: _typing.Any = _Any()


Faker: _typing.Any = _Any()


FakeHttpResponse: _typing.Any = _Any()


Illusion: _typing.Any = _Any()


TDD: _typing.Any = _Any()


Test: _typing.Any = _Any()


Booking: _typing.Any = _Any()


lambda_event: _typing.Any = _Any()


lambda_convergence: _typing.Any = _Any()


LambdaBooking: _typing.Any = _Any()


Websocket: _typing.Any = _Any()


ipam: _typing.Any = _Any()


class CLI(object):
    def __init__(self, **kwargs: _typing.Any) -> None:
        pass
    
    async def send_command(self, *args: _typing.Any, **kwargs: _typing.Any) -> _typing.Any:
        raise NotImplementedError
    
    async def send_config_set(self, *args: _typing.Any, **kwargs: _typing.Any) -> _typing.Any:
        raise NotImplementedError
    
    async def __aenter__(self) -> CLI:
        raise NotImplementedError

    async def __aexit__(self, *args: _typing.Any, **kwargs: _typing.Any) -> _typing.Any:
        raise NotImplementedError

    def __getattr__(self, name: _typing.Any) -> _typing.Any:
        raise NotImplementedError


Device: _typing.Any = _Any()


ComplexDevice: _typing.Any = _Any()


CLIProxy: _typing.Any = _Any()


NetconfProxy: _typing.Any = _Any()


class Netconf(object):
    def __init__(self, *args: _typing.Any, **kwargs: _typing.Any) -> None:
        raise NotImplementedError

    async def __aenter__(self) -> Netconf:
        raise NotImplementedError

    async def __aexit__(self, exc_type: _typing.Any, exc: _typing.Any, tb: _typing.Any) -> _typing.Any:
        raise NotImplementedError

    def __getattr__(self, name: _typing.Any) -> _typing.Any:
        raise NotImplementedError


class _SNMP(object):
    async def bulk(
        self, 
        address: _typing.Any,
        port: _typing.Any = 161,
        oids: _typing.Any = [],
        nonRepeaters: _typing.Any = 0,
        maxRepetitions: _typing.Any = None,
        timeout: _typing.Any = None,
        retries: _typing.Any = None,
    ) -> _typing.Any:
        raise NotImplementedError

    async def get(
        self,
        address: _typing.Any,
        port: _typing.Any = 161,
        oid: _typing.Any = None,
        timeout: _typing.Any = None,
        retries: _typing.Any = None,
    ) -> _typing.Any:
        raise NotImplementedError

    def __getattr__(self, name: _typing.Any) -> _typing.Any:
        raise NotImplementedError


class SNMPv2(_SNMP):
    def __init__(self, *args: _typing.Any, **kwargs: _typing.Any):
        raise NotImplementedError


class SNMPv3(_SNMP):
    def __init__(self, *args: _typing.Any, **kwargs: _typing.Any) -> None:
        raise NotImplementedError


Collection: _typing.Any = _Any()


Runtime: _typing.Any = _Any()


FIFO: _typing.Any = _Any()


mFIFO: _typing.Any = _Any()
