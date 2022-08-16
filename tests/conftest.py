import pathlib
import sys

import pytest


@pytest.fixture(scope='function')
def project_path(tmp_path: pathlib.Path):
    path = tmp_path.joinpath('project')
    path.mkdir()
    return path


@pytest.fixture(scope='function')
def yaml_path(tmp_path: pathlib.Path):
    path = tmp_path.joinpath('yaml')
    path.mkdir()
    return path


@pytest.fixture(scope='function')
def temp_module_path(tmp_path: pathlib.Path):
    path = tmp_path.joinpath('temp_module').resolve()
    path.mkdir()
    sys.path.append(str(path))
    return path
