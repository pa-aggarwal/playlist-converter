import os
from typing import List, Tuple, Union


def directory_files(path: str) -> List[str]:
    filenames = []
    contents = os.listdir(path)
    for entry in contents:
        entry_path = os.path.join(path, entry)
        if os.path.isfile(entry_path):
            filenames.append(entry)
    return filenames

def filter_textfiles(filenames: List[str]) -> List[str]:
    txtfile = lambda name: os.path.splitext(name)[1] == ".txt"
    return [fn for fn in filenames if txtfile(fn)]

def directory_textfiles(path: str) -> List[str]:
    if not os.path.isdir(path):
        raise NotADirectoryError('"{}" is not a directory.'.format(path))
    textfiles = filter_textfiles(directory_files(path))
    if not textfiles:
        message = '"{}" contains no textfiles'.format(path)
        raise FileNotFoundError(message)
    return textfiles

