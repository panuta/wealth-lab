from pathlib import Path

STORAGE_ROOT = './storage/'


def abs_path(folders, filename):
    abs_folder = Path('{}{}'.format(STORAGE_ROOT, folders))
    abs_folder.mkdir(parents=True, exist_ok=True)
    return abs_folder.joinpath(Path(filename)).resolve()
