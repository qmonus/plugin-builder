import typing
import re

import yaml


def str_representer(dumper: typing.Any, data: typing.Any) -> typing.Any:
    if '\n' in data:
        # WA for https://github.com/yaml/pyyaml/issues/121 (PyYAML disallow trailing spaces in block scalars)
        data = re.sub(r' +\n', '\n', data)
        data = re.sub(r'( |\n)+\Z', '', data)
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    else:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

# Specify SafeDumper for yaml.safe_dump
yaml.add_representer(str, str_representer, Dumper=yaml.SafeDumper)


def dump(obj: typing.Any) -> str:
    yml: str = yaml.safe_dump(
        obj, indent=2, default_flow_style=False,
        allow_unicode=True, encoding='utf-8').decode('utf-8')
    return yml
