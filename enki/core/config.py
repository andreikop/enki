"""
config --- Load and save settings
=================================
"""

from enki.core.core import core
import enki.core.json_wrapper

from PyQt4.QtGui import QApplication, QFont, QFontDatabase


class Config():
    """Settings storage.

    This class stores core settings. Plugins are also allowed to store its settings here.

    Instance is accessible as: ::

        from enki.core.core import core
        core.config()

    Created by :class:`enki.core.core.Core`

    Use this object as a dictionary for read and write options.
    Example: ::
        font = core.config()["Qutepart"]["DefaultFont"]  # read option
        core.config()["Qutepart"]["DefaultFont"] = font  # write option
    See also get() and set() methods

    You SHOULD flush config, when writing changed settings is finished.
    Example: ::
        core.config().flush()
    Usually flushing is done by :class:`enki.core.uisettings.UISettingsManager`
    """

    def __init__(self, enableWriting, filePath):
        """If enableWriting is False - flush() does nothing
        """
        self._enableWriting = enableWriting
        self._filePath = filePath
        self.reload()  # exceptions are ok, raise it to upper level

    def _updateVersion(self):
        """Update config version, if config is old
        """
        if not '_version' in self._data:
            self._data['_version'] = 1
            self._data['NegativeFileFilter'] = self._data['FileBrowser']['NegativeFilter']

        if self._data['_version'] == 1:
            self._data['Associations']['Markdown'] = { "FileName": [ "*.md", "*.markdown"], \
                                                       "FirstLine": [] }
            self._data['_version'] = 2

        if self._data['_version'] == 2:
            self._data["Editor"]["MonochromeSelectionForeground"] = True
            self._data['_version'] = 3

        if self._data['_version'] == 3:
            self._data['PlatformDefaultsHaveBeenSet'] = False
            self._data["Preview"] = {"Enabled": True,
                                     "JavaScriptEnabled": True}

            self._data['_version'] = 4

        if self._data['_version'] == 4:
            editor = self._data['Editor']
            self._data['Qutepart'] = {
                "Font": { "Family": editor['DefaultFont'],
                          "Size": editor['DefaultFontSize'] },
                "Indentation": {'UseTabs': editor['Indentation']['UseTabs'],
                                'Width': editor['Indentation']['Width'],
                                'AutoDetect': editor['Indentation']['AutoDetect'],
                               },
                "Edge": { 'Color': editor['Edge']['Color'],
                          'Column': editor['Edge']['Column'],
                          'Enabled': editor['Edge']['Enabled']
                        },
                "AutoCompletion": { 'Enabled': editor['AutoCompletion']['Enabled'],
                                    "Threshold": editor['AutoCompletion']['Threshold']
                                  },
                "Wrap": { 'Enabled': editor['Wrap']['Enabled'],
                          'Mode': 'WrapAtWord' if editor['Wrap']['Mode'] == "WrapWord" else "WrapAnywhere" },
                "EOL": editor["EOL"]
            }
            self._data['_version'] = 5

        if self._data['_version'] in (5, 6):
            self._data['Qutepart']['WhiteSpaceVisibility'] = {'Trailing': True, 'AnyIndentation': False}
            self._data['_version'] = 7

        if self._data['_version'] == 7:
            if not 'Preview' in self._data:  # should appear in version 4, but migration was broken in some versions
                self._data["Preview"] = {"Enabled": True,
                                         "JavaScriptEnabled": True}
            self._data['Preview']['Template'] = 'Default'
            self._data['_version'] = 8

        if self._data['_version'] == 8:
            self._data['Navigator'] = {'Enabled': True, 'CtagsPath': 'ctags'}
            self._data['_version'] = 9

        if self._data['_version'] == 9:
            self._data['Qutepart']['StripTrailingWhitespace'] = False
            self._data['_version'] = 10

        if self._data['_version'] == 10:
            self._data['Navigator']['SortAlphabetically'] = False
            self._data['_version'] = 11

        if self._data['_version'] == 11:
            self._data['OpenTerm'] = {'Term': ''}
            self._data['_version'] = 12

        if self._data['_version'] == 12:
            ws = self._data['Qutepart']['WhiteSpaceVisibility']
            ws['Incorrect'] = ws['Trailing']
            del ws['Trailing']
            ws['Any'] = ws['AnyIndentation']
            del ws['AnyIndentation']
            self._data['_version'] = 13

        if self._data['_version'] == 13:
            self._data['Lint'] = {'Python': {'Enabled': True,
                                             'Show': "all",
                                             'Path': "pylint"}
                                 }
            self._data['_version'] = 14

        if self._data['_version'] == 14:
            self._data['FileBrowser'] = {'LastPath': ''}
            self._data['_version'] = 15

        if self._data['_version'] == 15:
            self._data['Qutepart']['VimModeEnabled'] = False
            self._data['_version'] = 16

        if self._data['_version'] == 16:
            self._data['Lint']['Python']['Path'] = 'flake8'
            self._data['_version'] = 17

        if self._data['_version'] == 17:
            self._data['Lint']['Python']['IgnoredMessages'] = ''
            self._data['Lint']['Python']['MaxLineLength'] = 79
            self._data['_version'] = 18

    def _setPlatformDefaults(self):
        """Set default values, which depend on platform
        """

        """Monaco - old Mac font,
        Menlo - modern Mac font,
        Consolas - default font for Windows Vista+
        Lucida Console - on Windows XP
        Monospace - default for other platforms
        """
        fontFamilies = ("Menlo", "Monaco", "Monospace", "Consolas", "Lucida Console")
        availableFontFamilies = QFontDatabase().families()
        for fontFamily in fontFamilies:
            if fontFamily in availableFontFamilies:
                self._data['Qutepart']['Font']['Family'] = fontFamily
                break
        else:
            self._data['Qutepart']['Font']['Family'] = 'Monospace'

        self._data['Qutepart']['Font']['Size'] = max(QApplication.instance().font().pointSize(), 12)
        self._data['PlatformDefaultsHaveBeenSet'] = True

    def reload(self):
        """Reload config from the disk
        """
        self._data = self._load()  # exceptions are ok, raise it to upper level
        self._updateVersion()
        if not self._data['PlatformDefaultsHaveBeenSet']:
            self._setPlatformDefaults()

    def get(self, name):  # pylint: disable=W0221
        """
        Get option by slash-separated path. i.e. ::

            font = core.config().get("Editor/DefaultFont")

        Raises KeyError if not found
        """
        object_ = self._data
        path = name.split('/')
        while len(path):
            object_ = object_[path.pop(0)]
        return object_

    def set(self, name, value):
        """
        Set option by slash-separated path. i.e. ::

            core.config().get("Editor/DefaultFont") = font
        """
        section = self._data
        path = name.split('/')
        for sectionName in path[:-1]:
            if not sectionName in section:
                section[sectionName] = {}
            section = section[sectionName]
        section[path[-1]] = value

    def clear(self):
        """Clear the config
        """
        self._data = {}

    def flush(self):
        """Flush config to the disk.
        Does nothing, if *enableWriting* is *False* (probably default config is opened)
        """
        if self._enableWriting:
            enki.core.json_wrapper.dump(self._filePath, 'settings', self._data)

    def _load(self):
        """Load the config
        """
        data = enki.core.json_wrapper.load(self._filePath, 'settings', None)
        if data is not None:
            return data
        else:
            raise UserWarning()

    def __getitem__(self, key):
        """Python dictionary interface implementation
        """
        return self._data[key]

    def __setitem__(self, key, value):
        """Python dictionary interface implementation
        """
        self._data[key] = value

    def __contains__(self, key):
        """Python dictionary interface implementation
        """
        return key in self._data
