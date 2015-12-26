# .. -*- coding: utf-8 -*-
# **************************************************************************************
# approx_match.py - provide approximate matching to support code and web synchronization
# **************************************************************************************
# The findApproxTextInTarget_ function in this module searches a target string
# for the best match to characters about an anchor point in a source string. In
# particular, it first locates a block of target text which forms the closest
# approximate match for source characters about the anchor. Then, it looks for
# the (almost) longest possible exact match between source characters about the
# anchor and the block of target text found in the first step.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Library imports
# ---------------
# For debugging.
import codecs
import html
import os
#
# Third-party imports
# -------------------
import pkg_resources

# The `regex <https://pypi.python.org/pypi/regex>`_ module supports approximate
# matching. Make sure it is recent enough to be usable.
import regex
try:
  # Get the version of regex. See https://pythonhosted.org/setuptools/pkg_resources.html#distribution-attributes.
  regexVersion = pkg_resources.get_distribution('regex').parsed_version
  # Issues I filed before this make regex unusable. See #166, #167, andd #169 at
  # https://bitbucket.org/mrabarnett/mrab-regex/issues. For version parse, see
  # https://pythonhosted.org/setuptools/pkg_resources.html#parsing-utilities.
  assert regexVersion >= pkg_resources.parse_version('2015.11.07')
except AssertionError as ValueError:
  raise ImportError
#
# For debug
# =========
# Write the results of a match to an HTML file if enabled.
ENABLE_LOG = False
#
# Given a search result, format it in HTML: create a <pre> entry with the text,
# hilighting from the leftAnchor to the searchAnchor in one color and from
# searchAnchor to rightAnchor in another color. Show the anchor with a big
# yellow X marks the spot.
def htmlFormatSearchInput(searchText, leftAnchor, searchAnchor, rightAnchor,
  showX=True):
    # Divide the text into four pieces based on the three anchors. Escape them
    # for use in HTML.
    beforeLeft = html.escape(searchText[:leftAnchor])
    leftToAnchor = html.escape(searchText[leftAnchor:searchAnchor])
    anchorToRight = html.escape(searchText[searchAnchor:rightAnchor])
    afterRight = html.escape(searchText[rightAnchor:])

    return ( (
      # Use preformatted text so spaces, newlines get
      # interpreted correctly. Include all text up to the
      # left anchor.
      '<pre style="word-wrap:break-word; white-space:pre-wrap;">%s' +
      # Format text between the left anchor and the search
      # anchor with a red background.
      '<span style="background-color:red;">%s</span>' +
      # Place a huge X marks the spot at the anchor
      ('<span style="color:blue; font-size:xx-large;">X</span>' if showX else '') +
      # Format text between the search anchor and the right
      # anchor with a yellow background.
      '<span style="background-color:yellow;">%s</span>' +
      # Include the text between the right anchor and end of
      # text with no special formatting.
      '%s</pre>') % (beforeLeft, leftToAnchor, anchorToRight, afterRight) )

# Take these two results and put them side by side in a table.
def htmlFormatSearch(htmlSearchInput, htmlSearchResults, resultText):
    return ( (
      # Preserve white space in the resultText string.
      '<span style="white-space:pre;">%s</span><br />\n\n' +
      '<table id="outerTable"><tr><th>Search input</th><th>Search results</th></tr>\n'
      '<tr><td>%s</td>\n' +
      '<td>%s</td></tr></table>\n' +
      '<br /><br /><br />'
      ) %
      (resultText, htmlSearchInput, htmlSearchResults) )


# Create text for a simple web page.
LOG_COUNTER = 0
def htmlTemplate(body):
    global LOG_COUNTER

    LOG_COUNTER += 1
    return ( (
      """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
      "http://www.w3.org/TR/html4/strict.dtd"><html>
      <head><title>ApproxMatch log #%d</title>
      <meta http-equiv="content-type" content="text/html;charset=utf-8" />
      <style>
         table {border-collapse:collapse; table-layout:fixed;}
         table td {border:solid 1px; word-wrap:break-all; vertical-align: top;}
      </style></head>
      <body>%s</body></html>
      """) % (LOG_COUNTER, body) )

# Given HTML, write it to a file.
def writeHtmlLog(htmlText):
    print(("Writing log file to " + os.getcwd()))
    with codecs.open('approx_match_log.html', 'w', encoding = 'utf-8') as f:
        f.write(htmlText)
