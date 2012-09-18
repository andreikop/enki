"""
fuzzycompleter --- Fuzzy completer for Locator
============================================
"""

from enki.core.locator import AbstractCompleter
from enki.core.core import core

class FuzzySearchCompleter(AbstractCompleter):
    """Class for fuzzy searching.
    It is base on finding Levenshtein distance
    """
    def __init__(self, fuzzy_word):
        """Retrieve all words(correct C/C++ names of identificators) from current document.
        Compare its with typed (fuzzy_word) word.
        Prepare list for display results of matching.
        """
        import re
        #   1. Check for correct type
        if fuzzy_word is None:
            return
        if not isinstance(fuzzy_word, unicode):
            return
        fuzzy_word = fuzzy_word.strip()
        if len(fuzzy_word) < 1:
            return
        self._fuzzy_word = fuzzy_word.lower()
        #   2. Retrieve unique words from document
        full_text = core.workspace().currentDocument().text()
        words = re.findall(r"\b([a-zA-Z]\w*)\b", full_text, re.I);
        word_occurrence = {} # key: unique word, value: count of occurance this word in document
        for word in words:
            word_occurrence[word] = word_occurrence.get(word, 0) + 1
        #   3. Find levenshteine distance for each word
        nearest_words = {}
        for word in word_occurrence.keys():
            lev_distance = self._levenshtein(self._fuzzy_word, word.lower())
            if nearest_words.has_key(lev_distance):
                nearest_words[lev_distance].append(word)
            else:
                nearest_words[lev_distance] = [word]
        #   4. Maximal number of distinct between original fuzzy_word and existed
        max_distance = len(self._fuzzy_word) / 2
        #   5. Prepare displayed list. In beginning it contain more precise matched words
        self._displayed_list = []
        for i in range(max_distance + 1):
            if not nearest_words.has_key(i):
                continue
            matched_words = nearest_words[i]
            matched_words.sort()
            for word in matched_words:
                self._displayed_list.append([word, word_occurrence[word]])
    
    def rowCount(self):
        """Return len of _displayed_list list
        plus 1 (reserve row for header)
        """
        rows = len(self._displayed_list)
        rows += 1
        return rows
    
    def columnCount(self):
        """Column count for tree view.
        In first column displayed search results.
        In second - total count of occurrence each matched word
        """
        columns = 2
        return columns
    
    def text(self, row, column):
        """First row reserved for columns titles
        In each displayed word are highlighting matched symbols with
        typed word(_fuzzy_word)
        In second column displayed total count of occurrence each matched word
        """
        if row == 0:
            if column == 0:
                return "Results:"
            else:
                return "Occurrence:"
        
        if column == 0:
            word = (self._displayed_list[row - 1])[0]
            prescription = self._levenshtein(self._fuzzy_word, word.lower(), True)
            highlighted_word = ""
            for action in prescription:
                if action == 'M':
                    html_code = '<b>%s</b>' % word[0]
                else:
                    html_code = '<i>%s</i>' % word[0]
                highlighted_word += html_code
                word = word[1:]
            return highlighted_word
        
        if column == 1:
            return (self._displayed_list[row - 1])[1]
        
        return "-1"
    
    def icon(self, row, column):
        """Icon for TreeView item. Now doesn't used.
        """
        return None
    
    def inline(self):
        """Inline completion.
        
        Shown after cursor. Appended to the typed text, if Tab is pressed
        """
        #print "inline"
        return ""
    
    def getFullText(self, row):
        """Row had been clicked by mouse. Get inline completion, which will be inserted after cursor
        """
        #print "getFullText " + str(row)
        if row != 0:
            return (self._displayed_list[row - 1])[0]
            
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

