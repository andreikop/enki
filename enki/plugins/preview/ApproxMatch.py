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
# ***************************************************************************************************
# ApproxMatch.py - provide approximate matching to support code and web synchronization
# ***************************************************************************************************
# The find_approx_text_in_target_ function in this module searches a target string
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
# Both used for debugging.
import codecs
import cgi
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
ENABLE_LOG = True
#
# Given a search result, format it in HTML: create a <pre> entry with the text,
# hilighting from the left_anchor to the search_anchor in one color and from
# search_anchor to right_anchor in another color. Show the anchor with a big
# yellow X marks the spot.
def html_format_search_input(search_text, left_anchor, search_anchor, right_anchor):
    # Divide the text into four pieces based on the three anchors. Escape them for use in HTML.
    before_left = cgi.escape(search_text[:left_anchor])
    left_to_anchor = cgi.escape(search_text[left_anchor:search_anchor])
    anchor_to_right = cgi.escape(search_text[search_anchor:right_anchor])
    after_right = cgi.escape(search_text[right_anchor:])

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
      '%s</pre>') % (before_left, left_to_anchor, anchor_to_right, after_right) )

# Take these two results and put them side by side in a table.
def html_format_search(html_search_input, html_search_results, match_cost):
    return ( (
      'Editing distance: %s<br />\n\n' +
      '<table id="outerTable"><tr><th>Search input</th><th>Search results</th></tr>\n'
      '<tr><td>%s</td>\n' +
      '<td>%s</td></tr></table>\n    <script language="Javascript">' +
      'document.getElementById("outerTable").width = window.innerWidth/1.1;' +
      '</script>'
      ) %
      (unicode(match_cost), html_search_input, html_search_results) )


# Create text for a simple web page.
LOG_COUNTER = 0
def html_template(body):
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
import os
def write_html_log(html_text):
    print "Write Log file to : " + os.getcwd()
    with codecs.open('ApproxMatch_log.html', 'w', encoding = 'utf-8') as f:
        f.write(html_text)
#
# find_approx_text
# ================
# The find_approx_text function performs a single approximate match using TRE. 
# TRE stop at the first match it find; this routine makes sure the match found 
# is at least 10% better than the next best approximate match.
#
# Return value:
#   - If there is no unique value, (None, 0, 0)
#   - Otherwise, it returns (match, begin_in_target, end_in_target) where:
#
#     match
#       A TRE match object.
#
#     begin_in_target
#       The index into the target string at which the approximate match begins.
#
#     end_in_target
#       The index into the target string at which the approximate match ends.
def find_approx_text(search_text,
                     #   Text to search for
                     target_text,
                     #   Text in which to find the search_text
                     cost = None):
                     #   Maximum allowable cost for an approximate match. None indicates no maximum cost.
    # tre.LITERAL specifies that search_str is a literal search string, not
    # a regex.
    pat = tre.compile(search_text, tre.LITERAL)
    fz = tre.Fuzzyness(maxerr = cost) if cost else tre.Fuzzyness()
    match = pat.search(target_text, fz)
    # Store the index into the target string of the first and last matched chars.
    begin_in_target, end_in_target = match.groups()[0]

    # TRE picks the first match it finds, even if there is
    # more than one match with identical error. So, manually
    # call it again with a substring to check. In addition,
    # make sure this match is unique: it should be 10%
    # better than the next best match.
    match_again = pat.search(target_text[:begin_in_target] + target_text[end_in_target:], fz)

    if match_again and (match_again.cost <= match.cost*1.1):
        ## print('Multiple matches ' + str(match_again.groups()))
        return None, 0, 0
    else:
        ## print(search_text + '\n' + target_text[begin_in_target:end_in_target])
        return match, begin_in_target, end_in_target

# find_approx_text_in_target
# ==========================
# This routine first finds the closest approximate match of a substring centered
# around the search_anchor in the target_text. Given this search substring and 
# the approximately matched target substring, it looks for the best possible 
# (hopefully exact) match containing the search_anchor between the search substring
# and the target substring by steadily reducing the size of the substrings. With
# this best possible (hopefully exact) match, it can then locate the search_anchor
# in this target substring; it retuns this target_anchor, which is the index of
# the search_anchor in the target_text.
#step_size
# Return value: An (almost) exactly-matching location in the target document, or
# -1 if not found.
def find_approx_text_in_target(search_text,
                               # The text composing the entire source document in
                               # which the search string resides.
                               search_anchor,
                               # A location in the source document which should be
                               # found in the target document.
                               target_text,
                               # The target text in which the search will be performed.
                               search_range=30,
                               # The radius of the substring around the search_anchor
                               # that will be approximately matched in the
                               # target_text: a value of 10 produces a length-20
                               # substring (10 characters before the anchor, and 10
                               # after).
                               step_size=1):
                               # When searching for a best possible mD:\\enki\\enkiatch, this
                               # specifies the number of characters to remove from
                               # the substrings. It must be a minimum of 1.
    assert step_size > 0
