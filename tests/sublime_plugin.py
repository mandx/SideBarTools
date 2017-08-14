"""
Simple `sublime_plugin` mock module
"""

from sublime import Window


class ApplicationCommand:

    """
    Fake ``Applicationcommand`` class. Currently no functionality implemented.
    """


class EventListener:

    """
    Fake ``EventListener`` class. Currently no functionality implemented.
    """


class TextCommand:

    """
    Fake ``TextCommand`` class. Currently no functionality implemented.
    """


class WindowCommand:

    """
    Fake ``WindowCommand`` class. Currently no functionality implemented.
    """

    def __init__(self):
        self.window = Window()
