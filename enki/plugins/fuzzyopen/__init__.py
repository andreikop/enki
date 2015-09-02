import os.path

from PyQt4.QtGui import QApplication

from enki.core.core import core

from enki.core.locator import AbstractCommand, AbstractCompleter, InvalidCmdArgs


def fuzzyMatch(pattern, text):
    """Match text with pattern and return
        (score, list of matching indexes)
        or None

    Score is a summa or distances of continuos matched peaces from the end of the text.
    Less peaces -> better mathing
    Peaces close to the end -> better matching

    Reverse mathing is used because symbols at the end of the path are usually more impotant.
    """
    iter_text = reversed(list(enumerate(text)))
    indexes = []

    sequence_start_indexes = []

    prev_matched = False
    for pattern_char in reversed(pattern):
        for text_index, text_char in iter_text:
            if pattern_char == text_char:
                if not prev_matched:  # start of sequence of matched symbols
                    sequence_start_indexes.append(text_index)
                    prev_matched = True
                indexes.append(text_index)
                break
            else:
                prev_matched = False

        else:
            return None

    if indexes:
        score = sum([len(text) - index for index in sequence_start_indexes])
        return (score, indexes)
    else:
        return None


class FuzzyOpenCompleter(AbstractCompleter):
    def __init__(self, items):
        self._message = None
        self._items = items

        smallerFont = core.locator().font().pointSizeF() / 1.5
        self._itemTemplate = ('{{}}'
            '<div style="margin: 10px; font-size:{smallerFont}pt">{{}}</div>'.format(smallerFont=smallerFont))

    def rowCount(self):
        return len(self._items)

    def columnCount(self):
        return 1

    def text(self, row, column):
        if self._message:
            return self._message
        else:
            path, score, indexes = self._items[row]
            basename = os.path.basename(path)
            chars = ['<b>{}</b>'.format(char) if charIndex in indexes else char
                        for charIndex, char in enumerate(path)]
            pathFormatted = ''.join(chars)
            basenameFormatted = ''.join(chars[-len(basename):])
            return self._itemTemplate.format(basenameFormatted, pathFormatted)


class FuzzyOpenCommand(AbstractCommand):
    command = 'o'
    signature = 'o PATH [LINE]'
    description = 'Open file in project. Fuzzy match the path'
    isDefaultCommand = False

    @staticmethod
    def isAvailable():
        return core.project().path() is not None

    def __init__(self, args):
        if len(args) != 1:
            raise InvalidCmdArgs()

        pattern = args[0]
        if pattern:
            matching = []
            for path in core.project().files():
                res = fuzzyMatch(pattern, path)
                if res is not None:
                    score, indexes = res
                    matching.append((path, score, indexes))

            matching.sort(key=lambda item: item[1])  # sort starting from minimal score
        else:
            matching = [(item, 0, []) for item in core.project().files()]

        self._completer = FuzzyOpenCompleter(matching)

    def completer(self, argIndex):
        return self._completer

    def isReadyToExecute(self):
        return True

    def execute(self):
        pass


class Plugin:
    def __init__(self):
        core.locator().addCommandClass(FuzzyOpenCommand)

    def del_(self):
        core.locator().removeCommandClass(FuzzyOpenCommand)
