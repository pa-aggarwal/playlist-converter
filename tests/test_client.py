import unittest
from unittest.mock import patch, create_autospec
from string import ascii_letters, digits
from secrets import choice
import requests
from playlist_converter import client


CLIENT = "playlist_converter.client"
ALPHANUM = ascii_letters + digits

def random_string(length, characters=ALPHANUM) -> str:
    return "".join([choice(characters) for _ in range(length)])


class TestSpotifyClient(unittest.TestCase):
    """Test the methods of the SpotifyClient class."""

    @classmethod
    def setUpClass(cls):
        fake_token = random_string(220, ALPHANUM + "_-")
        cls.instance = client.SpotifyClient(fake_token, "sp_userid")
        cls.fake_tids = [random_string(23) for _ in range(5)]

    def setUp(self):
        auth_header = {"Authorization": "Bearer " + self.instance.access_token}
        self.request_args = {"headers": auth_header}
        patcher = patch(CLIENT + ".send_request")
        self.mock_request = patcher.start()
        self.addCleanup(patcher.stop)

    def update_request_args(self, **kwargs):
        self.request_args = {**self.request_args, **kwargs}

    def test_find_track_ids_request_helper(self):
        self.update_request_args(
            url=client.SEARCH_URL,
            params={"q": "foo artist:bar", "type": "track", "limit": 20})
        self.instance.find_track_ids("foo", "bar")
        self.mock_request.assert_called_once_with("GET", self.request_args)

    def test_find_track_ids_empty(self):
        self.mock_request.return_value = {"tracks": {"items": []}}
        self.assertFalse(self.instance.find_track_ids("foo", "bar"))

    def test_find_track_ids_nonempty(self):
        items = [{"id": _id} for _id in self.fake_tids]
        self.mock_request.return_value = {"tracks": {"items": items}}
        result_tids = self.instance.find_track_ids("foo", "bar")
        self.assertTrue(all(isinstance(tid, str) for tid in result_tids))
        self.assertListEqual(result_tids, self.fake_tids)

    def test_find_saved_track_request_helper(self):
        self.update_request_args(
            url=client.CONTAINS_URL,
            params={"ids": self.fake_tids})
        self.instance.find_saved_track(self.fake_tids)
        self.mock_request.assert_called_once_with("GET", self.request_args)

    @patch(CLIENT + ".first_saved", return_value=None)
    def test_find_saved_track_none(self, mock_first):
        expected_arg = [(tid, False) for tid in self.fake_tids]
        self.mock_request.return_value = [False] * len(self.fake_tids)
        self.assertIsNone(self.instance.find_saved_track(self.fake_tids))
        mock_first.assert_called_once_with(expected_arg)

    @patch(CLIENT + ".first_saved")
    def test_find_saved_track_found(self, mock_first):
        mock_first.return_value = self.fake_tids[0]
        self.mock_request.return_value = [True, False]
        expected_arg = [(self.fake_tids[0], True), (self.fake_tids[1], False)]
        saved_track = self.instance.find_saved_track(self.fake_tids[:2])
        self.assertEqual(saved_track, self.fake_tids[0])
        mock_first.assert_called_once_with(expected_arg)

    @patch(CLIENT + ".SpotifyClient.find_saved_track")
    @patch(CLIENT + ".SpotifyClient.find_track_ids")
    def test_get_track_id(self, mock_find_tracks, mock_find_saved):
        mock_find_tracks.return_value = []
        self.assertIsNone(self.instance.get_track_id("foo", "bar"))
        self.assertFalse(mock_find_saved.called)
        # No saved track found
        mock_find_tracks.return_value = self.fake_tids
        mock_find_saved.return_value = None
        result = self.instance.get_track_id("foo", "bar")
        self.assertEqual(result, self.fake_tids[0])
        mock_find_saved.assert_called_once_with(self.fake_tids)
        # Saved track was found
        mock_find_saved.return_value = self.fake_tids[4]
        result = self.instance.get_track_id("foo", "bar")
        self.assertEqual(result, self.fake_tids[4])

    @patch(CLIENT + ".dumps", return_value="pname")
    def test_create_playlist_send_request(self, mock_dumps):
        new_header = {"Content-Type": "application/json"}
        self.update_request_args(
            url=client.PLAYLIST_URL.format(self.instance.user_id),
            headers={**self.request_args["headers"], **new_header},
            data="pname")
        self.instance.create_playlist("pname")
        self.mock_request.assert_called_once_with("POST", self.request_args)
        mock_dumps.assert_called_once_with({"name": "pname"})

    def test_create_playlist_return_value(self):
        with patch(CLIENT + ".dumps"):
            self.mock_request.return_value = {"id": "abc"}
            self.assertEqual(self.instance.create_playlist("foo"), "abc")

    @patch(CLIENT + ".subsets_of_size", return_value=[["foo"]])
    @patch(CLIENT + ".dumps", return_value="foobar")
    def test_add_playlist_tracks_one_request(self, mock_dumps, _):
        new_header = {"Content-Type": "application/json"}
        self.update_request_args(
            url=client.ADD_TRACK_URL.format("bar"),
            headers={**self.request_args["headers"], **new_header},
            data="foobar")
        self.instance.add_playlist_tracks("bar", ["foo"])
        self.mock_request.assert_called_once_with("POST", self.request_args)
        mock_dumps.assert_called_once_with({"uris": ["foo"]})

    @patch(CLIENT + ".subsets_of_size", return_value=[["foo1"], ["foo2"]])
    @patch(CLIENT + ".dumps", return_value="foobar")
    def test_add_playlist_tracks_multiple_requests(self, mock_dumps, _):
        self.instance.add_playlist_tracks("bar", ["foo1", "foo2"])
        self.assertEqual(mock_dumps.call_count, 2)
        self.assertEqual(self.mock_request.call_count, 2)


class TestClientHelpers(unittest.TestCase):
    """Test the helper functions from the client module."""

    @patch(CLIENT + ".requests.request", autospec=True)
    def test_send_request_exception(self, mock_request):
        mock_response = create_autospec(spec=requests.Response)
        mock_response.raise_for_status.side_effect = requests.HTTPError
        mock_request.return_value = mock_response
        with self.assertRaises(requests.HTTPError):
            client.send_request("GET", {"url": "https://blah.com"})
        mock_request.assert_called_once_with("GET", url="https://blah.com")
        self.assertFalse(mock_response.json.called)

    @patch(CLIENT + ".requests.request", autospec=True)
    def test_send_request_successful(self, mock_request):
        mock_response = create_autospec(spec=requests.Response)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"data": "blah"}
        mock_request.return_value = mock_response
        result = client.send_request("POST", {"url": "https://foo.com"})
        self.assertEqual(result, {"data": "blah"})
        self.assertTrue(mock_response.raise_for_status.called)

    def test_first_saved(self):
        result = client.first_saved([("foo", False), ("bar", False)])
        self.assertIsNone(result)
        tracks_saved = [("foo", False), ("bar", True), ("a", True)]
        self.assertEqual(client.first_saved(tracks_saved), "bar")

    def test_subsets_of_size(self):
        result1 = client.subsets_of_size(["foo", "bar"], 2)
        result2 = client.subsets_of_size(["abc", "xyz", "123"], 2)
        self.assertEqual(result1, [["foo", "bar"]])
        self.assertEqual(result2, [["abc", "xyz"], ["123"]])


if __name__ == "__main__":
    unittest.main()
