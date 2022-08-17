import pathlib
import toml

import qmonus_plugin_builder


def test_pyproject_version_and_init_version_are_the_same():
    path = pathlib.Path(__file__).joinpath('../../pyproject.toml').resolve()
    pyproject = toml.load(path)
    assert pyproject['tool']['poetry']['version'] == qmonus_plugin_builder.__version__
