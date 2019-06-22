import os

from pathlib import Path

STORAGE_ROOT = './storage/'


def abs_path(path, filename=None):
    storage_abs_path = Path('{}{}'.format(STORAGE_ROOT, path))
    storage_abs_path.mkdir(parents=True, exist_ok=True)

    if filename:
        return storage_abs_path.joinpath(Path(filename)).resolve()
    else:
        return storage_abs_path.resolve()


def list_files(abspath):
    return [f for f in os.listdir(abspath) if os.path.isfile(f'{abspath}/{f}')]
