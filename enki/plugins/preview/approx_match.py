# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Bryan A. Jones.
#
#    This file is part of Enki.
#
#    Enki is free software: you can redistribute it and/or modify it under the
#    terms of the GNU General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option) any later
#    version.
#
#    Enki is distributed in the hope that it will be useful, but WITHOUT ANY
#    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#    FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with
#    Enki.  If not, see <http://www.gnu.org/licenses/>.
#
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
# These are listed in the order prescribed by `PEP 8 <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Library imports
# ---------------
# For debugging.
import codecs
import cgi
import os
# For LCS.
import bisect
#
# Third-party imports
# -------------------
# For approximate pattern matching, this module uses the Python port of `TRE
# <http://hackerboss.com/approximate-regex-matching-in-python>`_.
import tre
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
def htmlFormatSearchInput(searchText, leftAnchor, searchAnchor, rightAnchor):
    # Divide the text into four pieces based on the three anchors. Escape them for use in HTML.
    beforeLeft = cgi.escape(searchText[:leftAnchor])
    leftToAnchor = cgi.escape(searchText[leftAnchor:searchAnchor])
    anchorToRight = cgi.escape(searchText[searchAnchor:rightAnchor])
    afterRight = cgi.escape(searchText[rightAnchor:])

    return ( (
      # Use preformatted text so spaces, newlines get
      # interpreted correctly. Include all text up to the
      # left anchor.
      '<pre style="word-wrap: break-word;white-space: pre-wrap;">%s' +
      # Format text between the left anchor and the search
      # anchor with a red background.
      '<span style="background-color:red;">%s</span>' +
      # Place a huge X marks the spot at the anchor
      '<span style="color:blue; font-size:xx-large;">X</span>' +
      # Format text between the search anchor and the right
      # anchor with a yellow background.
      '<span style="background-color:yellow;">%s</span>' +
      # Include the text between the right anchor and end of
      # text with no special formatting.
      '%s</pre>') % (beforeLeft, leftToAnchor, anchorToRight, afterRight) )

# Take these two results and put them side by side in a table.
def htmlFormatSearch(htmlSearchInput, htmlSearchResults, matchCost):
    return ( (
      'Editing distance: %s<br />\n\n' +
      '<table id="outerTable"><tr><th>Search input</th><th>Search results</th></tr>\n'
      '<tr><td>%s</td>\n' +
      '<td>%s</td></tr></table>\n    <script language="Javascript">' +
      'document.getElementById("outerTable").width = window.innerWidth/1.1;' +
      '</script>'
      ) %
      (unicode(matchCost), htmlSearchInput, htmlSearchResults) )


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
    print("Writing log file to " + os.getcwd())
    with codecs.open('approx_match_log.html', 'w', encoding = 'utf-8') as f:
        f.write(htmlText)
#
# findApproxText
# ================
# The findApproxText function performs a single approximate match using TRE.
# TRE stops at the first match it find; this routine makes sure the match found
# is at least 10% better than the next best approximate match.
#
# Return value:
#   - If there is no unique value, (None, 0, 0)
#   - Otherwise, it returns (match, beginInTarget, endInTarget) where:
#
#     match
#       A TRE match object.
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
  targetText,
  # Maximum allowable cost for an approximate match. None indicates no maximum cost.
  cost = None):

    # tre.LITERAL specifies that searchText is a literal search string, not
    # a regex.
    pat = tre.compile(searchText, tre.LITERAL)
    fz = tre.Fuzzyness(maxerr = cost) if cost else tre.Fuzzyness()
    match = pat.search(targetText, fz)
    # Store the index into the target string of the first and last matched chars.
    beginInTarget, endInTarget = match.groups()[0]

    # TRE picks the first match it finds, even if there is
    # more than one match with identical error. So, manually
    # call it again excluding the found text to check. In addition,
    # make sure this match is unique: it should be 10%
    # better than the next best match.
    matchAgain = pat.search(targetText[:beginInTarget] + targetText[endInTarget:], fz)

    if matchAgain and (matchAgain.cost <= match.cost*1.1):
        ## print('Multiple matches ' + str(matchAgain.groups()))
        return None, 0, 0
    else:
        ## print(searchText + '\n' + targetText[beginInTarget:endInTarget])
        return match, beginInTarget, endInTarget
#
# findApproxTextInTarget
# ==========================
# This routine first finds the closest approximate match of a substring centered
# around the searchAnchor in the targetText. Given this search substring and
# the approximately matched target substring, it looks for the best possible
# (hopefully exact) match containing the searchAnchor between the search substring
# and the target substring by steadily reducing the size of the substrings. With
# this best possible (hopefully exact) match, it can then locate the searchAnchor
# in this target substring; it retuns this targetAnchor, which is the index of
# the searchAnchor in the targetText.
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

