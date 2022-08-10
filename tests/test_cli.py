import sys
import pathlib
import subprocess


def test_init_action_works(project_path: pathlib.Path):
    process = subprocess.run(
        [sys.executable, '-m', 'qmonus_plugin_builder', 'init', str(project_path)]
    )
    assert process.returncode == 0


def test_update_action_works(project_path: pathlib.Path):
    process = subprocess.run(
        [sys.executable, '-m', 'qmonus_plugin_builder', 'init', str(project_path)]
    )
    assert process.returncode == 0

    process = subprocess.run(
        [sys.executable, '-m', 'qmonus_plugin_builder', 'update', str(project_path)]
    )
    assert process.returncode == 0


def test_dump_action_works(project_path: pathlib.Path, yaml_path: pathlib.Path):
    process = subprocess.run(
        [sys.executable, '-m', 'qmonus_plugin_builder', 'init', str(project_path)]
    )
    assert process.returncode == 0

    process = subprocess.run(
        [sys.executable, '-m', 'qmonus_plugin_builder', 'dump', str(project_path), str(yaml_path)]
    )
    assert process.returncode == 0
