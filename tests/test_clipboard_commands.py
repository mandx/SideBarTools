import pytest
from unittest.mock import patch, MagicMock


from SideBar import (
    SideBarCopyNameCommand,
    SideBarCopyAbsolutePathCommand,
    SideBarCopyRelativePathCommand,
)


@pytest.mark.parametrize('cls', (
    SideBarCopyNameCommand,
    SideBarCopyAbsolutePathCommand,
    SideBarCopyRelativePathCommand,
))
def test_description_method(cls):
    assert isinstance(cls().description(), str)


@pytest.mark.parametrize('paths,view_filename,clip_data,status_bar', (
    (
        ['/some/path/here'],
        '/file/being/edited',
        'here',
        '"here"',
    ),
    (
        ['/some/path/here', '/some/other/path/over-here'],
        '/file/being/edited',
        'here\nover-here',
        '2 lines',
    ),
    (
        ['/some/path/here', '/some/other/path/over-here', '/yet/another/file'],
        '/file/being/edited',
        'here\nover-here\nfile',
        '3 lines',
    ),
    (
        [],
        '/file/being/edited',
        'edited',
        '"edited"',
    ),
    pytest.param([], AssertionError, None, None, marks=pytest.mark.xfail(
        reason='Ensure the view\'s filename is used')),
))
def test_clipboard_copy_basename_method(paths, view_filename, clip_data, status_bar):
    command = SideBarCopyNameCommand()
    command.window = MagicMock()
    view = command.window.active_view.return_value = MagicMock()
    view.file_name.return_value = view_filename

    with patch('sublime.set_clipboard') as clipboard_stub:
        with patch.object(command.window, 'status_message', wraps=command.window.status_message) as status_message_stub:
            command.run(paths)
            clipboard_stub.assert_called_once_with(clip_data)
            status_message_stub.assert_called_once_with('Copied {} to clipboard'.format(status_bar))


@pytest.mark.parametrize('paths,view_filename,clip_data,status_bar', (
    (
        ['/some/path/here'],
        '/file/being/edited',
        '/some/path/here',
        '"/some/path/here"',
    ),
    (
        ['/some/path/here', '/some/other/path/over-here'],
        '/file/being/edited',
        '/some/path/here\n/some/other/path/over-here',
        '2 lines',
    ),
    (
        ['/some/path/here', '/some/other/path/over-here', '/yet/another/file'],
        '/file/being/edited',
        '/some/path/here\n/some/other/path/over-here\n/yet/another/file',
        '3 lines',
    ),
    (
        [],
        '/file/being/edited',
        '/file/being/edited',
        '"/file/being/edited"',
    ),
    pytest.param([], AssertionError, None, None, marks=pytest.mark.xfail(
        reason='Ensure the view\'s filename is used')),
))
def test_clipboard_copy_abs_path_method(paths, view_filename, clip_data, status_bar):
    command = SideBarCopyAbsolutePathCommand()
    command.window = MagicMock()
    view = command.window.active_view.return_value = MagicMock()
    view.file_name.return_value = view_filename

    with patch('sublime.set_clipboard') as clipboard_stub:
        with patch.object(command.window, 'status_message', wraps=command.window.status_message) as status_message_stub:
            command.run(paths)
            clipboard_stub.assert_called_once_with(clip_data)
            status_message_stub.assert_called_once_with('Copied {} to clipboard'.format(status_bar))


@pytest.mark.parametrize('proj_filename,proj_folder,paths,view_filename,clip_data,status_bar', (
    (
        '/home/project/test.sublime-project',
        '/home/not-in-use/',
        ['/some/path/here'],
        '/file/being/edited',
        '/some/path/here',
        '"/some/path/here"',
    ),
    (
        '/home/project/test.sublime-project',
        '/home/not-in-use/',
        ['/home/project/here'],
        '/file/being/edited',
        'here',
        '"here"',
    ),
    (
        '/home/project/test.sublime-project',
        '/home/not-in-use/',
        ['/home/project/here', '/home/project/path/over-here'],
        '/file/being/edited',
        'here\npath/over-here',
        '2 lines',
    ),
))
def test_clipboard_copy_relative_path_method(proj_filename, proj_folder, paths, view_filename, clip_data, status_bar):
    command = SideBarCopyRelativePathCommand()
    command.window = MagicMock()
    command.window.project_file_name.return_value = proj_filename
    command.window.project_data.return_value = {'folders': [{'path': proj_folder}]}
    view = command.window.active_view.return_value = MagicMock()
    view.file_name.return_value = view_filename

    with patch('sublime.set_clipboard') as clipboard_stub:
        with patch.object(command.window, 'status_message', wraps=command.window.status_message) as status_message_stub:
            command.run(paths)
            clipboard_stub.assert_called_once_with(clip_data)
            status_message_stub.assert_called_once_with('Copied {} to clipboard'.format(status_bar))
