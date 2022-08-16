from __future__ import annotations
import abc
import typing
import functools
import inspect


_TBaseClass = typing.TypeVar("_TBaseClass", bound="BaseClass")


class BaseClass(abc.ABC):
    def __init__(self) -> None:
        self.instance: str
        self.xid: str
        self.xname: str

    @abc.abstractmethod
    def __setting__(self) -> Setting:
        pass

    async def save(
        self,
        conn: typing.Any = None,
        tran: typing.Any = None,
        propagation_mode: bool = True,
        **kwargs: typing.Any,
    ) -> typing.Any:
        pass

    async def destroy(
        self,
        conn: typing.Any = None,
        tran: typing.Any = None,
        propagation_mode: bool = True,
        delay_seconds: int = 0,
    ) -> typing.Any:
        pass

    def __await__(self: _TBaseClass) -> typing.Generator[None, None, _TBaseClass]:
        yield
        return self

    def localfields(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        pass

    # def __getattr__(self, name) -> typing.Any:
    #     pass


class BaseType(abc.ABC):
    pass


class STRING(BaseType):
    def __init__(self) -> None:
        super().__init__()


class INTEGER(BaseType):
    def __init__(self) -> None:
        super().__init__()


class NUMBER(BaseType):
    def __init__(self) -> None:
        super().__init__()


class BOOLEAN(BaseType):
    def __init__(self) -> None:
        super().__init__()


class DATETIME(BaseType):
    def __init__(self) -> None:
        super().__init__()


class OBJECT(BaseType):
    def __init__(self) -> None:
        super().__init__()


class ARRAY(BaseType):
    def __init__(self) -> None:
        super().__init__()


class MU(BaseType):
    def __init__(self) -> None:
        super().__init__()


class ARRAY_OF_MU(BaseType):
    def __init__(self) -> None:
        super().__init__()


class CLASS(BaseType):
    def __init__(self, cls: typing.Type[BaseClass]) -> None:
        super().__init__()
        self.cls = cls


class ARRAY_OF_CLASS(BaseType):
    def __init__(self, cls: typing.Type[BaseClass]) -> None:
        super().__init__()
        self.cls = cls


class Setting(object):
    def __init__(
        self, 
        identifier: typing.Optional[Identifier] = None,
        local_fields: typing.Optional[typing.List[LocalField]] = None,
        ref_fields: typing.Optional[typing.List[RefField]] = None,
        persistence: bool = True, 
        abstract: bool = False, 
        extends: typing.Optional[typing.List[typing.Type[BaseClass]]] = None,
        api_generation: bool = False, 
        api_auto_response: typing.Optional[bool] = None,
        scope: typing.Optional[str] = None,
        workspace: typing.Optional[str] = None,
        category: typing.Optional[str] = None, 
        version: int = 1,
        created_at: typing.Optional[str] = None, 
        update: typing.Optional[str] = None,
    ) -> None:
        if workspace == '':
            raise ValueError("workspace must not be empty")
        
        if local_fields is None:
            local_fields = []
        
        if ref_fields is None:
            ref_fields = []

        self.identifier = identifier
        self.local_fields = local_fields
        self.ref_fields = ref_fields
        self.workspace = workspace
        self.category = category
        self.persistence = persistence
        self.abstract = abstract
        self.extends = extends
        self.api_generation = api_generation
        self.api_auto_response = api_auto_response
        self.scope = scope
        self.version = version
        self.created_at = created_at
        self.update = update


class Field(object):
    def __init__(self) -> None:
        pass
        # self.type: typing.Type[Base]


class Identifier(Field):
    def __init__(
        self, 
        name: str,
        type: BaseType, 
        persistence: bool = True,
        immutable: bool = True, 
        default: typing.Optional[str] = None,
        metadata: typing.Optional[typing.Dict[typing.Any, typing.Any]] = None,
        dbtype: typing.Optional[str] = None,
        length: typing.Optional[int] = None,
    ) -> None:
        self.name = name
        self.type = type
        self.persistence = persistence
        self.immutable = immutable
        self.default = default

        # self.nullable = nullable

        self.metadata = metadata
        self.dbtype = dbtype
        self.length = length


class FSM(object):
    def __init__(
        self, 
        execution_method: str, 
        success_transition: typing.Optional[str] = None,
        failure_transition: typing.Optional[str] = None,
        status_value: typing.Optional[str] = None,
        status_type: typing.Optional[str] = None,
        pre_statuses: typing.Optional[typing.List[str]] = None
    ) -> None:
        self.execution_method = execution_method
        self.success_transition = success_transition
        self.failure_transition = failure_transition
        self.status_value = status_value
        self.status_type = status_type
        self.pre_statuses = pre_statuses


class LocalField(Field):
    def __init__(
        self, 
        name: str,
        type: BaseType, 
        persistence: bool = True,
        nullable: bool = True, 
        immutable: bool = False, 
        unique: bool = False, 
        default: typing.Optional[str] = None,
        enum: typing.Optional[typing.List[str]] = None,
        format: typing.Optional[typing.Union[typing.Dict[typing.Any, typing.Any], str]] = None,
        metadata: typing.Optional[typing.Dict[typing.Any, typing.Any]] = None,
        alias: typing.Optional[str] = None,
        fsm: typing.Optional[typing.Dict[str, FSM]] = None,
        dbtype: typing.Optional[str] = None,
        length: typing.Optional[int] = None,
    ) -> None:
        self.name = name
        self.type = type
        self.persistence = persistence
        self.nullable = nullable
        self.immutable = immutable
        self.unique = unique
        self.default = default
        self.enum = enum
        self.format = format
        self.metadata = metadata
        self.alias = alias
        self.fsm = fsm
        self.dbtype = dbtype
        self.length = length


class RefField(Field):
    def __init__(
        self, 
        name: str,
        type: BaseType, 
        ref_class: typing.Type[BaseClass],
        ref_class_field: str,
        persistence: bool = True,
        unique: bool = False,
        metadata: typing.Optional[typing.Dict[typing.Any, typing.Any]] = None,
        dbtype: typing.Optional[str] = None,
        length: typing.Optional[int] = None,
    ) -> None:
        self.name = name
        self.type = type
        self.persistence = persistence
        self.unique = unique
        self.ref_class = ref_class
        self.ref_class_field = ref_class_field
        self.metadata = metadata
        self.dbtype = dbtype
        self.length = length


# InstanceMethod
F = typing.TypeVar('F', bound=typing.Callable[..., typing.Any])

def instance_method(
    propagation_mode: bool = False,
    topdown: bool = True,
    auto_rollback: bool = True,
    multiplexable_number: int = 1,
    field_order: str = 'ascend',
    timeout: typing.Optional[int] = None,
) -> typing.Callable[[F], F]:
    def decorator(func: F) -> F:
        class _InstanceMethod(InstanceMethod):
            def __init__(self) -> None:
                super().__init__(
                    propagation_mode=propagation_mode,
                    topdown=topdown,
                    auto_rollback=auto_rollback,
                    multiplexable_number=multiplexable_number,
                    field_order=field_order,
                    timeout=timeout)

            @functools.wraps(func)
            def wrapper(self, *args: typing.Any, **kwargs: typing.Any) -> None:
                func(*args, **kwargs)

            @functools.wraps(func)
            async def async_wrapper(self, *args: typing.Any, **kwargs: typing.Any) -> None:
                await func(*args, **kwargs)

        # def _to_any(v) -> typing.Any:
        #     return v

        wrap = _InstanceMethod()
        if inspect.iscoroutinefunction(func):
            # wrapper: F = _to_any(wrap.async_wrapper)
            # return wrapper
            return typing.cast(F, wrap.async_wrapper)
        else:
            # wrapper: F = _to_any(wrap.wrapper)
            # return wrapper
            return typing.cast(F, wrap.wrapper)
    return decorator


class InstanceMethod(object):
    def __init__(
        self, 
        propagation_mode: bool,
        topdown: bool,
        auto_rollback: bool,
        multiplexable_number: int,
        field_order: str,
        timeout: typing.Optional[int],
    ) -> None:
        self.propagation_mode = propagation_mode
        self.topdown = topdown
        self.auto_rollback = auto_rollback
        self.multiplexable_number = multiplexable_number
        self.field_order = field_order
        self.timeout = timeout
