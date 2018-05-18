# coding=utf8

"""
SideBarTools plugin commands
"""

from threading import Thread
import os
import shutil
from functools import partial

import sublime
import sublime_plugin


def with_trailing_path_sep(path):
    if path[-1] != os.path.sep:
        return path + os.path.sep
    return path


class SideBarCommand(sublime_plugin.WindowCommand):
    """
    Base class for all SideBarTools commands

    Groups common utilities and functionality in one place, to be reused elsewhere
    """

    def copy_to_clipboard_and_inform(self, data):
        """
        Copies the text in `data` to the OS clipboard,
        """
        sublime.set_clipboard(data)
        lines = len(data.split('\n'))
        self.window.status_message('Copied {} to clipboard'.format(
            '{} lines'.format(lines) if lines > 1 else '"{}"'.format(data)
        ))

    def get_path(self, paths):
        """
        Returns the first path in the `paths` argument, returning the current
        view's file name if the argument is empty
        """
        try:
            return paths[0]
        except IndexError:
            return self.window.active_view().file_name()

    def is_visible(self, paths):
        """
        Determines when this command is visible.
        """

        if paths:
            return len(paths) < 2
        return bool(self.window.active_view().file_name())

    @staticmethod
    def make_dirs_for(filename):
        """
        Attempts to create all necessary subdirectories for `filename`.
        """

        destination_dir = os.path.dirname(filename)
        try:
            os.makedirs(destination_dir)
            return True
        except OSError:
            return False

    @staticmethod
    def same_paths(path_a, path_b):
        """
        Simple utility method to check if two paths refer to the same location
        """
        return os.path.normcase(os.path.abspath(path_a)) == os.path.normcase(os.path.abspath(path_b))


class MultipleFilesMixin(object):

    def get_paths(self, paths):
        return paths or [self.get_path(paths)]

    def is_visible(self, paths):
        return bool(paths or self.window.active_view().file_name())


class SideBarCopyNameCommand(MultipleFilesMixin, SideBarCommand):
    """
    Command that copies the base name of the current view's file name.
    """

    def run(self, paths):
        """
        Called by Sublime when the command is invoked.

        Will set the clipboard to the base name of the current view's file
        """

        names = (os.path.split(_path)[1] for _path in self.get_paths(paths))
        self.copy_to_clipboard_and_inform('\n'.join(names))

    def description(self):
        """
        Default text to show in the menus
        """
        return 'Copy Filename'


class SideBarCopyAbsolutePathCommand(MultipleFilesMixin, SideBarCommand):
    """
    Command that copies the absolute path of the current view's file.
    """

    def run(self, paths):
        """
        Called by Sublime when the command is invoked

        Will set the clipboard to the absolute path of the current view's file
        """
        paths = self.get_paths(paths)
        self.copy_to_clipboard_and_inform('\n'.join(paths))

    def description(self):
        """
        Default text to show in the menus
        """
        return 'Copy Absolute Path'


class SideBarCopyRelativePathCommand(MultipleFilesMixin, SideBarCommand):
    """
    Command that copies the relative path of the current view's file,
    from the current project's root.
    """

    def run(self, paths):
        """
        Called by Sublime when the command is invoked

        Will set the clipboard to the absolute path of the current view's file
        """
        project_file_name = self.window.project_file_name()

        if project_file_name:
            root_dir = os.path.dirname(project_file_name)
        else:
            root_dir = self.window.project_data()['folders'][0]['path']

        root_dir = with_trailing_path_sep(root_dir)

        paths = self.get_paths(paths)
        relative_paths = []

        for path in paths:
            common = os.path.commonprefix([root_dir, path])

            if len(common) > 1:
                path = path[len(common):]

            relative_paths.append(path)

        self.copy_to_clipboard_and_inform('\n'.join(relative_paths))

    def description(self):
        """
        Default text to show in the menus
        """
        return 'Copy Relative Path'


class SideBarDuplicateCommand(SideBarCommand):
    """
    Command that copies/duplicates a file to a new destination. The destination
    can be anywhere, as long as Sublime has permission to write.
    """

    def run(self, paths):
        """
        Called by Sublime when the command is invoked

        Will ask the user for the final path of the duplicate. The actual copy
        is started inside the `on_done` callback.
        """
        source = self.get_path(paths)
        base, leaf = os.path.split(source)
        name, ext = os.path.splitext(leaf)

        if ext:
            while '.' in name:
                name, _ext = os.path.splitext(name)
                ext = _ext + ext
                if not _ext:
                    break

        initial_text = os.path.join(base, name + ' (Copy)' + ext)
        input_panel = self.window.show_input_panel(
            'Duplicate As:',
            initial_text,
            partial(self.on_done, source),
            None,
            None,
        )

        input_panel.sel().clear()
        input_panel.sel().add(
            sublime.Region(len(base) + 1, len(initial_text) - len(ext))
        )

    def on_done(self, source, destination):
        """
        Called by Sublime when the user is finished entering the duplicate's
        destination.

        The `destination` argument should be provided by Sublime, the `source`
        should come as a `partial` application.

        Will start a new thread in which the copy operation is actually done.
        """

        if self.same_paths(source, destination):
            self.window.status_message('Can\'t copy a file/directory into itself')
        else:
            Thread(target=self.copy, args=(source, destination)).start()

    def copy(self, source, destination):
        """
        Thread function, will simply use one of `shutil.copy*` functions to
        perform the copy.

        Uses `shutil.copytree` if the source is a directory, otherwise will use
        `shutil.copy2`.
        """

        self.window.status_message('Copying "{src}" to "{dst}"'.format(src=source, dst=destination))

        self.make_dirs_for(destination)

        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
                self.window.open_file(destination)
        except OSError as error:
            self.window.status_message(
                'Error copying: {error} ("{src}" to "{dst}")'.format(
                    src=source,
                    dst=destination,
                    error=error,
                )
            )

    def description(self):
        """
        Default text to show in the menus
        """
        return 'Duplicate File…'


