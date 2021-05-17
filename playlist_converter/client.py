from json import dumps
from typing import List, Tuple, Dict, Union, Any
import requests


SEARCH_URL = "https://api.spotify.com/v1/search"
CONTAINS_URL = "https://api.spotify.com/v1/me/tracks/contains"
PLAYLIST_URL = "https://api.spotify.com/v1/users/{}/playlists"
ADD_TRACK_URL = "https://api.spotify.com/v1/playlists/{}/tracks"

class SpotifyClient:
    """Client makes requests to the Spotify API to create a playlist."""

    def __init__(self, access_token: str, user_id: str):
        self.access_token = access_token
        self.user_id = user_id

    def find_track_ids(self, track: str, artist: str) -> List[str]:
        query = "{} artist:{}".format(track, artist)
        request_args = {
            "url": SEARCH_URL,
            "headers": {"Authorization": "Bearer " + self.access_token},
            "params": {"q": query, "type": "track", "limit": 20}
        }
        response_json = send_request("GET", request_args)
        tracks_found = response_json["tracks"]["items"]
        return [result["id"] for result in tracks_found]

    def find_saved_track(self, track_ids: List[str]) -> Union[str, None]:
        request_args = {
            "url": CONTAINS_URL,
            "headers": {"Authorization": "Bearer " + self.access_token},
            "params": {"ids": track_ids}
        }
        response_json = send_request("GET", request_args)
        return first_saved(list(zip(track_ids, response_json)))

    def get_track_id(self, track: str, artist: str) -> Union[str, None]:
        track_results = self.find_track_ids(track, artist)
        if not track_results:
            return None
        saved_track = self.find_saved_track(track_results)
        if not saved_track:
            return track_results[0]
        return saved_track

    def create_playlist(self, name: str) -> str:
        request_args = {
            "url": PLAYLIST_URL.format(self.user_id),
            "headers": {
                "Authorization": "Bearer " + self.access_token,
                "Content-Type": "application/json"
            },
            "data": dumps({"name": name})
        }
        response_json = send_request("POST", request_args)
        # Playlist ID used to add tracks to the playlist
        return response_json["id"]

    def add_playlist_tracks(self, pid: str, track_uris: List[str]) -> None:
        request_args = {
            "url": ADD_TRACK_URL.format(pid),
            "headers": {
                "Authorization": "Bearer " + self.access_token,
                "Content-Type": "application/json"
            }
        }
        # Maximum of 100 items per request
        subsets = subsets_of_size(track_uris, 100)
        for subset in subsets:
            request_body = {"uris": subset}
            request_args["data"] = dumps(request_body)
            send_request("POST", request_args)

    def make_playlist_with_tracks(
            self,
            playlist_name: str,
            tracks_with_artist: List[Tuple[str, str]]
        ) -> None:
        track_ids = [self.get_track_id(*pair) for pair in tracks_with_artist]
        track_uris = ["spotify:track:{}".format(tid) for tid in track_ids]
        if track_uris:
            playlist_id = self.create_playlist(playlist_name)
            self.add_playlist_tracks(playlist_id, track_uris)


def send_request(method: str, request_args: Dict) -> Any:
    response = requests.request(method, **request_args)
    response.raise_for_status()
    return response.json()

def first_saved(tracks_saved: List[Tuple[str, bool]]) -> Union[str, None]:
    for tid, saved in tracks_saved:
        if saved:
            return tid
    return None

def subsets_of_size(items: List, size: int) -> List[List]:
    subsets = []
    duplicate = list(items)
    while duplicate:
        subset = duplicate[:size]
        subsets.append(subset)
        duplicate = duplicate[size:]
    return subsets
