import typing



def aiodb() -> "_Connection":
    return _Connection()


class _Connection(object):
    async def __aenter__(self) -> "_Connection":
        return self

    async def __aexit__(self, exc_type: typing.Any, exc: typing.Any, tb: typing.Any) -> typing.Any:
        pass

    def begin(self) -> "_Transaction":
        return _Transaction()

    async def execute(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        pass

    def __getattr__(self, name: typing.Any) -> typing.Any:
        pass


class _Transaction(object):
    async def __aenter__(self) -> "_Transaction":
        return self

    async def __aexit__(self, exc_type: typing.Any, exc: typing.Any, tb: typing.Any) -> typing.Any:
        pass

    def __getattr__(self, name: typing.Any) -> typing.Any:
        pass
