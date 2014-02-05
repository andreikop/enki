# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Bryan A. Jones.
#
#    This file is part of Enki.
#
#    Enki is free software: you can redistribute it and/or
#    modify it under the terms of the GNU General Public
#    License as published by the Free Software Foundation,
#    either version 3 of the License, or (at your option)
#    any later version.
#
#    Enki is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied
#    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#    PURPOSE.  See the GNU General Public License for more
#    details.
#
#    You should have received a copy of the GNU General
#    Public License along with Enki.  If not, see
#    <http://www.gnu.org/licenses/>.

#
# *************************************************************************************
# ApproxMatch.py - provide approximate matching to support code and web synchronization
# *************************************************************************************
# The find_approx_text_in_target_ function in this module
# searches a target string for the best match to characters
# about an anchor point in a source string. In particular,
# it first locates a block of target text which forms the
# closest approximate match for source characters about the
# anchor. Then, it looks for the (almost) longest possible
# exact match between source characters about the anchor and
# the block of target text found in the first step.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8
# <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Library imports
# ---------------
# Both used for debugging.
import codecs
import cgi
#
# Third-party imports
# -------------------
# For approximate pattern matching, this module uses the
# Python port of `TRE
# <http://hackerboss.com/approximate-regex-matching-in-python>`_.
import tre
#
# For debug
# =========
# Write the results of a match to an HTML file if enabled.
ENABLE_LOG = False
#
# Given a search result, format it in HTML: create a <pre>
# entry with the text, hilighting from the left_anchor to
# the search_anchor in one color and from search_anchor to
# right_anchor in another color. Show the anchor with a big
# yellow X marks the spot.
def html_format_search_input(search_text, left_anchor, search_anchor, right_anchor):
    # Divide the text into four pieces based on the three
    # anchors. Escape them for use in HTML.
    before_left = cgi.escape(search_text[:left_anchor])
    left_to_anchor = cgi.escape(search_text[left_anchor:search_anchor])
    anchor_to_right = cgi.escape(search_text[search_anchor:right_anchor])
    after_right = cgi.escape(search_text[right_anchor:])

    return ( (
      # Use preformatted text so spaces, newlines get
      # interpreted correctly. Include all text up to the
      # left anchor.
      '<pre>%s' +
      # Format text between the left anchor and the search
      # anchor with a red background.
      '<span style="background-color:red;">%s</span>' +
      # Place a huge X marks the spot at the anchor
      '<span style="color:yellow; font-size:xx-large;">X</span>' +
      # Format text between the search anchor and the right
      # anchor with a blue background.
      '<span style="background-color:blue;">%s</span>' +
      # Include the text between the right anchor and end of
      # text with no special formatting.
      '%s</pre>') % (before_left, left_to_anchor, anchor_to_right, after_right) )

# Show the results from a search: create a <pre> entry with
# the text, highlighting the matched portion of the text.
def html_format_search_results(searched_text, left_anchor, right_anchor):
    # Divide the text into three pieces based on the two
    # anchors. Escape them for use in HTML.
    before_left = cgi.escape(search_text[:left_anchor])
    left_to_right = cgi.escape(search_text[left_anchor:right_anchor])
    after_right = cgi.escape(search_text[right_anchor:])

    return ( (
      # Use preformatted text so spaces, newlines get
      # interpreted correctly. Include all text up to the
      # left anchor.
      '<pre>%s' +
      # Format text between the left anchor and the right
      # anchor with a green background.
      '<span style="background-color:green;">%s</span>' +
      # Include the text between the right anchor and end of
      # text with no special formatting.
      '%s</pre>') % (before_left, left_to_right, after_right) )

# Take these two results and put them side by side in a table.
def html_format_search(html_search_input, html_search_results, match_cost):
    return ( (
      '<table><tr><th>Search input</th><th>Search results</th></tr>\n'
      '<tr><td>%s</td>\n' +
      '<td>%s</td></tr></table>\n' +
      'Match cost: %s<br />\n\n') %
     (html_search_input, html_search_results, unicode(match_cost)) )

