import pathlib


def compare_dir(a: pathlib.Path, b: pathlib.Path, glob_pattern: str) -> bool:
    a = a.resolve()
    b = b.resolve()

    a_map = {}
    for file in a.glob(glob_pattern):
        a_map[str(file.relative_to(a))] = file.read_text()

    b_map = {}
    for file in b.glob(glob_pattern):
        b_map[str(file.relative_to(b))] = file.read_text()

    return a_map == b_map
