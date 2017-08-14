# -*- coding: utf-8 -*-
"""
Simple `sublime` mock module
"""

from collections import Sequence
from threading import Thread
from time import sleep


def set_clipboard(data):
    assert isinstance(data, str)


class TimeoutThread(Thread):

    def __init__(self, callback, delay):
        self.callback = callback
        self.delay = delay
        super().__init__()

    def run(self):
        sleep(self.delay)
        self.callback()


def set_timeout(callback, delay):
    assert callable(callback)
    assert isinstance(delay, int)
    TimeoutThread(callback, delay).start()


def status_message(string):
    assert isinstance(string, str)


class Region:
    def __init__(self, a, b):
        super().__init__()
        self.start = self.a = a
        self.end = self.b = b


def windows():
    return []


class View:
    """
    Sublime's View class stub
    """

    @staticmethod
    def file_name():
        return '/fake/path.txt'

    @staticmethod
    def retarget(to):
        assert isinstance(to, str)


class Window:
    """
    Sublime's Window class stub
    """

    @staticmethod
    def status_message(message):
        """
        Show a message in the status bar.
        """
        assert isinstance(message, str)

    @staticmethod
    def active_view():
        """
        Returns the currently edited view.
        """
        return View()

    @staticmethod
    def project_file_name():
        """
        Returns name of the currently opened project file, if any.
        """
        return '/fake/path/project.sublime-project'

    @staticmethod
    def project_data():
        """
        Returns the project data associated with the current window.
        The data is in the same format as the contents of a .sublime-project file.
        """
        return {'folders': [{'path': '/fake/path'}]}

    @staticmethod
    def show_input_panel(caption, initial_text, on_done, on_change, on_cancel):
        """
        Shows the input panel, to collect a line of input from the user.
        `on_done` and `on_change`, if not `None`, should both be functions
        that expect a single string argument. `on_cancel` should be a
        function that expects no arguments. The view used for the input
        widget is returned.
        """
        assert isinstance(caption, str)
        assert isinstance(initial_text, str)
        assert (on_done is None) or callable(on_done)
        assert (on_change is None) or callable(on_change)
        assert (on_cancel is None) or callable(on_cancel)

    @staticmethod
    def open_file(file_name):
        assert isinstance(file_name, str)

    @staticmethod
    def run_command(command_name, arguments=None):
        assert isinstance(command_name, str)
        assert (arguments is None) or isinstance(arguments, Sequence)
