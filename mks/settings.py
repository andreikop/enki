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

class Config:
    """Settings storage
    """
    def __init__(self):
        # Create config file in the users home
        failed = False
        if not os.path.exists(_CONFIG_PATH):
            try:
                shutil.copyfile(_DEFAULT_CONFIG_PATH, _CONFIG_PATH)
            except IOError, ex:
                core.messageManager().appendMessage('Failed to create configuration file. Error' + 
                                                unicode(str(ex), 'utf_8') + 
                                                '\nUsing default configuration')
                failed = True
        
        # Open config file
        if not failed:
            try:
                self._config = ConfigObj(_CONFIG_PATH, configspec=_DEFAULT_CONFIG_SPEC_PATH)
            except ParseError, ex:
                core.messageManager().appendMessage('Failed to parse configuration file ' + 
                                                _CONFIG_PATH + 
                                                '\n Error:' + 
                                                unicode(str(ex), 'utf_8') + 
                                                '\n Fix the file or delete it.' + 
                                                '\nUsing default configuration')
                failed = True
            
            if not failed:
                message_string = self._validateConfig(self._config)
                if message_string:
                    core.messageManager().appendMessage('Invalid configuration file ' + 
                                                    _CONFIG_PATH + 
                                                    '\n Error:' + 
                                                    message_string + 
                                                    '\n Fix the file or delete it.' + 
                                                    '\nUsing default configuration')
                    failed = True
            
            # Open default, if failed to use config in the users home
            if failed:
                self._config = ConfigObj(_DEFAULT_CONFIG_PATH, configspec=_DEFAULT_CONFIG_SPEC_PATH)
                message_string = self._validateConfig(self._config)
                if message_string:
                    print message_string
                    assert not message_string  # default config MUST be valid

    # Validate config file
    def _validateConfig(self, config):
        message_string = ''
        validator = Validator()
        errors = self._config.validate(validator, preserve_errors=True)
        if errors:
            for entry in flatten_errors(config, errors):
                # each entry is a tuple
                section_list, key, error = entry
                if key is not None:
                   section_list.append(key)
                else:
                    section_list.append('[missing section]')
                section_string = ', '.join(section_list)
                if error == False:
                    error = 'Missing value or section.'
                message_string += (section_string + ' = ' + str(error))
        return message_string
    
    def _reloadConfig():
        """TMP functions, probably I should invent something better"""
        self._config.reload()

    def _flushConfig():
        """TMP functions, probably I should invent something better"""
        if self._config.filename != _DEFAULT_CONFIG_PATH:
            self._config.write()
