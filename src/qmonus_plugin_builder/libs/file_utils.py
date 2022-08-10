import pathlib


def open_file(file_path: pathlib.Path) -> str:
    with open(str(file_path.resolve()), 'r', encoding='utf-8') as f:
        text = f.read()
    return text


def create_file(file_path: pathlib.Path, data: str) -> None:
    if file_path.is_dir():
        raise ValueError("Failed to create file: '{}' is directory".format(str(file_path)))

    create_dir(dir_path=file_path.parent)

    with open(str(file_path.resolve()), 'w', encoding='utf-8', newline='\n') as f:
        f.write(data)


def create_dir(dir_path: pathlib.Path) -> None:
    if dir_path.is_file():
        raise ValueError("Failed to create directory: '{}' is file".format(str(dir_path)))
    dir_path.mkdir(parents=True, exist_ok=True)


def delete(path: pathlib.Path) -> None:
    if path.is_file():
        path.unlink()
    else:
        for child_path in path.glob('*'):
            delete(child_path)
        path.rmdir()


def delete_files_in_directory(dir_path: pathlib.Path) -> None:
    if dir_path.is_file():
        raise ValueError("Failed to delete files: '{}' is file".format(str(dir_path)))

    for child_path in dir_path.glob('*'):
        delete(child_path)