#
# findApproxText
# ==============
# This function performs a single approximate match using the regex_ library.
#
# Return value:
#   - If there is no unique value, (None, 0, 0)
#   - Otherwise, it returns (match, beginInTarget, endInTarget) where:
#
#     match
#       A regex_ match object.
#
#     beginInTarget
#       The index into the target string at which the approximate match begins.
#
#     endInTarget
#       The index into the target string at which the approximate match ends.
def findApproxText(
  # Text to search for
  searchText,
  # Text in which to find the searchText
  targetText):

    mo = regexFuzzySearch(searchText, targetText)
    if mo:
        # See if this match is unique enough by looking for the next best match
        # by searching in the string before then the string after the match.
        moPre = regexFuzzySearch(searchText, targetText[:mo.start()])
        moPost = regexFuzzySearch(searchText, targetText[mo.end():])

        # Compute an error based on the fuzzyness. If there wasn't a match, use
        # maximum error of moError + 6, so that the test below passes.
        moError = sum(mo.fuzzy_counts)
        moPreError = sum(moPre.fuzzy_counts) if moPre else moError*2
        moPostError = sum(moPost.fuzzy_counts) if moPost else moError*2

        # Make sure the difference between the match and any other match is high
        # enough to consider this match unique.
        if moError*1.1 <= moPreError and moError*1.1 <= moPostError:
            return mo

    # If a match couldn't be found or wasn't good enough, return a failure.
    return None

# This helper function uses regex_ to perform a fuzzy search.
def regexFuzzySearch(
  # Text to search for. It is NOT treated as a regex.
  searchText,
  # Text in which to find the searchText
  targetText):

    # Escape any characters in searchText that would be treated as a regexp.
    searchText = regex.escape(searchText)
    # The regex_ library supports fuzzy matching. Quoting from the manual:
    #
    # - ``(item){e}`` means perform a fuzzy match of the given ``item``,
    #   allowing insertions, deletions, or substitutions.
    # - The BESTMATCH flag searches for the best possible match, rather than the
    #   match found first.
    return regex.search('(' + searchText + '){e}', targetText, regex.BESTMATCH)

#
# findApproxTextInTarget
# ======================
# This routine first finds the closest approximate match of a substring centered
# around the searchAnchor in the targetText.
#
# Return value: An (almost) exactly-matching location in the target document, or
# -1 if not found.
def findApproxTextInTarget(
  # The text composing the entire source document in
  # which the search string resides.
  searchText,
  # A location in the source document which should be
  # found in the target document.
  searchAnchor,
  # The target text in which the search will be performed.
  targetText,
  # The radius of the substring around the searchAnchor
  # that will be approximately matched in the
  # targetText: a value of 10 produces a length-20
  # substring (10 characters before the anchor, and 10
  # after).
  searchRange=30):

    # Look for the best approximate match within the targetText of the source
    # substring composed of characters within a radius of the anchor.
    begin = max(0, searchAnchor - searchRange)
    end = min(len(searchText), searchAnchor + searchRange)
    # Empty documents are easy to search.
    if end <= begin:
        return 0
    # Look for a match.
    # record left and right search radii.
    mo = findApproxText(searchText[begin:end], targetText)
    # If no unique match is found, try again with an increased search radius.
    if not mo:
        begin = max(0, searchAnchor - int(searchRange*1.5))
        end = min(len(searchText), searchAnchor + int(searchRange*1.5))
        mo = findApproxText(searchText[begin:end], targetText)
        if not mo:
            if ENABLE_LOG:
                si = htmlFormatSearchInput(searchText, begin, searchAnchor, end)
                sr = htmlFormatSearchInput(targetText, 0, 0, 0)
                fs = htmlFormatSearch(si, sr, "No unique match found.")
                ht = htmlTemplate(fs)
                writeHtmlLog(ht)
            return -1
    if ENABLE_LOG:
        # Log the initial match results
        si = htmlFormatSearchInput(searchText, begin, searchAnchor, end)
        sr = htmlFormatSearchInput(targetText, mo.start(), mo.start(),
          mo.end(), False)
        fs = htmlFormatSearch(si, sr, "Initial fuzzy search results")

    # Get a search and target substring from the match.
    searchPattern = searchText[begin:end]
    targetSubstring = targetText[mo.start():mo.end()]
    # Use the LCS_ algorithm to perform a more exact match. This algorithm
    # runs in O(NM) time, compared to regex's compiled (and hopefully faster)
    # performance.
    relativeSearchAnchor = searchAnchor - begin
    offset, lcsString = refineSearchResult(searchPattern, relativeSearchAnchor,
      targetSubstring, ENABLE_LOG)
    if offset != -1:
        offset = offset + mo.start()

    if ENABLE_LOG:
        si = htmlFormatSearchInput(searchText, begin, searchAnchor, end)
        if offset is not -1:
            sr = htmlFormatSearchInput(targetText, mo.start(), offset,
              mo.end())
            fs += htmlFormatSearch(si, sr, "Match was '%s'" % lcsString)
        else:
            sr = htmlFormatSearchInput(targetText, 0, 0, 0)
            fs += htmlFormatSearch(si, sr, "No unique match found.")
        ht = htmlTemplate(fs)
        writeHtmlLog(ht)

    return offset