#
# Approximate match of searchAnchor within targetText
# -----------------------------------------------------
# Look for the best approximate match within the targetText of the source
# substring composed of characters within a radius of the anchor.
    #
    # First, choose a radius of chars about the anchor to search in.
    begin = max(0, searchAnchor - searchRange)
    end = min(len(searchText), searchAnchor + searchRange)
    # Empty documents are easy to search.
    if end <= begin:
        return 0
    # Look for a match; record left and right search radii.
    match, beginInTarget, endInTarget = findApproxText(searchText[begin:end], targetText)
    # If no unique match is found, give up (for now -- this could be improved).
    if not match:
        # how about we try it again by increasing search region?
        begin = max(0, searchAnchor - int(searchRange*1.5))
        end = min(len(searchText), searchAnchor + int(searchRange*1.5))
        match, beginInTarget, endInTarget = findApproxText(searchText[begin:end], targetText)
        if not match:
            if ENABLE_LOG:
                si = htmlFormatSearchInput(searchText, begin, searchAnchor, end)
                sr = htmlFormatSearchInput(targetText, 0, 0, 0)
                fs = htmlFormatSearch(si, sr, "No unique match found.")
                ht = htmlTemplate(fs)
                writeHtmlLog(ht)
            return -1

    # acquire search string and target string
    searchPattern = searchText[begin:end]
    targetSubstring = targetText[beginInTarget:endInTarget]
    # find where the anchor is in searchPattern
    relativeSearchAnchor = searchAnchor - begin
    offset, editingDist, lcsString = refineSearchResult(relativeSearchAnchor,
      searchPattern, targetSubstring)
    if offset is not -1:
        offset = offset + beginInTarget

    if ENABLE_LOG:
        si = htmlFormatSearchInput(searchText, begin, searchAnchor, end)
        if offset is not -1:
            sr = htmlFormatSearchInput(targetText, beginInTarget, offset, endInTarget)
            fs = htmlFormatSearch(si, sr, editingDist)
        else:
            sr = htmlFormatSearchInput(targetText, 0, 0, 0)
            fs = htmlFormatSearch(si, sr, "No unique match found.")
        ht = htmlTemplate(fs)
        writeHtmlLog(ht)

    return offset
#
# A moded way of refining search result
# -------------------------------------
def refineSearchResult(searchAnchor, searchPattern, targetSubstring):
    # perform a `lcs <http://en.wikipedia.org/wiki/Longest_common_subsequence_problem>`_ search.
    # Code adopt from `Rosettacode <http://rosettacode.org/wiki/Longest_common_subsequence#Dynamic_Programming_6>`_.
    lengths = [[0 for j in range(len(targetSubstring)+1)] for i in range(len(searchPattern)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(searchPattern):
        for j, y in enumerate(targetSubstring):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
    # read the subsequence out from the table
    lcsString = ""
    x, y = len(searchPattern), len(targetSubstring)
    # define the editing distance
    minCost = 0
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
            minCost = minCost+1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
            minCost = minCost+1
        else:
            assert searchPattern[x-1] == targetSubstring[y-1]
            lcsString = searchPattern[x-1] + lcsString
            x -= 1
            y -= 1

    # if LCS fails to find common subsequence, then set offset to -1 and inform
    # ``findApproxTextInTarget`` that no match is found. This rarely happens
    # since TRE has preprocessed input string.
    if len(lcsString) is 0:
        return -1, -1, ''

    # map search result back to both searchPattern and targetSubstring. get
    # the relative index in both search pattern and target substring.
    ind = [[len(searchPattern)+1, len(targetSubstring)+1] for i in range(1+len(lcsString))]
    for i in range(len(lcsString)-1, -1, -1):
        ind[i][0] = searchPattern[:ind[i+1][0]].rindex(lcsString[i])
        ind[i][1] = targetSubstring[:ind[i+1][1]].rindex(lcsString[i])
    ind = ind[:len(lcsString)][:]

    # lcs map back to search pattern will get ``lcsSearchPatternInd``
    lcsSearchPatternInd = [ ind[i][0] for i in xrange(len(ind)) ]
    # find the corresponding index in targetText
    lcsClosestIndInTargetText = bisect.bisect_left(lcsSearchPatternInd, searchAnchor)
    # BUG: if anchor is at the end of searchText (this won't happen until user
    # select the last char. of the whole page)
    if lcsClosestIndInTargetText == len(ind):
        anchorInTargetText = len(targetSubstring)
    else:
        anchorInTargetText = ind[lcsClosestIndInTargetText][1]
    return anchorInTargetText, minCost, lcsString
