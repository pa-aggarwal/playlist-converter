import unittest
from unittest import mock
from configparser import ConfigParser, NoSectionError, NoOptionError
from playlist_converter import app


class TestApp(unittest.TestCase):
    """Test all functions in the app module."""

    def setUp(self):
        self.patcher = mock.patch("playlist_converter.app.show_error")
        self.mock_error = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    @mock.patch("playlist_converter.app.sys")
    def test_show_error(self, mock_sys):
        self.patcher.stop()
        app.show_error("oops")
        mock_sys.stderr.write.assert_called_once_with("Error: oops\n")
        mock_sys.exit.assert_called_once_with(1)
        self.assertTrue(mock_sys.stderr.flush.called)

    def test_quote_each_word(self):
        result = app.quote_each_word(["foo", "bar"])
        self.assertEqual(result, "'foo', 'bar'")

    @mock.patch("playlist_converter.app.os.path")
    def test_get_config_path_failure(self, mock_path):
        mock_path.join.return_value = "foo/bar"
        mock_path.exists.return_value = False
        app.get_config_path()
        self.assertTrue(self.mock_error.called)

    @mock.patch("playlist_converter.app.os.path")
    def test_get_config_path_successful(self, mock_path):
        mock_path.join.return_value = "foo/bar"
        mock_path.exists.return_value = True
        result = app.get_config_path()
        mock_path.exists.assert_called_once_with("foo/bar")
        self.assertEqual(result, "foo/bar")

    @mock.patch("playlist_converter.app.configparser", autospec=True)
    def test_read_config(self, mock_parser):
        with mock.patch("builtins.open", mock.mock_open()) as mock_open:
            result = app.read_config("foo/bar")
        mock_open.assert_called_once_with("foo/bar", "r")
        parser_obj = mock_parser.ConfigParser.return_value
        self.assertTrue(parser_obj.read_file.called)
        self.assertIsInstance(result, ConfigParser)

    def config_values_error(self, parser, error, error_args):
        parser.get.side_effect = error(*error_args)
        app.get_config_values(parser)
        self.assertTrue(self.mock_error.called)

    def test_get_config_values_failure(self):
        parser = mock.create_autospec(ConfigParser)
        self.config_values_error(parser, NoSectionError, ["bar"])
        self.config_values_error(parser, NoOptionError, ["foo", "bar"])

    def test_get_config_values_successful(self):
        mock_parser_cls = mock.create_autospec(ConfigParser)
        mock_parser_cls.get.side_effect = ["foo"] * 5
        result = app.get_config_values(mock_parser_cls)
        self.assertEqual(mock_parser_cls.get.call_count, 5)
        self.assertEqual(len(result), 5)

    @mock.patch("playlist_converter.app.quote_each_word", return_value="'foo'")
    def test_check_empty_found(self, mock_quote):
        app.check_empty(dict(foo="", bar="blah"))
        mock_quote.assert_called_with(["foo"])
        self.assertTrue(self.mock_error.called)

    @mock.patch("playlist_converter.app.quote_each_word")
    def test_check_data_order_failure(self, mock_quote):
        mock_quote.return_value = "'track artist', 'artist track'"
        app.check_data_order("foo")
        self.assertTrue(self.mock_error.called)

    @mock.patch("playlist_converter.app.get_playlists")
    def test_get_playlist_files_failure(self, mock_get):
        for error in [NotADirectoryError, FileNotFoundError]:
            mock_get.side_effect = error
            app.get_playlist_files("foo/bar")
            self.assertTrue(self.mock_error.called)


if __name__ == "__main__":
    unittest.main()
