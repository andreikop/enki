"""
pathcompleter --- Path completer for Locator
============================================
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QFileSystemModel, QPalette, QStyle

import os
import os.path
import glob

from enki.lib.htmldelegate import htmlEscape
from enki.core.locator import AbstractCompleter
from enki.core.core import core


def makeSuitableCompleter(text):
    """Returns PathCompleter if text is normal path or GlobCompleter for glob
    """
    if '*' in text or '?' in text or '[' in text:
        return GlobCompleter(text)
    else:
        return PathCompleter(text)


class AbstractPathCompleter(AbstractCompleter):
    """Base class for PathCompleter and GlobCompleter
    """

    mustBeLoaded = True

    # global object. Reused by all completers
    _fsModel = QFileSystemModel()

    _ERROR = 'error'
    _HEADER = 'currentDir'
    _STATUS = 'status'
    _DIRECTORY = 'directory'
    _FILE = 'file'

    def __init__(self, text):
        self._originalText = text
        self._dirs = []
        self._files = []
        self._error = None
        self._status = None

        """hlamer: my first approach is making self._model static member of class. But, sometimes it
        returns incorrect icons. I really can't understand when and why.
        When it is private member of instance, it seems it works
        """
        self._model = None  # can't construct in the construtor, must be constructed in GUI thread

    @staticmethod
    def _filterHidden(paths):
        """Remove hidden and ignored files from the list
        """
        return [path for path in paths
                    if not os.path.basename(path).startswith('.') and
                        not core.fileFilter().regExp().match(path)]

    def _classifyRowIndex(self, row):
        """Get list item type and index by it's row
        """

        if self._error:
            assert row == 0
            return (self._ERROR, 0)

        if row == 0:
            return (self._HEADER, 0)

        row -= 1
        if self._status:
            if row == 0:
                return (self._STATUS, 0)
            row -= 1

        if row in range(len(self._dirs)):
            return (self._DIRECTORY, row)
        row -= len(self._dirs)

        if row in range(len(self._files)):
            return (self._FILE, row)

        assert False

    def _formatHeader(self, text):
        """Format current directory for show it in the list of completions
        """
        return '<font style="background-color: %s; color: %s">%s</font>' % \
                (QApplication.instance().palette().color(QPalette.Window).name(),
                 QApplication.instance().palette().color(QPalette.WindowText).name(),
                 htmlEscape(text))

    def rowCount(self):
        """Row count in the list of completions
        """
        if self._error:
            return 1
        else:
            count = 1  # current directory
            if self._status:
                count += 1
            count += len(self._dirs)
            count += len(self._files)
            return count

    def _iconForPath(self, path):
        """Get icon for file or directory path. Uses QFileSystemModel
        """
        if self._model is None:
            self._model = QFileSystemModel()

        index = self._model.index(path)
        return self._model.data(index, Qt.DecorationRole)

    def text(self, row, column):
        """Item text in the list of completions
        """
        rowType, index = self._classifyRowIndex(row)
        if rowType == self._ERROR:
            return '<font color=red>%s</font>' % htmlEscape(self._error)
        elif rowType == self._HEADER:
            return self._formatHeader(self._headerText())
        elif rowType == self._STATUS:
            return '<i>%s</i>' % htmlEscape(self._status)
        elif rowType == self._DIRECTORY:
            return self._formatPath(self._dirs[index], True)
        elif rowType == self._FILE:
            return self._formatPath(self._files[index], False)

    def icon(self, row, column):
        """Item icon in the list of completions
        """
        rowType, index = self._classifyRowIndex(row)
        if rowType == self._ERROR:
            return QApplication.instance().style().standardIcon(QStyle.SP_MessageBoxCritical)
        elif rowType == self._HEADER:
            return None
        elif rowType == self._STATUS:
            return None
        elif rowType == self._DIRECTORY:
            return self._iconForPath(self._dirs[index])
        elif rowType == self._FILE:
            return self._iconForPath(self._files[index])

    def isSelectable(self, row, column):
        rowType, index = self._classifyRowIndex(row)
        return rowType in (self._DIRECTORY, self._FILE)

    def getFullText(self, row):
        """User clicked a row. Get inline completion for this row
        """
        row -= 1  # skip current directory
        if row in range(len(self._dirs)):
            return self._dirs[row] + '/'
        else:
            row -= len(self._dirs)  # skip dirs
            if row in range(len(self._files)):
                return self._files[row]

        return None


class PathCompleter(AbstractPathCompleter):
    """Path completer for Locator. Supports globs

    Used by Open command
    """

    def __init__(self, text):
        AbstractPathCompleter.__init__(self, text)

    def load(self, stopEvent):
        enterredDir = os.path.dirname(self._originalText)
        enterredFile = os.path.basename(self._originalText)

        if enterredDir.startswith('/'):
            pass
        elif self._originalText.startswith('~'):
            enterredDir = os.path.expanduser(enterredDir)
        else:  # relative path
            relPath = os.path.join(os.path.curdir, enterredDir)
            try:
                enterredDir = os.path.abspath(relPath)
            except OSError:  # current directory have been deleted
                enterredDir = relPath

        self._path = os.path.normpath(enterredDir)
        if self._path != '/':
            self._path += '/'

        if not os.path.isdir(self._path):
            self._status = 'No directory %s' % self._path
            return

        try:
            filesAndDirs = os.listdir(self._path)
        except OSError, ex:
            self._error = unicode(str(ex), 'utf8')
            return

        if not filesAndDirs:
            self._status = 'Empty directory'
            return

        # filter matching
        variants = [path for path in filesAndDirs
                        if path.startswith(enterredFile)]

        notHiddenVariants = self._filterHidden(variants)
        """If list if not ignored (not hidden) variants is empty, we use list of
        hidden variants.
        Use case: user types path "~/.", dotfiles shall be visible and completed
        """
        if notHiddenVariants:
            variants = notHiddenVariants

        variants.sort()

        for variant in variants:
            absPath = os.path.join(self._path, variant)
            if os.path.isdir(absPath):
                self._dirs.append(absPath)
            else:
                self._files.append(absPath)

        if not self._dirs and not self._files:
            self._status = 'No matching files'

    def _headerText(self):
        """Get text, which shall be displayed on the header
        """
        return self._path.replace(os.sep, '/')

    def _formatPath(self, path, isDir):
        """Format file or directory for show it in the list of completions
        """
        path = os.path.basename(path)
        if isDir:
            path += '/'

        typedLen = self._lastTypedSegmentLength()
        typedLenPlusInline = typedLen + len(self.inline())
        return '<b>%s</b><font color="red">%s</font>%s' % \
            (htmlEscape(path[:typedLen]),
             htmlEscape(path[typedLen:typedLenPlusInline]),
             htmlEscape(path[typedLenPlusInline:]))

    def _lastTypedSegmentLength(self):
        """Length of path segment, typed by a user

        For /home/a/Docu _lastTypedSegmentLength() is len("Docu")
        """
        return len(os.path.split(self._originalText)[1])

    def _commonStart(self, a, b):
        """The longest common start of 2 string
        """
        for index, char in enumerate(a):
            if len(b) <= index or b[index] != char:
                return a[:index]
        return a

    def inline(self):
        """Inline completion. Displayed after the cursor
        """
        if self._error is not None:
            return None
        else:
            if self._dirs or self._files:
                dirs = [os.path.basename(dir) + '/' for dir in self._dirs]
                files = [os.path.basename(file) for file in self._files]
                commonPart = reduce(self._commonStart, dirs + files)
                return commonPart[self._lastTypedSegmentLength():]
            else:
                return ''


class GlobCompleter(AbstractPathCompleter):
    """Path completer for Locator. Supports globs, does not support inline completion

    Used by Open command
    """
    def __init__(self, text):
        AbstractPathCompleter.__init__(self, text)

    def load(self, stopEvent):
        variants = glob.iglob(os.path.expanduser(self._originalText) + '*')
        variants = self._filterHidden(variants)
        variants.sort()

        for path in sorted(variants):
            if os.path.isdir(path):
                self._dirs.append(path)
            else:
                self._files.append(path)

        if not self._dirs and not self._files:
            self._status = 'No matching files'

    def _formatPath(self, path, isDir):
        """GlobCompleter shows paths as is
        """
        return path

    def _headerText(self):
        """Get text, which shall be displayed on the header
        """
        return self._originalText
