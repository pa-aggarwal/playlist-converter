import os
from typing import List, Tuple, Union


class PlaylistFile:
    """File representation of a playlist."""

    def __init__(self, path: str, filename: str):
        self.path = path
        self.filename = filename
        self.lines = self.clean_lines()

    def clean_lines(self) -> List[str]:
        # Return the lines of this object's file stripped of whitespace.
        with open(self.path, "r") as f:
            lines = f.readlines()
        return [ln.strip() for ln in lines]

    def line_starts_with(self, prefix: str) -> Union[str, None]:
        # Return the first line beginning with prefix, or None.
        for ln in self.lines:
            if ln.lower().startswith(prefix):
                return ln
        return None

    def playlist_name(self) -> str:
        """Return this playlist's name on a specific line or the filename."""
        # Assumption: Line with playlist name begins with "name:"
        line = self.line_starts_with("name:")
        if not line:
            return self.filename
        colon_index = line.index(":")
        return line[colon_index + 1:].strip()

    def playlist_items(
            self,
            delimiter: str,
            order: str) -> List[Tuple[str, str]]:
        """Return a list of pairs of song names and their respective artist."""
        # Assumption: Track name and artists separated by delimiter
        # Assumption: order argument is "track artist" or "artist track"
        items = []
        track_index = order.split().index("track")
        artist_index = order.split().index("artist")
        for ln in self.lines:
            content = ln.split(delimiter)
            if len(content) < 2:
                continue
            track = content[track_index].strip()
            artist = content[artist_index].strip()
            items.append((track, artist))
        return items


def directory_files(path: str) -> List[str]:
    # Return the names of all files in a directory path
    filenames = []
    contents = os.listdir(path)
    for entry in contents:
        entry_path = os.path.join(path, entry)
        if os.path.isfile(entry_path):
            filenames.append(entry)
    return filenames

def filter_textfiles(filenames: List[str]) -> List[str]:
    # Return the names of all files with a .txt extension
    txtfile = lambda name: os.path.splitext(name)[1] == ".txt"
    return [fn for fn in filenames if txtfile(fn)]

def directory_textfiles(path: str) -> List[str]:
    # Return the names of all text files in a directory path
    if not os.path.isdir(path):
        raise NotADirectoryError('"{}" is not a directory.'.format(path))
    textfiles = filter_textfiles(directory_files(path))
    if not textfiles:
        message = '"{}" contains no textfiles'.format(path)
        raise FileNotFoundError(message)
    return textfiles

def get_playlists(directory_path: str) -> List[PlaylistFile]:
    """Return a list of PlaylistFile objects for each file to convert."""
    playlists = []
    textfiles = directory_textfiles(directory_path)
    for tf in textfiles:
        tf_path = os.path.join(directory_path, tf)
        tf_name = os.path.basename(tf_path)
        playlists.append(PlaylistFile(tf_path, tf_name))
    return playlists
