"""
config --- Load and save settings
=================================

MkS uses ConfigObj for store settings

ConfigObj is cool config file reader and writer. Home page and documentation:
http://www.voidspace.org.uk/python/configobj.html

instance is accessible as: ::

    from mks.core.core import core
    core.config()

Created by ::class:mks.core.core.Core
"""

from mks._3rdparty.configobj import ConfigObj, flatten_errors, ParseError
from mks._3rdparty.validate import Validator

class Config(ConfigObj):
    """Settings storage
    Class extends ConfigObj with few methods, usefull for MkS
    There are 3 instances of this class currently (when the comment is being writen):
    * Main configuration file
    * QScintilla shortcuts
    * QScintilla settings
    
    Use this object as a dictionary for read and write options.
    Example: ::
        font = core.config()["Editor"]["DefaultFont"]  # read option
        core.config()["Editor"]["DefaultFont"] = font  # write option
    
    You SHOULD flush config, when writing changed settings is finished.
    Example: ::
        core.config().flush()
    """
    
    def __init__(self, enableWriting, *args, **kwargs):
        """If enableWriting is True - object will write settings on flush(), if False - will do nothing
        """
        self.enableWriting = enableWriting
        # Open config file
        try:
            super(Config, self).__init__(*args, **kwargs)
        except ParseError, ex:
            messageString = 'Failed to parse configuration file %s\n' \
                            'Error:\n' \
                            '%s\n' \
                            'Fix the file or delete it.' % (self.filename, unicode(str(ex), 'utf_8'))
            raise UserWarning(messageString)
        
        if self.configspec is not None:
            self._validate()

    def _validate(self):
        """Validate opened config, raise UserWarning if it is invalid
        """
        validator = Validator()
        result = self.validate(validator, preserve_errors=True)
        if result is not True:
            messageString = ''
            for entry in flatten_errors(self, result):
                # each entry is a tuple
                sectionList, key, error = entry
                if key is not None:
                    sectionList.append(key)
                else:
                    sectionList.append('[missing section]')
                sectionString = ', '.join(sectionList)
                if error == False:
                    error = 'Missing value or section.'
                messageString += (sectionString + ' = ' + str(error) + '\n')
            raise UserWarning('Invalid configuration file '
                              '%s\n'
                              'Error:\n'
                              '%s\n'
                              'Fix the file or delete it.' % (self.filename, messageString))
    
    def reload(self):
        """Reload config from the disk
        
        TODO replace with file watcher
        """
        super(Config, self).reload()
        if self.configspec is not None:
            self._validate()

    def get(self, name):
        """Get option by slash-separated path
        """
        object = self
        path = name.split('/')
        while len(path):
            object = object[path.pop(0)]
        return object
    
    def set(self, name, value):
        """Set option by slash-separated path
        """
        object = self
        path = name.split('/')
        while len(path) > 1:
            object = object[path.pop(0)]
        object[path.pop(0)] = value

    def flush(self):
        """Flush config to the disk
        Does nothing, if enableWriting is False (probably default config is opened)
        """
        if self.enableWriting:
            self.write()
