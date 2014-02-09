"""Ctags execution and output parsing functionality
"""

import os
import subprocess
import tempfile
from contextlib import contextmanager

from enki.core.core import core


class Tag:
    def __init__(self, type_, name, lineNumber, parent):
        self.type = type_
        self.name = name
        self.lineNumber = lineNumber
        self.parent = parent
        self.children = []

    def format(self, indentLevel=0):
        indent = '\t' * indentLevel
        formattedChildren = [child.format(indentLevel + 1) \
                                for child in self.children]
        result = '{}{} {}'.format(indent, self.lineNumber, self.name)
        if formattedChildren:
            result += '\n'
            result += '\n'.join(formattedChildren)

        return result


def _parseTag(line):
    items = line.split('\t')
    name = items[0]
    if len(items) == 5:
        type_ = items[-2]
        lineText = items[-1]
        scopeText = None
    else:
        type_ = items[-3]
        lineText = items[-2]
        scopeText = items[-1]

    # -1 to convert from human readable to machine numeration
    lineNumber = int(lineText.split(':')[-1]) - 1

    if scopeText:
        scopeParts = scopeText.split(':')
        scopeType = scopeParts[0]
        scopeName = scopeParts[-1].split('.')[-1]
    else:
        scopeType = None
        scopeName = None

    return name, lineNumber, type_, scopeType, scopeName

def _findScope(tag, scopeType, scopeName):
    """Check tag and its parents, if theirs name is scopeName.
    Return tag or None
    """
    if tag is None:
        return None
    if tag.name == scopeName and \
       tag.type == scopeType:
        return tag
    elif tag.parent is not None:
        return _findScope(tag.parent, scopeType, scopeName)
    else:
        return None

def _parseTags(text):
    ignoredTypes = ('variable')

    tags = []
    lastTag = None
    for line in text.splitlines():
        name, lineNumber, type_, scopeType, scopeName = _parseTag(line)
        if type_ not in ignoredTypes:
            parent = _findScope(lastTag, scopeType, scopeName)
            tag = Tag(type_, name, lineNumber, parent)
            if parent is not None:
                parent.children.append(tag)
            else:
                tags.append(tag)
            lastTag = tag

    return tags


# Workaround for tempfile.NamedTemporaryFile's behavior, which prevents Windows processes from accessing the file until it's deleted. Adapted from http://bugs.python.org/issue14243.
@contextmanager
def _namedTemp():
    f = tempfile.NamedTemporaryFile(delete=False)
    try:
        yield f
    finally:
        try:
            os.unlink(f.name)
        except OSError:
            pass


def processText(ctagsLang, text):
    ctagsPath = core.config()['Navigator']['CtagsPath']
    langArg = '--language-force={}'.format(ctagsLang)

    # \t is used as separator in ctags output. Avoid \t in tags text to simplify parsing
    # encode to utf8
    data = text.encode('utf8').replace('\t', '    ')

    if hasattr(subprocess, 'STARTUPINFO'):  # windows only
        # On Windows, subprocess will pop up a command window by default when run from
        # Pyinstaller with the --noconsole option. Avoid this distraction.
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so it will.
        env = os.environ
    else:
        si = None
        env = None

    with _namedTemp() as tempFile:
        tempFile.write(data)
        tempFile.close() # Windows compatibility

        try:
            # On Windows, running this from the binary produced by Pyinstller
            # with the --noconsole option requires redirecting everything
            # (stdin, stdout, stderr) to avoid a OSError exception
            # "[Error 6] the handle is invalid."
            popen = subprocess.Popen(
                    [ctagsPath, '-f', '-', '-u', '--fields=nKs', langArg, tempFile.name],
                    stdin=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdout=subprocess.PIPE,
                    startupinfo=si, env=env)
        except OSError as ex:
            return 'Failed to execute ctags console utility "{}": {}\n'\
                        .format(ctagsPath, str(ex)) + \
                   'Go to Settings -> Settings -> Navigator to set path to ctags'

        stdout, stderr = popen.communicate()

    return _parseTags(stdout)
