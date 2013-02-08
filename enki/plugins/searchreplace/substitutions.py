"""Module contains makeSubstitutions() function, which is used by controller and the threads
"""
import re

_seqReplacer = re.compile('\\\\.')

_escapeSequences = \
{  '\\': '\\',
  'a': '\a',
  'b': '\b',
  'f': '\f',
  'n': '\n',
  'r': '\r',
  't': '\t',}


def makeSubstitutions(replaceText, matchObject):
    """Replace patterns like \n and \1 with symbols and matches
    """
    def _replaceFunc(escapeMatchObject):
        char = escapeMatchObject.group(0)[1]
        if char in _escapeSequences:
            return _escapeSequences[char]
        elif char.isdigit():
            index = int(char)
            try:
                return matchObject.group(index)
            except IndexError:
                return escapeMatchObject.group(0)
        
        return escapeMatchObject.group(0)  # no any replacements, return original value

    return _seqReplacer.sub(_replaceFunc, replaceText)
