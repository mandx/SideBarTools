import pytest
from unittest.mock import patch, MagicMock

import sublime_plugin

# copy_to_clipboard_and_inform
# get_path
# is_visible
# make_dirs_for
# same_paths

from SideBar import SideBarCommand, MultipleFilesMixin


def test_class_hierarchy():
    # Right now the only way to assert that the command subclass
    # will have `self.window` available is by checking the superclass
    assert issubclass(SideBarCommand, sublime_plugin.WindowCommand)


@pytest.mark.parametrize('data,displayed', (
    ('some text', '"some text"'),
    ('some more text', '"some more text"'),
    ('here is more text', '"here is more text"'),
    ('some\ntext', '2 lines'),
    ('some\nmore\ntext', '3 lines'),
    ('here\nis\nmore\ntext', '4 lines'),
))
def test_clipboard_method(data, displayed):
    command = SideBarCommand()
    command.window = MagicMock()

    with patch('sublime.set_clipboard') as clipboard_stub:
        with patch.object(command.window, 'status_message', wraps=command.window.status_message) as status_message_stub:
            command.copy_to_clipboard_and_inform(data)
            clipboard_stub.assert_called_once_with(data)
            status_message_stub.assert_called_once_with('Copied {} to clipboard'.format(displayed))


@pytest.mark.parametrize('args,window_filename,expected', (
    (['a', 'b'], 'c', 'a'),
    ([], 'c', 'c'),
    (['a'], AssertionError, 'a'),
    pytest.param([], AssertionError, None, marks=pytest.mark.xfail(
        reason='Ensure the view\'s filename is used')),
))
def test_get_path_method(args, window_filename, expected):
    command = SideBarCommand()
    command.window = MagicMock()
    view = command.window.active_view.return_value = MagicMock()
    view.file_name.return_value = window_filename
    assert command.get_path(args) == expected


@pytest.mark.parametrize('args,window_filename,expected', (
    (['a', 'b', 'c', 'd'], 'e', False),
    (['a', 'b', 'c'], 'e', False),
    (['a', 'b'], 'e', False),
    (['a'], 'e', True),
    ([], 'e', True),
    ([], None, False),
    pytest.param([], AssertionError, None, marks=pytest.mark.xfail(
        reason='Ensure the view\'s filename is used')),
))
def test_is_visible_method(args, window_filename, expected):
    command = SideBarCommand()
    command.window = MagicMock()
    view = command.window.active_view.return_value = MagicMock()
    view.file_name.return_value = window_filename
    assert command.is_visible(args) == expected


@pytest.mark.parametrize('filename,directory,side_effect,expected', (
    ('/some/file/name', '/some/file', None, True),
    ('/some/file/name', '/some/file', OSError, False),
))
def test_make_dirs_for_method(filename, directory, side_effect, expected):
    command = SideBarCommand()
    with patch('os.makedirs', side_effect=side_effect) as makedirs_stub:
        assert command.make_dirs_for(filename) == expected
        makedirs_stub.assert_called_once_with(directory)


class MultipleFilesCommand(MultipleFilesMixin, SideBarCommand):
    """
    Test subclass
    """
    pass


@pytest.mark.parametrize('args,window_filename,expected', (
    (['a', 'b'], 'c', ['a', 'b']),
    ([], 'c', ['c']),
    (['a'], AssertionError, ['a']),
    pytest.param([], AssertionError, None, marks=pytest.mark.xfail(
        reason='Ensure the view\'s filename is used')),
))
def test_multiple_get_paths_method(args, window_filename, expected):
    command = MultipleFilesCommand()
    command.window = MagicMock()
    view = command.window.active_view.return_value = MagicMock()
    view.file_name.return_value = window_filename
    assert command.get_paths(args) == expected


@pytest.mark.parametrize('args,window_filename,expected', (
    (['a', 'b', 'c', 'd'], 'e', True),
    (['a', 'b', 'c'], 'e', True),
    (['a', 'b'], 'e', True),
    (['a'], 'e', True),
    ([], 'e', True),
    ([], None, False),
    pytest.param([], AssertionError, None, marks=pytest.mark.xfail(
        reason='Ensure the view\'s filename is used')),
))
def test_multiple_is_visible_method(args, window_filename, expected):
    command = MultipleFilesCommand()
    command.window = MagicMock()
    view = command.window.active_view.return_value = MagicMock()
    view.file_name.return_value = window_filename
    assert command.is_visible(args) == expected
