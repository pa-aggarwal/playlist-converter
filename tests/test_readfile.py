import unittest
from unittest import mock
from playlist_converter import readfile


@mock.patch("playlist_converter.readfile.os")
class TestDirectoryFunctions(unittest.TestCase):
    """Test functions in readfile.py that read directory contents."""

    @classmethod
    def setUpClass(cls):
        cls.listdir = ["subdir", "playlist.txt", "song.mp3"]

    def test_directory_files_none(self, mock_os):
        mock_os.listdir.return_value = []
        result = readfile.directory_files(".")
        self.assertFalse(mock_os.path.join.called)
        self.assertFalse(result)

    def test_directory_files_exist(self, mock_os):
        mock_os.listdir.return_value = self.listdir
        mock_os.path.isfile.side_effect = [False, True, True]
        result = readfile.directory_files(".")
        self.assertEqual(mock_os.path.isfile.call_count, 3)
        self.assertCountEqual(result, self.listdir[1:])

    def test_filter_textfiles_none(self, mock_os):
        result = readfile.filter_textfiles([])
        self.assertFalse(mock_os.path.splitext.called)
        self.assertFalse(result)

    def test_filter_textfiles_exist(self, mock_os):
        splitext_result = [("playlist", ".txt"), ("song", ".mp3")]
        mock_os.path.splitext.side_effect = splitext_result
        result = readfile.filter_textfiles(self.listdir[1:])
        self.assertEqual(result, [self.listdir[1]])

    def test_directory_textfiles_path(self, mock_os):
        mock_os.path.isdir.return_value = False
        with self.assertRaises(NotADirectoryError):
            readfile.directory_textfiles(".")

    def test_directory_textfiles_none(self, mock_os):
        mock_os.path.isdir.return_value = True
        func_target = "playlist_converter.readfile.filter_textfiles"
        with mock.patch(func_target) as mock_func:
            mock_func.return_value = []
            with self.assertRaises(FileNotFoundError):
                readfile.directory_textfiles(".")


if __name__ == "__main__":
    unittest.main()
