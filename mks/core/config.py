"""
config --- Load and save settings
=================================
"""

import json


class Config():
    """Settings storage.
        
    This class stores core settings. Plugins are also allowed to store its settings here.

    Instance is accessible as: ::

        from mks.core.core import core
        core.config()

    Created by :class:`mks.core.core.Core`
    
    Use this object as a dictionary for read and write options.
    Example: ::
        font = core.config()["Editor"]["DefaultFont"]  # read option
        core.config()["Editor"]["DefaultFont"] = font  # write option
    See also get() and set() methods
    
    You SHOULD flush config, when writing changed settings is finished.
    Example: ::
        core.config().flush()
    Usually flushing is done by :class:`mks.core.uisettings.ModuleConfigurator`
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
    
    def reload(self):
        """Reload config from the disk
        """
        self._data = self._load()  # exceptions are ok, raise it to upper level
        self._updateVersion()

    def get(self, name):  # pylint: disable=W0221
        """
        Get option by slash-separated path. i.e. ::
        
            font = core.config().get("Editor/DefaultFont")
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
            try:
                with open(self._filePath, 'w') as f:
                    json.dump(self._data, f, sort_keys=True, indent=4)
            except (OSError, IOError), ex:
                error = unicode(str(ex), 'utf8')
                text = "Failed to save settings file '%s': %s" % (self._filePath, error)
                core.mainWindow().appendMessage(text)

    def _load(self):
        """Load the config
        """
        try:
            with open(self._filePath, 'r') as f:
                return json.load(f)
        except (OSError, IOError), ex:
            error = unicode(str(ex), 'utf8')
            text = "Failed to load settings file '%s': %s" % (self._filePath, error)
            core.mainWindow().appendMessage(text)
            raise ex

    def __getitem__(self, key):
        """Python dictionary interface implementation
        """
        return self._data[key]
    
    def __setitem__(self, key, value):
        """Python dictionary interface implementation
        """
        self._data[key] = value
