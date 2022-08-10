import pathlib

import qmonus_plugin_builder
from . import lib


def test_dump_action_creates_correct_yml_files(project_path: pathlib.Path, yaml_path: pathlib.Path):
    qmonus_plugin_builder.init(project_path=str(project_path))
    qmonus_plugin_builder.dump(project_path=str(project_path), yaml_path=str(yaml_path))
    init_yaml_path = pathlib.Path(__file__).joinpath('../../src/qmonus_plugin_builder/init_files/yml')
    assert lib.compare_dir(init_yaml_path, yaml_path, glob_pattern='**/*.yml')
