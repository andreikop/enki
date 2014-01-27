# .. -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Bryan A. Jones.
#
#    This file is part of Enki.
#
#    Enki is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    Enki is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with Enki.  If not, see <http://www.gnu.org/licenses/>.
#
# ***************************************************************************************************
# ApproxMatch.py - provide approximate matching to support code and web synchronization
# ***************************************************************************************************
# The find_approx_text_in_target_ function in this module searches a target string for the best match to characters about an anchor point in a source string. In particular, it first locates a block of target text which forms the closest approximate match for source characters about the anchor. Then, it looks for the (almost) longest possible exact match between source characters about the anchor and the block of target text found in the first step.
#
# Imports
# =======
# These are listed in the order prescribed by `PEP 8 <http://www.python.org/dev/peps/pep-0008/#imports>`_.
#
# Third-party imports
# -------------------
# For approximate pattern matching, this module uses the Python port of `TRE <http://hackerboss.com/approximate-regex-matching-in-python>`_.
import tre
#
# For debug
#import codecs
#
# find_approx_text
# ================
# The find_approx_text function performs a single approximate match using TRE. TRE stop at the first match it find; this routine makes sure the match found is at least 10% better than the next best approximate match.
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

    # TRE picks the first match it finds, even if there is more than one match with identical error. So, manually call it again with a substring to check. In addition, make sure this match is unique: it should be 10% better than the next best match.
    match_again = pat.search(target_text[end_in_target:], fz)
    if match_again and (match_again.cost <= match.cost*1.1):
##        print('Multiple matches ' + str(match_again.groups()))
        return None, 0, 0
    else:
##        print(search_text + '\n' + target_text[begin_in_target:end_in_target])
        return match, begin_in_target, end_in_target

# find_approx_text_in_target
# ==========================
# This routine first finds the closest approximate match of a substring centered around the search_anchor in the target_text. Given this search substring and the approximately matched target substring, it looks for the best possible (hopefully exact) match containing the search_anchor between the search substring and the target substring by steadily reducing the size of the substrings. With this best possible (hopefully exact) match, it can then locate the search_anchor in this target substring; it retuns this target_anchor, which is the index of the search_anchor in the target_text.
#
# Return value: An (almost) exactly-matching location in the target document, or -1 if not found.
def find_approx_text_in_target(
      search_text,
      # The text composing the entire source document in which the search string resides.
      search_anchor,
      # A location in the source document which should be found in the target document.
      target_text,
      # The target text in which the search will be performed.
      search_range=40,
      # The radius of the substring around the search_anchor that will be approximately matched in the target_text: a value of 10 produces a length-20 substring (10 characters before the anchor, and 10 after). 
      step_size=1):
      # When searching for a best possible match, this specifies the number of characters to remove from the substrings. It must be a minimum of 1.
    #
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
##        print("No unique match found.")
##        with codecs.open('search_log.txt', 'w', encoding = 'utf-8') as f:
##            f.write("No unique match found.\n" + search_text[begin:end] + '\n\n\n\n' + target_text)
        return -1
#
# Search for an exact match between the search_anchor substring and the target_text approximate match
# --------------------------------------------------------------------------------------------------------
    # Record this initial match cost (which measures the difference between the source and target substrings). Perform all future searches only within the source and target substrings found in this search.
    min_cost = match.cost
    min_cost_begin = begin
    min_cost_end = end
    # For debug logging
 ##   log_begin = begin
 ##   log_end = end

    # If we have an exact match, need to define this, since the while loops won't (both will fall through without being evaluated). We're 0 characters forward from the begin_in_target point before we do any additional search refinements.
    begin_in_target_substr = 0

# Look for an exact match to the left of the anchor
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Reduce the left search radius, looking for better match. Keep the best possible match.
#
    # While the search radius to the left of the anchor > 0 and the cost > 0:
##    print('Searching right radius')
    while (end > search_anchor) and (min_cost > 0):

        # Decrease the left search radius by step_size and approximate search again.
        #
        # Note that (end - search_anchor)/2 == 0 when end = search_anchor + 1, causing infinite looping. The max fixes this case.
        end -= max((end - search_anchor) - step_size, 1)
        match, begin_in_target_substr, end_in_target_substr = \
            find_approx_text(search_text[begin:end],
                             target_text[begin_in_target:end_in_target])

        # If there are multiple matches, undo this search radius change and exit. This is the lowest achievable cost.
        if not match:
            break

        # If the cost has decreased, record this new cost and its associated left search radius.
        if match.cost < min_cost:
            min_cost = match.cost
            min_cost_end = end

# Look for an exact match to the right of the anchor
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # Repeat the above loop for the right search radius.
##    print('Searching left radius')
    while (begin < search_anchor) and (min_cost > 0):

        # Decrease the right search radius by step_size and approximate search again.
        begin += max((search_anchor - begin) - step_size, 1)
        match, begin_in_target_substr, end_in_target_substr = \
            find_approx_text(search_text[begin:min_cost_end],
                             target_text[begin_in_target:end_in_target])

        # If there are multiple matches, undo this search radius change and exit. This is the lowest achievable cost.
        if not match:
            break

        # If the cost has decreased, record this new cost and its associated left search radius.
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
    # Make sure the result lies within the bounds of target_text. Since we return a cursor position, an offset of len(target_text), meaning the end of target_text, is valid.
    return min(len(target_text), max(0, offset))
