"""
settings --- Load, store and save settings
==========================================

MkS uses ConfigObj for store settings

ConfigObj is cool config file reader and writer. Home page and documentation:
http://www.voidspace.org.uk/python/configobj.html

Instance accessible as: ::

    core.workspace()

First time created by ::class:mks.monkeycore.Core
"""

import shutil
import os.path

from _3rdparty.configobj import ConfigObj, flatten_errors, ParseError
from _3rdparty.validate import Validator

from mks.monkeycore import core, DATA_FILES_PATH

_DEFAULT_CONFIG_PATH = os.path.join(DATA_FILES_PATH, 'config/mksv3.default.cfg')
_DEFAULT_CONFIG_SPEC_PATH = os.path.join(DATA_FILES_PATH, 'config/mksv3.spec.cfg')
_CONFIG_PATH = os.path.expanduser('~/.mksv3.cfg')

def _defaultConfig():
    config = ConfigObj(_DEFAULT_CONFIG_PATH, configspec=_DEFAULT_CONFIG_SPEC_PATH)
    message_string = config._validate()
    if message_string:
        print message_string
        assert not message_string  # default config MUST be valid

def createConfig():
    """Open config file and return Config instance
    
    Function creates config file in user's home directory, if necessary,
    validates and opens it.
    """
    try:
        # Create config file in the users home
        if not os.path.exists(_CONFIG_PATH):
            try:
                shutil.copyfile(_DEFAULT_CONFIG_PATH, _CONFIG_PATH)
            except IOError, ex:
                raise UserWarning('Failed to create configuration file. Error:\n' + 
                                  unicode(str(ex), 'utf_8'))
        # Open config file
        try:
            config = Config(_CONFIG_PATH, configspec=_DEFAULT_CONFIG_SPEC_PATH)
        except ParseError, ex:
            raise UserWarning('Failed to parse configuration file %s\n'
                              'Error:\n'
                              '%s\n'
                              'Fix the file or delete it.' % (_CONFIG_PATH, unicode(str(ex), 'utf_8')))
        config._validate()
    except UserWarning, ex:
        messageString = unicode(str(ex)) + '\n' + 'Using default configuration'
        core.messageManager().appendMessage(messageString)
        
        config = Config(_DEFAULT_CONFIG_PATH, configspec=_DEFAULT_CONFIG_SPEC_PATH)
        config._validate()
    return config

class Config(ConfigObj):
    """Settings storage
    
    Use this object as a dictionary for read and write options.
    Example:
        font = core.config()["Editor"]["DefaultFont"]  # read option
        core.config()["Editor"]["DefaultFont"] = font  # write option
    You SHOULD flush config, when writing changed settings finished.
    """
    # Validate config file
    def _validate(self):
        validator = Validator()
        errors = self.validate(validator, preserve_errors=True)
        if errors:
            messageString = ''
            for entry in flatten_errors(self, errors):
                # each entry is a tuple
                sectionList, key, error = entry
                if key is not None:
                   sectionList.append(key)
                else:
                    sectionList.append('[missing section]')
                sectionString = ', '.join(section_list)
                if error == False:
                    error = 'Missing value or section.'
                messageString += (sectionString + ' = ' + str(error))
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

    def flush(self):
        """Flush config to the disk
        Does nothing, if default config opened (failed to create config in users home directory)
        """
        if self.filename != _DEFAULT_CONFIG_PATH:
            self.write()
