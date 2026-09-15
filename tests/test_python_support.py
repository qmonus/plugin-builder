import pathlib
import re

import tomli
import yaml


REPO_ROOT = pathlib.Path(__file__).joinpath('../..').resolve()


def _pyproject_python_floor() -> tuple[int, int]:
    pyproject = tomli.loads((REPO_ROOT / 'pyproject.toml').read_text())
    constraint = pyproject['tool']['poetry']['dependencies']['python']
    match = re.fullmatch(r'>=(\d+)\.(\d+)', constraint)
    assert match, f'unexpected python constraint format: {constraint!r}'
    return (int(match.group(1)), int(match.group(2)))


def _ci_python_versions() -> list[tuple[int, int]]:
    workflow = yaml.safe_load((REPO_ROOT / '.github/workflows/ci.yml').read_text())
    versions = workflow['jobs']['test']['strategy']['matrix']['python-version']
    return [tuple(int(part) for part in v.split('.')) for v in versions]


def _readme_python_versions() -> list[tuple[int, int]]:
    readme = (REPO_ROOT / 'README.md').read_text()
    return [
        (int(major), int(minor))
        for major, minor in re.findall(r'^- Python (\d+)\.(\d+)$', readme, re.MULTILINE)
    ]


def test_ci_matrix_versions_satisfy_pyproject_python_floor():
    floor = _pyproject_python_floor()
    ci_versions = _ci_python_versions()
    assert ci_versions, 'CI python-version matrix must not be empty'
    for version in ci_versions:
        assert version >= floor, (
            f'CI tests Python {version[0]}.{version[1]}, '
            f'which is below the pyproject.toml floor {floor[0]}.{floor[1]}'
        )


def test_pyproject_floor_matches_lowest_ci_version():
    floor = _pyproject_python_floor()
    ci_versions = _ci_python_versions()
    assert floor == min(ci_versions), (
        'pyproject.toml python floor should equal the lowest version actually '
        'exercised by CI, otherwise the declared support is unverified'
    )


def test_readme_supported_versions_match_ci_matrix():
    ci_versions = sorted(_ci_python_versions())
    readme_versions = sorted(_readme_python_versions())
    assert readme_versions == ci_versions, (
        f'README サポートバージョン {readme_versions} does not match '
        f'CI python-version matrix {ci_versions}'
    )
