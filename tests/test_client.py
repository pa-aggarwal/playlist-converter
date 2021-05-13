import unittest
from unittest import mock
from string import ascii_letters, digits
from secrets import choice
from playlist_converter import client


MODULE = "playlist_converter.client"
ALPHANUM = ascii_letters + digits

def random_string(length, characters=ALPHANUM) -> str:
    return "".join([choice(characters) for _ in range(length)])


class TestSpotifyClient(unittest.TestCase):
    """Test the methods of the SpotifyClient class."""

    @classmethod
    def setUpClass(cls):
        fake_token = random_string(220, ALPHANUM + "_-")
        cls.instance = client.SpotifyClient(fake_token, "sp_userid")

    def setUp(self):
        auth_header = {"Authorization": "Bearer " + self.instance.access_token}
        self.request_args = {"headers": auth_header}

    @mock.patch(MODULE + ".send_request")
    def test_find_track_ids_request_helper(self, mock_helper):
        self.request_args.update({
            "url": client.SEARCH_URL,
            "params": {"q": "foo artist:bar", "type": "track", "limit": 20}
        })
        self.instance.find_track_ids("foo", "bar")
        mock_helper.assert_called_once_with("GET", self.request_args)

    def test_find_track_ids_empty(self):
        with mock.patch(MODULE + ".send_request") as mock_helper:
            mock_helper.return_value = {"tracks": {"items": []}}
            self.assertFalse(self.instance.find_track_ids("foo", "bar"))

    def test_find_track_ids_nonempty(self):
        fake_tids = [random_string(23) for _ in range(10)]
        fake_json = {"tracks": {"items": [{"id": _id} for _id in fake_tids]}}
        with mock.patch(MODULE + ".send_request") as mock_helper:
            mock_helper.return_value = fake_json
            result_tids = self.instance.find_track_ids("foo", "bar")
        self.assertEqual(len(result_tids), 10)
        self.assertTrue(all(isinstance(tid, str) for tid in fake_tids))
        self.assertListEqual(result_tids, fake_tids)

    @mock.patch(MODULE + ".send_request")
    def test_find_saved_track_request_helper(self, mock_helper):
        fake_tids = [random_string(23) for _ in range(8)]
        self.request_args.update(
            {"url": client.CONTAINS_URL, "params": {"ids": fake_tids}})
        self.instance.find_saved_track(fake_tids)
        mock_helper.assert_called_once_with("GET", self.request_args)

    @mock.patch(MODULE + ".first_saved")
    def test_find_saved_track_none(self, mock_first_helper):
        fake_tids = [random_string(23) for _ in range(5)]
        mock_first_helper.return_value = None
        expected_arg = [(tid, False) for tid in fake_tids]
        with mock.patch(MODULE + ".send_request") as mock_request:
            mock_request.return_value = [False] * 5
            self.assertIsNone(self.instance.find_saved_track(fake_tids))
        mock_first_helper.assert_called_once_with(expected_arg)

    @mock.patch(MODULE + ".first_saved")
    def test_find_saved_track_found(self, mock_first_helper):
        fake_tids = [random_string(23) for _ in range(2)]
        mock_first_helper.return_value = fake_tids[0]
        expected_arg = [(fake_tids[0], True), (fake_tids[1], False)]
        with mock.patch(MODULE + ".send_request") as mock_request:
            mock_request.return_value = [True, False]
            saved_track = self.instance.find_saved_track(fake_tids)
        self.assertEqual(saved_track, fake_tids[0])
        mock_first_helper.assert_called_once_with(expected_arg)

    @mock.patch(MODULE + ".SpotifyClient.find_saved_track")
    @mock.patch(MODULE + ".SpotifyClient.find_track_ids")
    def test_get_track_id(self, mock_find_tracks, mock_find_saved):
        mock_find_tracks.return_value = []
        self.assertIsNone(self.instance.get_track_id("foo", "bar"))
        self.assertFalse(mock_find_saved.called)
        # No saved track found
        fake_tids = [random_string(23) for _ in range(12)]
        mock_find_tracks.return_value = fake_tids
        mock_find_saved.return_value = None
        result = self.instance.get_track_id("foo", "bar")
        self.assertEqual(result, fake_tids[0])
        mock_find_saved.assert_called_once_with(fake_tids)
        # Saved track was found
        mock_find_saved.return_value = fake_tids[4]
        result = self.instance.get_track_id("foo", "bar")
        self.assertEqual(result, fake_tids[4])


if __name__ == "__main__":
    unittest.main()
