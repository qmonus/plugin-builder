import pathlib
import tomli

import qmonus_plugin_builder


def test_pyproject_version_and_init_version_are_the_same():
    path = pathlib.Path(__file__).joinpath('../../pyproject.toml').resolve()
    pyproject = tomli.loads(path.read_text())
    assert pyproject['tool']['poetry']['version'] == qmonus_plugin_builder.__version__
