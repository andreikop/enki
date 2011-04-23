#!/usr/bin/env python

help = """Script helps to convert C/C++ sources to C/C++ -like Python sources.

It does few edit operations, for convert C/C++ to Python.
After it you must edit code manually, but, probably you would spend less time for it.

Utility Will make mistaces and Will not generate ready for use code, so, it won't help you, 
if you don't know C/C++ and Python

For better result, it is recomented to format your code to ANSI style before do conversion.

NOTE: NO ANY BACKUPS CREATED. YOU MAY PERMANENTLY CORRUPT YOR SOURCES!!!

Usage:
    cpptopython.py DIR|FILE
    cpptopython.py -v|--version|-h|--help

When directory given - tries to find source files by C/C++ suffixes, when file name given - processes given file

Author: Andrei Kopats <hlamer@tut.by>
"""

import sys
import os.path
import re

def is_source(filename):
    suffixes = ('.cpp', '.c', '.cxx', '.c++', '.cc', '.h', '.hpp', '.hxx', '.h++')
    for s in suffixes:
        if filename.endswith(s):
            return True
    return False

def process_line(line):
        
    """ remove semicolons
        
        codecode(param, param);
                V
        codecode(param, param)
    """
    line = re.sub(';$', '', line) # remove semicolon from the end of line
    
    """ remove strings containing opening bracket
    
        if (blabla)
        {
            codecode
              V
        if (blabla)
            codecode
    """
    line = re.sub('\s*{\n$', '', line) 
    
    """ remove closing brackets. Empty line preserved
    
        if (blabla)
        {
            codecode
              V
        if (blabla)
            codecode
    """
    line = re.sub('\s*}$', '', line) 
    
    """ replace inline comment sign
    
        // here is comment
              V
        # here is comment
    """
    line = re.sub('//', '#', line) 
    
    """ replace /* comment sign
    
        /* here is comment
              V
        ''' here is comment
    """
    line = re.sub('/\*', "'''", line) 
    
    """ replace */ comment sign
    
        here is comment */
              V
        here is comment '''
    """
    line = re.sub('\*/', "'''", line) 
    
    """ replace '||' with 'or'
    
        boolvar || anotherboolvar
              V
        boolvar or anotherboolvar
    """
    line = re.sub('\|\|', 'or', line) 
    
    """ replace '&&' with 'and'
    
        boolvar && anotherboolvar
              V
        boolvar and anotherboolvar
    """
    line = re.sub('&&', 'and', line) 
    
    """ replace '!' with 'not '
    
        if !boolvar
              V
        if not boolvar
    """
    line = re.sub('!([^=\n])', 'not \\1', line) 
    
    """ replace '->' with '.'
    
        object->method()
              V
        object.method()
    """
    line = re.sub('->', '.', line) 
        
    """ replace 'false' with 'False'
    
        b = false
              V
        b = False
    """
    line = re.sub('false', 'False', line) 
    
    """ replace 'true' with 'True'
    
        b = true
              V
        b = True
    """
    line = re.sub('true', 'True', line) 
    
    """ remove "const" word from the middle of string
    
        const int result = a.exec();
              V
        int result = a.exec();
    """
    line = re.sub('const ', ' ', line)
    
    """ remove "const" word from the end of string
    
        const int result = a.exec();
              V
        int result = a.exec();
    """
    line = re.sub(' const$', '', line)
    
    """ remove brackets around if statement and add colon
    
        if (i = 4)
              V
        if i = 4:
    """
    line = re.sub('if\s*\((.*)\)$', 'if \\1:', line)
    
    """ remove brackets around if statement and add colon
    
        if (i = 4)
              V
        if i = 4:
    """
    line = re.sub('if\s*\((.*)\)$', 'if \\1:', line)
    #return line
    
    """ remove type from method definition and add a colon and "def"
    
        -bool pMonkeyStudio::isSameFile( const QString& left, const QString& right )
        +pMonkeyStudio::isSameFile( const QString& left, const QString& right ):
    """
    line = re.sub('^[\w:&<>\*]+\s+([\w:]+)\(([^\)]*\))$', 'def \\1(self, \\2:', line)
    
    """ after previous replacement fix "(self, )" to "(self)"
    
        -def internal_projectCustomActionTriggered(self, ):
        +def internal_projectCustomActionTriggered(self):
    """
    line = re.sub('\(\s*self,\s*\)', '(self)', line)
    
    """ remove type name from function parameters (second and farther)
    
        -def internal_currentProjectChanged(self,  XUPProjectItem* currentProject, XUPProjectItem* previousProject ):
        +def internal_currentProjectChanged(self,  currentProject, previousProject ):
    """
    line = re.sub(',\s*[\w\d:&\*<>]+\s+([\w\d:&\*]+)', ', \\1', line)
    
    """ remove type name from variable declaration and initialisation
        -pAbstractChild* document = currentDocument()
        +document = currentDocument()
    """
    line = re.sub('[\w\d:&\*]+\s+([\w\d]+)\s*= ', '\\1 = ', line)
    
    """ remove class name from method definition
    
        -pMonkeyStudio::isSameFile( const QString& left, const QString& right ):
        +pMonkeyStudio::isSameFile( const QString& left, const QString& right ):
    """
    line = re.sub('^def [\w\d]+::([\w\d]+\([^\)]*\):)$', 'def \\1', line)
    
    """ replace '::' with '.'
    
        YourNameSpace::YourFunction(bla, bla)
              V
        YourNameSpace.YourFunction(bla, bla)
    """
    line = re.sub('::', '.', line) 
    
    """ replace 'else if' with 'elif'
    
        else if (blabla)
              V
        elif (blabla)
    """
    line = re.sub('else\s+if', 'elif', line) 
    
    """ replace 'else' with 'else:'
        if blabala:
            pass
        else
            pass
              V
        if blabala:
            pass
        else:
            pass
    """
    line = re.sub('else\s*$', 'else:\n', line)
    
    """ Remove "new" keyword
        -i = new Class
        +i = Class
    """
    line = re.sub(' new ', ' ', line)
    
    """ Replace "this" with "self"
        -p = SomeClass(this)
        +p = SomeClass(self)
    """
    line = re.sub('([^\w])this([^\w])', '\\1self\\2', line)
    
    """ Replace Qt foreach macro with Python for
        -foreach ( QMdiSubWindow* window, a.subWindowList() )
        +foreach ( QMdiSubWindow* window, a.subWindowList() )
    """
    line = re.sub('foreach\s*\(\s*[\w\d:&\*]+\s+([\w\d]+)\s*,\s*([\w\d\.\(\)]+)\s*\)', 'for \\1 in \\2:', line)
    
    """ Replace Qt signal emit statement
        -emit signalName(param, param)
        +signalName.emit(param, param)
    """
    line = re.sub('emit ([\w\d]+)', '\\1.emit', line)
    
    """ Replace Qt connect call
        -connect( combo, SIGNAL( activated( int ) ), self, SLOT( comboBox_activated( int ) ) )
        +combo.activated.connect(self.comboBox_activated)
    """
    line = re.sub('connect\s*\(\s*([^,]+)\s*,\s*' + \
                'SIGNAL\s*\(\s*([\w\d]+)[^\)]+\)\s*\)\s*,'+ \
                '\s*([^,]+)\s*,\s*' + \
                'S[A-Z]+\s*\(\s*([\w\d]+)[^\)]+\)\s*\)\s*\)',
              '\\1.\\2.connect(\\3.\\4)', line)
    
    return line

def process_file(filename):
    with open(filename, 'rw+') as file:
        lines = file.readlines()  # probably would die on sources more than 100 000 lines :D 
        file.seek(0)
        file.truncate(0)
        for line in lines:
            file.write(process_line(line))


if __name__ == '__main__':
    if '--help' in sys.argv or \
       '-h' in sys.argv or \
       '--version' in sys.argv or \
       '-v' in sys.argv:
        print help
        sys.exit(0)
    if len (sys.argv) != 2:
        print >> sys.stderr, 'Invalid parameters count. Must be 1'
        print help
        sys.exit(-1)
    if os.path.isdir(sys.argv[1]):
        for root, dirs, files in os.walk(sys.argv[1]):
            for file in files:
                filename = root + '/' + file
                if is_source(filename):
                    process_file(filename)
    elif os.path.isfile(sys.argv[1]):
        process_file(sys.argv[1])
    else:
        print >> sys.stderr, 'Not a file or directory', sys.argv[1]
        sys.exit(-1)
