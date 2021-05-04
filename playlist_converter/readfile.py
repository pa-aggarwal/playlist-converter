import os
from typing import List, Tuple, Union


class PlaylistFile:
    """File representation of a playlist."""

    def __init__(self, path: str):
        self.path = path
        self.lines = self.clean_lines()

    def clean_lines(self) -> List[str]:
        with open(self.path, "r") as f:
            lines = f.readlines()
        return [ln.strip() for ln in lines]

    def line_starts_with(self, prefix: str) -> Union[str, None]:
        for ln in self.lines:
            if ln.lower().startswith(prefix):
                return ln
        return None

    def playlist_name(self) -> Union[str, None]:
        # Assumption: Line with playlist name begins with "name:"
        line = self.line_starts_with("name:")
        if not line:
            return None
        colon_index = line.index(":")
        return line[colon_index + 1:].strip()

    def playlist_items(self, delimiter: str) -> List[Tuple[str, str]]:
        items = []
        # Assumption: Track name and artists separated by delimiter
        for ln in self.lines:
            content = ln.split(delimiter)
            if len(content) >= 2:
                items.append((content[0].strip(), content[1].strip()))
        return items


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

def get_playlists(directory_path: str) -> List[PlaylistFile]:
    playlists = []
    textfiles = directory_textfiles(directory_path)
    for tf in textfiles:
        tf_path = os.path.join(directory_path, tf)
        playlists.append(PlaylistFile(tf_path))
    return playlists

