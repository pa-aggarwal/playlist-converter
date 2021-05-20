import unittest
from unittest import mock
from playlist_converter import read_file


READFILE = "playlist_converter.read_file"

@mock.patch(READFILE + ".os")
class TestDirectoryFunctions(unittest.TestCase):
    """Test functions in read_file.py that read directory contents."""

    @classmethod
    def setUpClass(cls):
        cls.listdir = ["subdir", "playlist.txt", "song.mp3"]

    def test_directory_files_none(self, mock_os):
        mock_os.listdir.return_value = []
        result = read_file.directory_files(".")
        self.assertFalse(mock_os.path.join.called)
        self.assertFalse(result)

    def test_directory_files_exist(self, mock_os):
        mock_os.listdir.return_value = self.listdir
        mock_os.path.isfile.side_effect = [False, True, True]
        result = read_file.directory_files(".")
        self.assertEqual(mock_os.path.isfile.call_count, 3)
        self.assertCountEqual(result, self.listdir[1:])

    def test_filter_textfiles_none(self, mock_os):
        result = read_file.filter_textfiles([])
        self.assertFalse(mock_os.path.splitext.called)
        self.assertFalse(result)

    def test_filter_textfiles_exist(self, mock_os):
        splitext_result = [("playlist", ".txt"), ("song", ".mp3")]
        mock_os.path.splitext.side_effect = splitext_result
        result = read_file.filter_textfiles(self.listdir[1:])
        self.assertEqual(result, [self.listdir[1]])

    def test_directory_textfiles_path(self, mock_os):
        mock_os.path.isdir.return_value = False
        with self.assertRaises(NotADirectoryError):
            read_file.directory_textfiles(".")

    def test_directory_textfiles_none(self, mock_os):
        mock_os.path.isdir.return_value = True
        func_target = READFILE + ".filter_textfiles"
        with mock.patch(func_target) as mock_func:
            mock_func.return_value = []
            with self.assertRaises(FileNotFoundError):
                read_file.directory_textfiles(".")


class TestPlaylistFile(unittest.TestCase):
    """Test methods and properties of PlaylistFile instances."""

    def setUp(self):
        self.song_lines = ["Track---Artist 1, Artist 2", "Track 2---Artist"]
        func_target = READFILE + ".PlaylistFile.clean_lines"
        self.patcher = mock.patch(func_target)
        self.mock_func = self.patcher.start()
        self.mock_func.return_value = self.song_lines
        self.instance = read_file.PlaylistFile("songs.txt", "songs.txt")

    def tearDown(self):
        self.patcher.stop()

    def test_constructor(self):
        self.assertIsInstance(self.instance, read_file.PlaylistFile)
        self.assertTrue(self.mock_func.called)
        self.assertEqual(self.instance.filename, "songs.txt")
        self.assertEqual(self.instance.lines, self.song_lines)

    def test_playlist_name(self):
        func_target = READFILE + ".PlaylistFile.line_starts_with"
        with mock.patch(func_target) as mock_line_start:
            mock_line_start.return_value = None
            filename = self.instance.filename
            self.assertEqual(self.instance.playlist_name(), filename)
            mock_line_start.return_value = "Name: My Playlist "
            self.assertEqual(self.instance.playlist_name(), "My Playlist")
            self.assertEqual(mock_line_start.call_count, 2)

    def test_playlist_items(self):
        result = self.instance.playlist_items("---", "track artist")
        self.assertEqual(len(result), 2)
        self.assertIn(("Track", "Artist 1, Artist 2"), result)
        self.assertIn(("Track 2", "Artist"), result)


if __name__ == "__main__":
    unittest.main()