#
# refineSearchResult
# ==================
# This function performs identically to findApproxTextInTarget_, but uses a more
# expensive and expact algorithm to compute the result.
def refineSearchResult(
  # The text composing the entire source document in
  # which the search string resides.
  searchText,
  # A location in the source document which should be
  # found in the target document.
  searchAnchor,
  # The target text in which the search will be performed.
  targetText,
  # True to return part of the resulting string as well; otherwise, the returned
  # lcsString will be empty. To get the full LCS string returned, pass
  # searchAnchor = 0. Used for testing.
  returnLcsString=False):
  #
    # Find the longest common substring (`LCS
    # <http://en.wikipedia.org/wiki/Longest_common_subsequence_problem>`_
    # between the source and target strings. The code was adopted from
    # `Rosettacode <http://rosettacode.org/wiki/Longest_common_subsequence#Dynamic_Programming_6>`_.
    #
    # A note on indices used in this algorithm::
    #
    #   The string s = abc:                        a b c
    #   Python string index (e.g. s[n]):           0 1 2
    #   LCS table index (e.g. x or y = n):         1 2 3
    #   Qt cursor anchor (e.g. searchAnchor = n): 0 1 2 3
    #
    # So, a given x or y value refers to a table index or, equivalently, an
    # anchor to their right.
    #
    # Initialize the substring length table entries to 0.
    lengths = [[0 for j in range(len(targetText) + 1)]
                    for i in range(len(searchText) + 1)]

    # Determine the length of the longest common subsequence and store this in
    # the table.
    for i, x in enumerate(searchText):
        for j, y in enumerate(targetText):
            # When characters match, increase the substring length. Otherwise,
            # the use maximum substring length found thus far.
            if x == y:
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])

    # If LCS fails to find a common subsequence, then set the offset to -1 and
    # inform ``findApproxTextInTarget`` that no match is found. This rarely
    # happens since regex has preprocessed input string.
    if lengths[-1][-1] == 0:
        return -1, ''

    # Walk through the table, read the LCS string out from the table and
    # finding the requested targetAnchor. This is a bit tricky:
    #
    # | Interesting case 1:
    # |  searchText = ab
    # |  searchAnchor: between ``a`` and ``b``.
    # |  targetText = a--b
    # | There's no clear correct answer for the returned cursor anchor. The most
    #   natural answer would be between ``a-`` and ``-b``. Therefore, we want to
    #   interpolate between the two target cursor anchors in this case.
    #
    # | Interesting case 2a:
    # |  searchText = Chapter 1:Once upon a time
    # |  targetText = :---------Once upon a time
    # |  searchAnchor: between ``Chapter 1:`` and ``Once upon a time``.
    # | The LCS in this case is ``:Once upon a time``. There are two mechanically
    #   value answers: an anchor to the right of the colon, or to the left of the
    #   O. We obviously want the anchor to the left of the O.
    #
    # | Interesting case 2b:
    # |  searchText = Once upon a time, there lived
    # |  targetText = Once upon a time------------,
    # |  searchAnchor: between ``Once upon a time`` and ``, there lived``.
    # | The LCS in this case is ``Once upon a time,``. There are two mechanically
    #   valid answers: an anchor to the right of the e, or to the left of the
    #   comma. We obviously want the anchor to the right of the e.
    #
    # So, in these cases, prefer the side with the longest consectuive match.
    # Given the type of text we're matching (some ignorable markup mixed with
    # valid text), picking the valid text instead of interpolating seems best.
    #
    # Therefore, we need to find the targetText index of both sides of the match
    # (unless the match occurs at the beginning or end of the string). If both
    # sides of the match refer to the same anchor (i.e. rightIndex == leftIndex + 1),
    # then return the anchor between these to characters. Otherwise, return an
    # anchor based on which side has more characters in their portion of the lcs
    # string.
    #
    # | Interesting case 3:
    # |  searchText = a--b
    # |  targetText = ab
    # |  searchAnchor: between ``a-`` and ``-b``.
    # | The characters near searchAnchor don't appear in targetText. So, pick the
    #   nearest targetText matches (a and b).
    #
    # So, walk backwards through the table.
    #
    # For debug, compute the lcs string.
    lcsString = ''
    # | x gives the searchText table index;
    # | y gives the targetText table index.
    # | Start at the end of the table.
    x, y = len(searchText), len(targetText)
    # Save the table index of the last matching character found.
    lastMatchIndex = y + 1
    # Record the length of the lcs match.
    lcsLen = 0
    # No anchor placement ambiguioty yet exists.
    matchIndices = None
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x - 1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y - 1]:
            y -= 1
        else:
            assert searchText[x - 1] == targetText[y - 1]
            # For debug purposes, uncomment the line below.
            ##print('x = %d, y = %d, searchText[x - 1] = %s, targetText[y - 1] = %s' % (x, y, searchText[x - 1], targetText[y - 1]))

            # On a match at or after the anchor (case 3 above -- the anchor
            # may lie between non-matching characters)...
            if x <= searchAnchor:
                # ...we now have a matched character index to the left of the
                # anchor. lastMatchIndex holds the matched character index to
                # the right of the anchor.
                #
                # In the simple case either:
                #
                # * These refer to adjacent characters, making the resulting
                #   anchor position unambiguous: place it between these two
                #   characters (to the left of lastMatchIndex == to the right of
                #   y).
                # * Or, this refers to the last matching character in the
                #   targetText (implying lastMatchIndex == y + 1), again making
                #   anchor placement unambiguous: to the right of y.
                #
                # In either case, return y, which refers to the desired anchor.
                if y == lastMatchIndex - 1:
                    return y, lcsString
                # Otherwise, we're have to distinguish between case 2a and 2b
                # above by comparing the lcs length before after this point.
                else:
                    # Save right LCS length and reset length to record left
                    # LCS length.
                    rightLcsLen = lcsLen + 1
                    lcsLen = -1
                    # Store these two indices, for use when the right LCS length
                    # is known and a decision about which to use can be made.
                    matchIndices = (y, lastMatchIndex - 1)
                    # Keep the if x <= searchAnchor from being true, so that the
                    # LCS algorithm will run to completion to compute the right
                    # LCS length.
                    searchAnchor = -1

            # Keep track of the last matched character's table index.
            lastMatchIndex = y

            # Don't compute the LCS string unless it's actually needed.
            if returnLcsString:
                lcsString = searchText[x - 1] + lcsString
            lcsLen += 1
            x -= 1
            y -= 1

    # Resolve an ambiguius anchor if necessary.
    if matchIndices:
        l, r = matchIndices
        # lcsLen holds the left LCS length.
        if lcsLen >= rightLcsLen:
            return l, lcsString
        else:
            return r, lcsString

    # At this point, we traced the LCS to the beginning of either the
    # searchText or the targetText, but haven't moved through
    # the desired searchAnchor. There are two cases:
    #
    # 1. x == 0: when searchAnchor == 0 and the index in y gives the
    #    corresponding targetText index.
    # 2. y == 0: the searchAnchor in the searchText lies before the
    #    corresponding targetText index. Return y == 0 as the best
    #    possible corresponding index.
    #
    # Therefore, return y.
    #
    # Some examples:
    #
    # * searchText = 'abcd', searchAnchor = 0 (before 'abcd'),
    #   targetText = '_abc', then y == 1 when x == 0, which lies between
    #   the characters '_' and 'abc' in the targetText.
    # * searchText = '__ab', searchAnchor = 1 (between '_' and '_ab'),
    #   targetText = 'ab', then x == 1 when y == 0, which is the beginning
    #   of the targetText.
    return y, lcsString
