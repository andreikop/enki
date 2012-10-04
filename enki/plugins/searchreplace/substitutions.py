"""Module contains makeSubstitutions() function, which is used by controller and threads
"""

def makeSubstitutions(regExp, replaceText, matchText):
    """Replace patterns like \n and \1 with symbols and matches
    """
    try:
        return regExp.sub(replaceText, matchText)
    except re.error, ex:
        message = unicode(str(ex), 'utf_8')
        message += r'. Probably <i>\group_index</i> used in replacement string, but such group not found. '\
                   r'Try to escape it: <i>\\group_index</i>'
        raise UserWarning(message)

