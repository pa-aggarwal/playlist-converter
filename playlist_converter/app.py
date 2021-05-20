import os
import sys
import configparser
from typing import Dict, List, Optional
from requests import RequestException, HTTPError
from .client import SpotifyClient
from .read_file import get_playlists, PlaylistFile


parser = configparser.ConfigParser
config_error_msg = "Something went wrong reading your config file...\n"

def show_error(message: str) -> None:
    sys.stderr.write("Error: {}\n".format(message))
    sys.stderr.flush()
    sys.exit(1)

def quote_each_word(words: List[str]) -> str:
    quote = lambda word: f"'{word}'"
    return ", ".join([quote(word) for word in words])

def get_config_path() -> Optional[str]:
    project_root = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(project_root, "config", "config.ini")
    if not os.path.exists(path):
        show_error("Required configuration file 'config.ini' not found")
    return path

def read_config(config_path: str) -> parser:
    config = configparser.ConfigParser()
    with open(config_path, "r") as config_file:
        config.read_file(config_file)
    return config

def get_config_values(config: parser) -> Optional[Dict[str, str]]:
    try:
        values = {
            "directory_path": config.get("FILE_INFO", "directory_path"),
            "data_order":     config.get("FILE_INFO", "data_order"),
            "data_delimiter": config.get("FILE_INFO", "data_delimiter"),
            "user_id":        config.get("API", "user_id"),
            "access_token":   config.get("API", "access_token")
        }
    except configparser.Error as error:
        show_error(config_error_msg + error.message)
    else:
        return values

def check_empty(mapping: Dict[str, str]) -> None:
    empty_keys = [key for key in mapping if not mapping[key]]
    if empty_keys:
        quoted = quote_each_word(empty_keys)
        custom_msg = "Missing values for key(s) {}".format(quoted)
        show_error(config_error_msg + custom_msg)

def check_data_order(data_order: str) -> None:
    allowed = ["track artist", "artist track"]
    if data_order not in allowed:
        quoted = quote_each_word(allowed)
        custom_msg = "Key 'data_order' must equal one of {}".format(quoted)
        show_error(config_error_msg + custom_msg)

def get_playlist_files(dir_path: str) -> Optional[List[PlaylistFile]]:
    try:
        playlist_files = get_playlists(dir_path)
    except (NotADirectoryError, FileNotFoundError) as error:
        custom_msg = "Something went wrong reading the directory path...\n"
        show_error(custom_msg + str(error))
    else:
        return playlist_files

def convert_files(
        playlist_files: List[PlaylistFile],
        client: SpotifyClient,
        delimiter: str,
        order: str
        ) -> None:
    for file in playlist_files:
        name = file.playlist_name()
        items = file.playlist_items(delimiter, order)
        try:
            client.make_playlist_with_tracks(name, items)
        except HTTPError:
            show_error("Failed due to an HTTP error")
        except RequestException as error:
            custom_msg = "A request exception occurred...\n"
            show_error(custom_msg + str(error))

def run_app():
    config_path = get_config_path()
    config = get_config_values(read_config(config_path))
    check_empty(config)
    check_data_order(config["data_order"])
    files = get_playlist_files(config["directory_path"])
    sp_client = SpotifyClient(config["access_token"], config["user_id"])
    delimiter, data_order = config["data_delimiter"], config["data_order"]
    convert_files(files, sp_client, delimiter, data_order)


if __name__ == "__main__":
    run_app()
