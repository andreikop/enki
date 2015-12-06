import os
import os.path

from enki.core.core import core

from enki.core.locator import AbstractCommand, AbstractCompleter, StatusCompleter


def fuzzyMatch(reversed_pattern, text):
    """Match text with pattern and return
        (score, list of matching indexes)
        or None

    Score is a summa or distances of continuos matched peaces from the end of the text.
    Less peaces -> better mathing
    Peaces close to the end -> better matching

    Reverse mathing is used because symbols at the end of the path are usually more impotant.

    pattern shall be already reversed for performance reasons
    """
    indexes = []
    score = 0
    text_len = len(text)

    index = text_len + 1
    prev_match = index
    for char in reversed_pattern:
        index = text.rfind(char, 0, index)
        if index == -1:
            return None, None

        indexes.append(index)
        if index + 1 != prev_match:
            score += text_len - index

        prev_match = index

    # find next /. Closer - better
    slash_index = text.rfind(os.sep, 0, index)
    if slash_index != -1:
        score += index - slash_index

    return score, indexes


class FuzzyOpenCompleter(AbstractCompleter):

    mustBeLoaded = True

    def __init__(self, pattern, files):
        smallerFont = core.mainWindow().font().pointSizeF() * 2 / 1.5
        self._itemTemplate = ('{{}}'
            '<div style="margin: 15px; font-size:{smallerFont}pt">{{}}</div>'.format(smallerFont=smallerFont))

        self._pattern = pattern
        self._files = files
        self._items = []

    def load(self, stopEvent):
        caseSensitive = any([c.isupper() for c in self._pattern])

        if not caseSensitive:
            self._pattern = self._pattern.lower()

        if self._pattern:
            if caseSensitive:
                pattern = self._pattern
                files = self._files
            else:
                pattern = self._pattern.lower()
                files = [f.lower() for f in self._files]

            reversed_pattern = pattern[::-1]

            matching = []
            for i, path in enumerate(files):
                score, indexes = fuzzyMatch(reversed_pattern, path)
                if indexes:
                    # Using original case path here
                    matching.append((self._files[i], score, indexes))

                if not (i % 100):
                    if stopEvent.is_set():
                        return

            matching.sort(key=lambda item: item[1])  # sort starting from minimal score
        else:
            matching = [(item, 0, []) for item in self._files]

        self._items = matching[:32]  # show not more than 32 items for better performance

    def rowCount(self):
        return len(self._items)

    def columnCount(self):
        return 1

    def text(self, row, column):
        path, score, indexes = self._items[row]
        basename = os.path.basename(path)
        chars = ['<span style="font-weight:900;">{}</span>'.format(char) if charIndex in indexes else char
                    for charIndex, char in enumerate(path)]
        pathFormatted = ''.join(chars)
        basenameFormatted = ''.join(chars[-len(basename):])
        return self._itemTemplate.format(basenameFormatted, pathFormatted)

    def autoSelectItem(self):
        return (0, 0)

    def getFullText(self, row):
        if self._items:
            return self._items[row][0]
        else:
            return None


class FuzzyOpenCommand(AbstractCommand):
    command = 'f'
    signature = '[f] PATH [LINE]'
    description = 'Open file in project. Fuzzy match the path'
    isDefaultCommand = True

    @staticmethod
    def isAvailable():
        return core.project().path() is not None

    def __init__(self):
        AbstractCommand.__init__(self)
        self._completer = None
        self._clickedPath = None

        core.project().filesReady.connect(self.updateCompleter)
        core.project().scanStatusChanged.connect(self.updateCompleter)
        if not core.project().isScanning():
            core.project().startLoadingFiles()
            self._iHaveStartedScan = True
        else:
            self._iHaveStartedScan = False

    def terminate(self):
        if self._iHaveStartedScan:
            core.project().cancelLoadingFiles()

        core.project().filesReady.disconnect(self.updateCompleter)
        core.project().scanStatusChanged.disconnect(self.updateCompleter)

    def setArgs(self, args):
        if len(args) > 1 and \
           all([c.isdigit() for c in args[-1]]):
            self._line = int(args[-1])
            del args[-1]
        else:
            self._line = None

        self._pattern = os.sep.join(args) if args else ''

    def completer(self):
        if core.project().files() is not None:
            return FuzzyOpenCompleter(self._pattern, core.project().files())
        else:
            return StatusCompleter("<i>{}</i>".format(core.project().scanStatus()))

    def onCompleterLoaded(self, completer):
        self._completer = completer

    def onItemClicked(self, fullText):
        self._clickedPath = fullText

    def lineEditText(self):
        return 'f ' + self._clickedPath

    def isReadyToExecute(self):
        return self._clickedPath is not None

    def execute(self):
        path = self._clickedPath
        fullPath = os.path.join(core.project().path(), path)
        if self._line is None:
            core.workspace().goTo(fullPath)
        else:
            core.workspace().goTo(fullPath, line=self._line - 1)


class ScanCommand(AbstractCommand):
    """Save As Locator command
    """
    command = 'scan'
    signature = 'scan'
    description = 'Scan (rescan) the project'

    @staticmethod
    def isAvailable():
        """Check if command is available.
        It is available, if at least one document is opened
        """
        return True

    def setArgs(self, args):
        if args:
            raise InvalidCmdArgs()

    def execute(self):
        core.project().startBackgroundScan()

