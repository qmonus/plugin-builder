import typing


def to_primitive(data: typing.Any) -> typing.Any:
    if isinstance(data, (str, int, float, bool)) or data is None:
        return data
    elif isinstance(data, dict):
        _dict = {}
        for k, v in data.items():
            _dict[k] = to_primitive(v)
        return _dict
    elif isinstance(data, (list, tuple)):
        items = []
        for item in data:
            items.append(to_primitive(item))
        return items
    elif hasattr(data, '__dict__'):
        _dict = {}
        for k, v in vars(data).items():
            _dict[k] = to_primitive(v)
        return _dict
    else:
        return str(data)
