import typing
import jinja2


def render(template: str, variables: typing.Dict[typing.Any, typing.Any]) -> str:
    env = jinja2.Environment(
        autoescape=False, undefined=jinja2.StrictUndefined,
        trim_blocks=True, lstrip_blocks=True)
    return env.from_string(template).render(variables)
