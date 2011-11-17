"""
config --- Load and save settings
=================================

MkS uses ConfigObj for store settings

ConfigObj is cool config file reader and writer. Home page and documentation:
http://www.voidspace.org.uk/python/configobj.html

Instance is accessible as: ::

    from mks.core.core import core
    core.config()

Created by :class:`mks.core.core.Core`
"""

from configobj import ConfigObj, flatten_errors, ParseError
from validate import Validator

class Config(ConfigObj):
    """Settings storage.
    
    Class extends ConfigObj with few methods, usefull for MkS
    
    There are 3 instances of this class currently (when the comment is being writen):
    
    * Main configuration file
    * QScintilla shortcuts
    * QScintilla leser settings
    
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
    
    def __init__(self, enableWriting, *args, **kwargs):
        """If enableWriting is True - object will write settings on flush(), if False - will do nothing
        """
        self.enableWriting = enableWriting
        # Open config file
        try:
            super(Config, self).__init__(default_encoding='utf8', encoding='utf8', *args, **kwargs)
        except ParseError, ex:
            exText = unicode(str(ex), 'utf8')
            messageString = u'Failed to parse configuration file %s. Error:\n' \
                             '%s\n' \
                             'Fix the file or delete it.' % (self.filename, exText)
            raise UserWarning(messageString)
        except IOError as ex:
            exText = unicode(str(ex), 'utf8')
            messageString = u'Failed to open configuration file %s\n' \
                             'Error: %s\n' % (self.filename, exText)
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
            message = u'Invalid configuration file %s\n' \
                       'Error:\n' \
                       '%s\n' \
                       'Fix the file or delete it.' % (self.filename, messageString)
            
            raise UserWarning(message)
    
    def reload(self):
        """Reload config from the disk
        
        TODO replace with file watcher
        """
        super(Config, self).reload()
        if self.configspec is not None:
            self._validate()

    def get(self, name):
        """
        Get option by slash-separated path. i.e. ::
        
            font = core.config().get("Editor/DefaultFont")
        """
        object_ = self
        path = name.split('/')
        while len(path):
            object_ = object_[path.pop(0)]
        return object_
    
    def set(self, name, value):
        """
        Set option by slash-separated path. i.e. ::
        
            core.config().get("Editor/DefaultFont") = font
        """
        section = self
        path = name.split('/')
        for sectionName in path[:-1]:
            if not sectionName in section:
                section[sectionName] = {}
            section = section[sectionName]
        section[path[-1]] = value

    def flush(self):
        """Flush config to the disk. 
        Does nothing, if *enableWriting* is *False* (probably default config is opened)
        """
        if self.enableWriting:
            try:
                self.write()
            except IOError as ex:
                exText = unicode(str(ex), 'utf8')
                message = u'Failed to write configuration file. Error:\n%s' % exText
                raise UserWarning(message)