class SideBarMoveCommand(SideBarCommand):
    """
    Command that moves a file to a new destination. The destination
    can be anywhere, as long as Sublime has permission to write.
    """

    def run(self, paths):
        """
        Called by Sublime when the command is invoked

        Will ask the user for the file's new path. The actual moving is
        started inside the `on_done` callback.
        """
        source = self.get_path(paths)

        input_panel = self.window.show_input_panel(
            'Move to:', source, partial(self.on_done, source), None, None)

        base, leaf = os.path.split(source)
        ext = os.path.splitext(leaf)[1]

        input_panel.sel().clear()
        input_panel.sel().add(
            sublime.Region(len(base) + 1, len(source) - len(ext)))

    def on_done(self, source, destination):
        """
        Called by Sublime when the user is finished entering the new destination.

        The `destination` argument should be provided by Sublime, the `source`
        should come as a `partial` application.

        Will start a new thread in which the move operation is actually done.
        """

        if self.same_paths(source, destination):
            self.window.status_message('Can\'t move a file/directory into itself')
        else:
            Thread(target=self.move, args=(source, destination)).start()

    @staticmethod
    def retarget_all_views(source, destination):
        """
        Iterates over all Sublime's views in all windows, checking which views
        need retargeting after a move operation.

        This function assumes `destination` path exists; that is, the move has
        already happened.
        """

        is_file_move = os.path.isfile(destination)

        source = with_trailing_path_sep(source)
        destination = with_trailing_path_sep(destination)

        for window in sublime.windows():
            for view in window.views():
                filename = view.file_name()

                if is_file_move:
                    if filename == source:
                        view.retarget(destination)
                else:
                    if os.path.commonprefix([source, filename]) == source:
                        view.retarget(os.path.join(destination, filename[len(source):]))

    def move(self, source, destination):
        """
        Thread function, will simply use `shutil.move` functions to
        `source` to `destination`.

        It will check if the destination's directory exists, and will
        attempt to create it if it doesn't exist (uses `os.makedirs`).
        """
        self.window.status_message('Moving "{src}" to "{dst}"'.format(src=source, dst=destination))

        self.make_dirs_for(destination)

        try:
            shutil.move(source, destination)
            self.retarget_all_views(source, destination)
        except OSError as error:
            self.window.status_message('Error moving: {error} ("{src}" to "{dst}")'.format(
                src=source,
                dst=destination,
                error=error,
            ))
        self.window.run_command('refresh_folder_list')

    def description(self):
        """
        Default text to show in the menus
        """
        return 'Move File…'


class SideBarNewCommand(SideBarCommand):
    """
    Command that creates a new, empty file in a user defined path.
    The path can be anywhere, as long as Sublime has permission to write.
    """
    NEW_FILENAME = 'New file.txt'

    def run(self, paths):
        """
        Called by Sublime when the command is invoked

        Will ask the user for the new file's path. The actual creation is
        started inside the `on_done` callback.
        """
        source = self.get_path(paths)

        base = source if os.path.isdir(source) else os.path.split(source)[0]
        new_filename = os.path.join(base, self.NEW_FILENAME)

        input_panel = self.window.show_input_panel(
            'New file\'s path:', new_filename, self.on_done, None, None)

        input_panel.sel().clear()
        input_panel.sel().add(sublime.Region(len(base) + 1, len(new_filename)))

    def on_done(self, filename):
        """
        Called by Sublime when the user is finished entering the new file name.

        Will start a new thread in which the create operation is actually done.
        """

        if filename.endswith(os.path.sep):
            self.window.status_message(
                'Filenames that end with "{sep}" are not allowed'.format(sep=os.path.sep))
        else:
            Thread(target=self.create_file, args=(filename,)).start()


    def create_file(self, filename):
        """
        Thread function, will simply use `open(filename, 'w')` to create an empty file.

        It will check if the destination's directory exists, and will
        attempt to create it if it doesn't exist (uses `os.makedirs`).
        """
        self.window.status_message('Creating "{filename}"'.format(filename=filename))

        if os.path.exists(filename):
            self.window.status_message('"{filename}" already exists'.format(filename=filename))
            return

        self.make_dirs_for(filename)

        try:
            with open(filename, 'wb') as fileobj:
                fileobj.write(b'')
            self.window.open_file(filename)
        except OSError as error:
            self.window.status_message(
                'Error creating "{filename}": {error}'.format(filename=filename, error=error),
            )

    def description(self):
        """
        Default text to show in the menus
        """
        return 'New File…'
