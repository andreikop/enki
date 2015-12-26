"""
json --- Utility functions for loading and saving JSON
======================================================

Enki uses JSON for storing settings.

This module is a wrapper around standard json module,
which catches and shows exceptions when loading and saving JSON files
"""

import os.path
import json
import sys

from enki.core.core import core


def load(filePath, dataName, defaultValue):
    """Try to load data from JSON file.
    If something goes wrong - shows warnings to user. But, not if file not exists.
    dataName used in error messages. i.e. 'cursor positions', 'file browser settings'
    defaultValue is returned, if file not exists or if failed to load and parse it
    """
    if not os.path.exists(filePath):
        return defaultValue

    try:
        with open(filePath, 'r') as openedFile:
            try:
                return json.load(openedFile)
            except Exception as ex:  # broken file?
                error = str(ex)
                text = "Failed to parse %s file '%s': %s" % (dataName, filePath, error)
                core.mainWindow().appendMessage(text)
                print(text, file=sys.stderr)
                return defaultValue
    except (OSError, IOError) as ex:
        error = str(ex)
        text = "Failed to load %s file '%s': %s" % (dataName, filePath, error)
        core.mainWindow().appendMessage(text)
        return defaultValue


def dump(filePath, dataName, data, showWarnings=True):
    """Try to save data to JSON file.
    Show exceptions on main window and print it, if something goes wrong
    """
    try:
        with open(filePath, 'w') as openedFile:
            json.dump(data, openedFile, sort_keys=True, indent=4)
    except (OSError, IOError) as ex:
        error = str(ex)
        text = "Failed to save %s to '%s': %s" % (dataName, filePath, error)
        if showWarnings and core.mainWindow() is not None:
            core.mainWindow().appendMessage(text)
        print(error, file=sys.stderr)