# Create text for a simple web page.
LOG_COUNTER = 0
def html_template(body):
    global LOG_COUNTER

    LOG_COUNTER += 1
    return ( (
"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <title>ApproxMatch log #%d</title>
    <meta http-equiv="content-type"
        content="text/html;charset=utf-8" />
  </head>

  <body>
%s
  </body>

</html>
""") % (LOG_COUNTER, body) )

# Given HTML, write it to a file.
def write_html_log(html_text):
    with codecs.open('ApproxMatch_log.html', 'w', encoding = 'utf-8') as f:
        f.write(html_text)
#
# find_approx_text
# ================
# The find_approx_text function performs a single
# approximate match using TRE. TRE stop at the first match
# it find; this routine makes sure the match found is at
# least 10% better than the next best approximate match.
#
# Return value:
#   - If there is no unique value, (None, 0, 0)
#   - Otherwise, it returns (match, begin_in_target,
#     end_in_target) where:
#
#     match
#       A TRE match object.
#
#     begin_in_target
#       The index into the target string at which the
#       approximate match begins.
#
#     end_in_target
#       The index into the target string at which the
#       approximate match ends.
def find_approx_text(
  # Text to search for
  search_text,
  # Text in which to find the search_text
  target_text,
  # Maximum allowable cost for an
  # approximate match. None indicates
  # no maximum cost.
  cost = None):
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
    match_again = pat.search(target_text[end_in_target:], fz)
    if match_again and (match_again.cost <= match.cost*1.1):
##        print('Multiple matches ' + str(match_again.groups()))
        return None, 0, 0
    else:
##        print(search_text + '\n' + target_text[begin_in_target:end_in_target])
        return match, begin_in_target, end_in_target

# find_approx_text_in_target
# ==========================
# This routine first finds the closest approximate match of
# a substring centered around the search_anchor in the
# target_text. Given this search substring and the
# approximately matched target substring, it looks for the
# best possible (hopefully exact) match containing the
# search_anchor between the search substring and the target
# substring by steadily reducing the size of the substrings.
# With this best possible (hopefully exact) match, it can
# then locate the search_anchor in this target substring; it
# retuns this target_anchor, which is the index of the
# search_anchor in the target_text.
#
# Return value: An (almost) exactly-matching location in the
# target document, or -1 if not found.
def find_approx_text_in_target(
  # The text composing the entire source document in
  # which the search string resides.
  search_text,
  # A location in the source document which should be
  # found in the target document.
  search_anchor,
  # The target text in which the search will be performed.
  target_text,
  # The radius of the substring around the search_anchor
  # that will be approximately matched in the
  # target_text: a value of 10 produces a length-20
  # substring (10 characters before the anchor, and 10
  # after).
  search_range=40,
  # When searching for a best possible match, this
  # specifies the number of characters to remove from
  # the substrings. It must be a minimum of 1.
  step_size=1):

    assert step_size > 0
#
# Approximate match of search_anchor within target_text
# -----------------------------------------------------
# Look for the best approximate match within the target_text
# of the source substring composed of characters within a
# radius of the anchor.
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
        if ENABLE_LOG:
            si = html_format_search_input(search_text, begin, search_anchor, end)
            sr = html_format_search_results(target_text, 0, 0)
            fs = html_format_search(si, sr, "No unique match found.")
            ht = html_template(fs)
            write_html_log(ht)
        return -1
#
# Search for an exact match between the search_anchor substring and the target_text approximate match
# --------------------------------------------------------------------------------------------------------
    # Record this initial match cost (which measures the
    # difference between the source and target substrings).
    # Perform all future searches only within the source and
    # target substrings found in this search.
    min_cost = match.cost
    min_cost_begin = begin
    min_cost_end = end
    # For debug logging
 ##   log_begin = begin
 ##   log_end = end

    # If we have an exact match, need to define this, since
    # the while loops won't (both will fall through without
    # being evaluated). We're 0 characters forward from the
    # begin_in_target point before we do any additional
    # search refinements.
    begin_in_target_substr = 0

# Look for an exact match to the left of the anchor
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Reduce the left search radius, looking for better match.
# Keep the best possible match.
#
    # While the search radius to the left of the anchor > 0 and the cost > 0:
##    print('Searching right radius')
    while (end > search_anchor) and (min_cost > 0):

        # Decrease the left search radius by step_size and
    # approximate search again.
        #
        # Note that (end - search_anchor)/2 == 0 when end =
    # search_anchor + 1, causing infinite looping. The
    # max fixes this case.
        end -= max((end - search_anchor) - step_size, 1)
        match, begin_in_target_substr, end_in_target_substr = \
            find_approx_text(search_text[begin:end],
                             target_text[begin_in_target:end_in_target])

        # If there are multiple matches, undo this search
    # radius change and exit. This is the lowest
    # achievable cost.
        if not match:
            break

        # If the cost has decreased, record this new cost
    # and its associated left search radius.
        if match.cost < min_cost:
            min_cost = match.cost
            min_cost_end = end

# Look for an exact match to the right of the anchor
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # Repeat the above loop for the right search radius.
##    print('Searching left radius')
    while (begin < search_anchor) and (min_cost > 0):

        # Decrease the right search radius by step_size and
    # approximate search again.
        begin += max((search_anchor - begin) - step_size, 1)
        match, begin_in_target_substr, end_in_target_substr = \
            find_approx_text(search_text[begin:min_cost_end],
                             target_text[begin_in_target:end_in_target])

        # If there are multiple matches, undo this search
    # radius change and exit. This is the lowest
    # achievable cost.
        if not match:
            break

        # If the cost has decreased, record this new cost
    # and its associated left search radius.
        if match.cost < min_cost:
            min_cost = match.cost
            min_cost_begin = begin

#
# Compute the index of search_anchor in target_text based on this best-possible match
# -----------------------------------------------------------------------------------
    # Return the match. It's not perfect if the cost > 0.
##    if min_cost > 0:
##        print('No exact match; cost was %d.' % min_cost)
##        with codecs.open('search_log.txt', 'w', encoding = 'utf-8') as f:
##            f.write(('Failed -- no exact match (cost was %d).\n\n' % min_cost) +
##              search_text[log_begin:log_end] + '\n\n' +
##              search_text[begin:min_cost_end] + '\n\n' +
##              target_text[begin_in_target:end_in_target] + '\n\n' +
##              target_text)
    offset = begin_in_target + begin_in_target_substr + (search_anchor - min_cost_begin)
    # Make sure the result lies within the bounds of
    # target_text. Since we return a cursor position, an
    # offset of len(target_text), meaning the end of
    # target_text, is valid.
    offset = min(len(target_text), max(0, offset))

    if ENABLE_LOG:
        si = html_format_search_input(search_text, begin, search_anchor, end)
        sr = html_format_search_input(target_text, begin_in_target, offset, end_in_target)
        fs = html_format_search(si, sr, min_cost)
        ht = html_template(fs)
        write_html_log(ht)

    return offset
