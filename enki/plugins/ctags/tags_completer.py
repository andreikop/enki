"""
tags_completer --- Completer for search and display tags
============================================
"""

from enki.core.locator import AbstractCompleter
from enki.core.core import core

class HidedField:
    SEPARATOR = ';\"'

class TagsCompleter(AbstractCompleter):
    """Class for fuzzy searching.
    It is base on finding Levenshtein distance
    """
    def __init__(self, fuzzy_word, words):
        """words - dict, where key is word, value - additional descriptions stored in list (one word may have more than one description)
        Compare its with typed (fuzzy_word) word.
        Prepare list for display results of matching in viewMode mode.
        """
        #   1. Check for correct type
        if fuzzy_word is None:
            return
        if not isinstance(fuzzy_word, unicode):
            return
        fuzzy_word = fuzzy_word.strip()
        self._fuzzy_word = fuzzy_word
        #   2. Find levenshteine distance for each word
        nearest_words = {}
        fuzzy_word = fuzzy_word.lower()
        for word in words.keys():
            lev_distance = self._levenshtein(fuzzy_word, word.lower())
            if nearest_words.has_key(lev_distance):
                nearest_words[lev_distance].append(word)
            else:
                nearest_words[lev_distance] = [word]
        #   3. Maximal number of distinct between original fuzzy_word and existed
        max_distance = len(self._fuzzy_word) / 2
        #   4. Prepare displayed list. In beginning it contain more precise matched words
        self._displayed_list = []
        for i in range(max_distance + 1):
            if not nearest_words.has_key(i):
                continue
            matched_words = nearest_words[i]
            matched_words.sort()
            for word in matched_words:
                for description in words[word]:
                    self._displayed_list.append([word, description])
    
    def rowCount(self):
        """Return len of _displayed_list list
        plus 1 (reserve row for header)
        """
        rows = len(self._displayed_list)
        rows += 1
        return rows
    
    def columnCount(self):
        """Column count for tree view.
        In first column displayed tags names.
        In second - tag address
        In third - file. which contain tag 
        """
        columns = 3
        return columns
    
    def text(self, row, column):
        """First row reserved for columns titles
        In each displayed word are highlighting matched symbols with
        typed word(_fuzzy_word)
        In second column displayed total count of occurrence each matched word or tag address
        """
        #   Columns titles
        if row == 0:
            if column == 0:
                return "Tags:"
            else:
                return "Place in document:"
        
        #   Highlighted(according to typed fuzzy word) existed words or tags
        if column == 0:
            word = (self._displayed_list[row - 1])[0]
            prescription = self._levenshtein(self._fuzzy_word.lower(), word.lower(), True)
            highlighted_word = ""
            for action in prescription:
                if action == 'M':
                    html_code = '<b>%s</b>' % word[0]
                else:
                    html_code = '<i>%s</i>' % word[0]
                highlighted_word += html_code
                word = word[1:]
            return highlighted_word
        
        #   Number of occurrences words or tag address
        if column == 1:
            tagAddress = (self._displayed_list[row - 1])[1][0]
            if tagAddress.isdigit():
                return tagAddress
            else:
                if tagAddress.startswith("/^"):
                    tagAddress = tagAddress[2 : ]
                else:
                    print __file__, "TagsCompleter::text Unusual tag address =", tagAddress
                if tagAddress.endswith('$/'):
                    tagAddress = tagAddress[ : -2]
                else:
                    print __file__, "TagsCompleter::text Unusual tag address =", tagAddress
                tagAddress.strip()
                return tagAddress
        
        if column == 2:
            return (self._displayed_list[row - 1])[1][1]
            
        return "-1"
    
    def icon(self, row, column):
        """Icon for TreeView item. Now doesn't used.
        """
        return None
    
    def inline(self):
        """Inline completion.
        If first displayed item matching with typed word - append to this word tail
        of displayed item
        """
        #print "TagsCompleter::inline", self._fuzzy_word
        if len(self._displayed_list) > 0:
            offer = self._displayed_list[0][0]
            if offer.startswith(self._fuzzy_word):
                tail = offer[len(self._fuzzy_word) : ]
                return tail
        return ""
    
    def getFullText(self, row):
        """Row had clicked by mouse.
        Return word from row of displayed list
        or, for tags, return tag and offset between duplicated tags, divided by ;"
        """
        #print "TagsCompleter::getFullText " + str(row)
        if row != 0:
            fullText = (self._displayed_list[row - 1])[0]
            offsetOfIdenticWords = 0
            row -= 1
            while row > 0:
                if fullText != (self._displayed_list[row - 1])[0]:
                    break
                offsetOfIdenticWords += 1
                row -= 1
            return fullText + HidedField.SEPARATOR + "%d" % offsetOfIdenticWords
            
        return ""

    def _levenshtein(self, fuzzy_word, existed_word, find_prescription = False):
        """Ordinary algorithm for finding Levenshtein distance
        http://muzhig.ru/levenstein-distance-python/
        """
        m, n = len(fuzzy_word), len(existed_word)
        if m > n:
            return None
        D = [range(n + 1)] + [[x + 1] + [None] * n for x in xrange(m)]
        for i in xrange(1, m + 1):
            for j in xrange(1, n + 1):
                if fuzzy_word[i - 1] == existed_word[j - 1]:
                    D[i][j] = D[i - 1][j - 1]
                else:
                    before_insert = D[i][j - 1]
                    before_delete = D[i - 1][j]
                    before_change = D[i - 1][j -1]
                    D[i][j] = min(before_insert, before_delete, before_change) + 1
        
        if not find_prescription:
            return D[m][m]
        
        prescription = [] # contain actions, which have to apply to fuzzy_word for convert it to existed_word
        # existed_word always equal or greater than fuzzy_word, therefore add actions "Insert"
        for i in xrange(n - m):
            prescription.append('I')
        i, j = m, m
        for x in xrange(m):
            insert = D[i][j-1]
            delete = D[i-1][j]
            match_or_replace = D[i-1][j-1]
            best_choice = min(insert, delete, match_or_replace)
            if best_choice == match_or_replace:
                if fuzzy_word[i - 1] == existed_word[j - 1]:
                    prescription.append('M')
                else: # replace
                    prescription.append('R')
                i -= 1
                j -= 1
            elif best_choice == insert:
                prescription.append('I')
                j -= 1
            elif best_choice == delete:
                prescription.append('D')
                i -= 1
        
        prescription.reverse()
        #print fuzzy_word, existed_word, prescription
        #for d in D:
        #    print d        
        return prescription