#
# Approximate match of search_anchor within target_text
# -----------------------------------------------------
# Look for the best approximate match within the target_text of the source substring composed of characters within a radius of the anchor.
    #
    # First, choose a radius of chars about the anchor to search in.
    begin = max(0, search_anchor - search_range)
    end = min(len(search_text), search_anchor + search_range)
    # Empty documents are easy to search.
    if end <= begin:
        return 0
    # Look for a match; record left and right search radii.
    match, begin_in_target, end_in_target = find_approx_text(search_text[begin:end], target_text)
    # If no unique match is found, give up (for now -- this could be improved).
    if not match:
        # how about we try it again by increasing search region?
        begin = max(0, search_anchor - int(search_range*1.5))
        end = min(len(search_text), search_anchor + int(search_range*1.5))
        match, begin_in_target, end_in_target = find_approx_text(search_text[begin:end], target_text)
        if not match:
            if ENABLE_LOG:
                si = html_format_search_input(search_text, begin, search_anchor, end)
                sr = html_format_search_input(target_text, 0, 0, 0)
                fs = html_format_search(si, sr, "No unique match found.")
                ht = html_template(fs)
                write_html_log(ht)
            return -1

    # acquire search string and target string
    search_pattern = search_text[begin:end]
    target_substring = target_text[begin_in_target:end_in_target]
    # find where the anchor is in search_pattern
    relative_search_anchor = search_anchor - begin
    offset, editing_dist, lcs_string = refine_search_result(relative_search_anchor, search_pattern, target_substring)
    if offset is not -1:
        offset = offset + begin_in_target

    if ENABLE_LOG:
        si = html_format_search_input(search_text, begin, search_anchor, end)
        if offset is not -1:
            sr = html_format_search_input(target_text, begin_in_target, offset, end_in_target)
            fs = html_format_search(si, sr, editing_dist)
        else:
            sr = html_format_search_input(target_text, 0, 0, 0)
            fs = html_format_search(si, sr, "No unique match found.")
        ht = html_template(fs)
        write_html_log(ht)

    return offset

# A moded way of refining search result
# --------------------------------------------------------------------------------------------------------
import bisect
def refine_search_result(search_anchor, search_pattern, target_substring):    
    # perform a `lcs <http://en.wikipedia.org/wiki/Longest_common_subsequence_problem>`_ search. Code adopt from `Rosettacode <http://rosettacode.org/wiki/Longest_common_subsequence#Dynamic_Programming_6>`_.
    lengths = [[0 for j in range(len(target_substring)+1)] for i in range(len(search_pattern)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(search_pattern):
        for j, y in enumerate(target_substring):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
    # read the subsequence out from the table
    lcs_string = ""
    x, y = len(search_pattern), len(target_substring)
    # define the editing distance
    min_cost = 0
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
            min_cost = min_cost+1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
            min_cost = min_cost+1
        else:
            assert search_pattern[x-1] == target_substring[y-1]
            lcs_string = search_pattern[x-1] + lcs_string
            x -= 1
            y -= 1
    
    # if LCS fails to find common subsequence, then set offset to -1 and inform ``find_approx_text_in_target`` that no match is found. This rarely happens since TRE has preprocessed input string.
    if len(lcs_string) is 0:
        return -1, -1, ''
    
    # map search result back to both search_pattern and target_substring. get the relative index in both search pattern and target substring
    ind = [[len(search_pattern)+1, len(target_substring)+1] for i in range(1+len(lcs_string))]
    for i in range(len(lcs_string)-1, -1, -1):
        ind[i][0] = search_pattern[:ind[i+1][0]].rindex(lcs_string[i])
        ind[i][1] = target_substring[:ind[i+1][1]].rindex(lcs_string[i])
    ind = ind[:len(lcs_string)][:]
    
    # lcs map back to search pattern will get ``lcs_search_pattern_ind``
    lcs_search_pattern_ind = [ ind[i][0] for i in xrange(len(ind)) ]
    # find the corresponding index in target_text
    lcs_closest_ind_in_target_text = bisect.bisect_left(lcs_search_pattern_ind, search_anchor)
    # BUG: if anchor is at the end of search_text (this won't happen until user select the last char. of the whole page)
    if lcs_closest_ind_in_target_text == len(ind):
        lcs_closest_ind_in_target_text = len(ind)-1
    anchor_in_target_text = ind[lcs_closest_ind_in_target_text][1]
    return anchor_in_target_text, min_cost, lcs_string