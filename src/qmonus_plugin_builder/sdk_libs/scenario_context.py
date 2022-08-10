import typing


class Session(object):
    def __init__(self) -> None:
        self.request = Request()

    def set_header(self, name: typing.Any, value: typing.Any) -> typing.Any:
        pass

    def add_header(self, name: typing.Any, value: typing.Any) -> typing.Any:
        pass

    def set_status(self, status_code: int) -> typing.Any:
        pass

    def finish(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        pass        

    def NO_CONTENT(self) -> typing.Any:
        pass

    def __getattr__(self, name: typing.Any) -> typing.Any:
        pass


class Request(object):
    def __init__(self) -> None:
        self.method: str
        self.path: str
        self.headers: dict
        self.body: str

    def __getattr__(self, name: typing.Any) -> typing.Any:
        pass


class FrozenRequest(object):
    def __init__(self) -> None:
        self.headers: typing.Any
        self.resources: typing.Any
        self.params: typing.Any
        self.body: typing.Any

    def __getattr__(self, name: typing.Any) -> typing.Any:
        pass


axis: typing.Any = None
qmonus: typing.Any = None

session = Session()
resources: typing.Dict[str, str] = {}
params: typing.Dict[str, typing.List[str]] = {}
request = FrozenRequest()

