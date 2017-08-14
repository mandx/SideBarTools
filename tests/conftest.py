"""
conftest.py
"""

import sys
from os import path, remove
from shutil import copy2

import pytest

sys.path.insert(0, path.dirname(__file__))


@pytest.fixture(autouse=True, scope='session')
def copy_command_module():
    """
    Will attempt to copy `SideBar.py` from the parent directory into the current one,
    if there's no previous copy yet
    """
    module_original = path.abspath(path.join(path.dirname(__file__), '..', 'SideBar.py'))
    module_copy = path.join(path.dirname(__file__), 'SideBar.py')
    if not path.exists(module_copy):
        copy2(module_original, module_copy)
        delete_after = True
    else:
        delete_after = False
    yield
    if delete_after:
        remove(module_copy)
