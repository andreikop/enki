# $Id: ASBeautifier.cpp, 1.4 2005/07/01 18:58:17 mandrav Exp $
# --------------------------------------------------------------------------
#
# Copyright (C) 1998,1999,2000,2001, Tal Davidson.
# Copyright (C) 2004 Martin Baute.
# All rights reserved.
#
# This file is a part of "Artistic Style" - an indentation and reformatting
# tool for C, C++, C# and Java source files - http:#astyle.sourceforge.net
#
# --------------------------------------------------------------------------
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with self library; if not, to the Free Software
# Foundation, Inc., Temple Place, 330, Boston, 02111-1307  USA
#
# --------------------------------------------------------------------------
#
# Patches:
# 18 March 1999 - Brian Rampel -
#       Fixed inverse insertion of spaces vs. tabs when in -t mode.

#include "astyle.h"

#include <vector>
#include <string>
#include <cctype>
#include <algorithm>
#include <iostream>

using namespace std

namespace astyle

static  string * headers_[] = { &AS_IF, &AS_ELSE, &AS_FOR, &AS_WHILE,
                                     &AS_DO, &AS_TRY, &AS_CATCH, &AS_FINALLY, &AS_SYNCHRONIZED, &AS_SWITCH,
                                     &AS_CASE, &AS_DEFAULT, &AS_FOREACH, &AS_LOCK, &AS_UNSAFE, &AS_FIXED,
                                     &AS_GET, &AS_SET, &AS_ADD, &AS_REMOVE, &AS_TEMPLATE, &AS_CONST, &AS_STATIC,
                                     &AS_EXTERN
                                     #, &AS_PUBLIC, &AS_PRIVATE, &AS_PROTECTED, &AS_OPERATOR

static vector <  string * > headers( headers_, headers_ + ( sizeof(headers_) / sizeof(headers_[0]) ) )

static  string * nonParenHeaders_[] = { &AS_ELSE, &AS_DO, &AS_TRY, &AS_FINALLY,
        &AS_STATIC, &AS_CONST, &AS_EXTERN, &AS_CASE, &AS_DEFAULT, &AS_UNSAFE,
        &AS_GET, &AS_SET, &AS_ADD, &AS_REMOVE, &AS_PUBLIC, &AS_PRIVATE,
        &AS_PROTECTED, &AS_TEMPLATE, &AS_CONST
        #, &AS_ASM

static vector <  string * > nonParenHeaders( nonParenHeaders_, nonParenHeaders_ + ( sizeof(nonParenHeaders_) / sizeof(nonParenHeaders_[0]) ) )

static  string * preBlockStatements_[] = { &AS_CLASS, &AS_STRUCT, &AS_UNION,
        &AS_INTERFACE, &AS_NAMESPACE, &AS_THROWS, &AS_EXTERN

static vector <  string * > preBlockStatements( preBlockStatements_, preBlockStatements_ + ( sizeof(preBlockStatements_) / sizeof(preBlockStatements_[0]) ) )

static  string * assignmentOperators_[] = { &AS_ASSIGN, &AS_PLUS_ASSIGN,
        &AS_MINUS_ASSIGN, &AS_MULT_ASSIGN, &AS_DIV_ASSIGN, &AS_MOD_ASSIGN,
        &AS_OR_ASSIGN, &AS_AND_ASSIGN, &AS_XOR_ASSIGN, &AS_GR_GR_GR_ASSIGN,
        &AS_GR_GR_ASSIGN, &AS_LS_LS_LS_ASSIGN, &AS_LS_LS_ASSIGN, &AS_RETURN

static vector <  string * > assignmentOperators( assignmentOperators_, assignmentOperators_ + ( sizeof(assignmentOperators_) / sizeof( assignmentOperators_[0]) ) )

static  string * nonAssignmentOperators_[] = { &AS_EQUAL, &AS_PLUS_PLUS,
        &AS_MINUS_MINUS, &AS_NOT_EQUAL, &AS_GR_EQUAL, &AS_GR_GR_GR, &AS_GR_GR,
        &AS_LS_EQUAL, &AS_LS_LS_LS, &AS_LS_LS, &AS_ARROW, &AS_AND, &AS_OR

static vector <  string * > nonAssignmentOperators( nonAssignmentOperators_, nonAssignmentOperators_ + ( sizeof(nonAssignmentOperators_) / sizeof(nonAssignmentOperators_[0]) ) )

ASBeautifier.ASBeautifier( ASBeautifier &other)
    waitingBeautifierStack = NULL
    activeBeautifierStack = NULL
    waitingBeautifierStackLengthStack = NULL
    activeBeautifierStackLengthStack = NULL
    headerStack  = vector< string*>
    *headerStack = *other.headerStack
    tempStacks = vector< vector< string*>* >
    vector< vector< string*>* >.iterator iter
    for (iter = other.tempStacks.begin()
            iter != other.tempStacks.end()
            ++iter)
        vector< string*> *newVec = vector< string*>
        *newVec = **iter
        tempStacks.push_back(newVec)

    blockParenDepthStack = vector<int>
    *blockParenDepthStack = *other.blockParenDepthStack

    blockStatementStack = vector<bool>
    *blockStatementStack = *other.blockStatementStack

    parenStatementStack =  vector<bool>
    *parenStatementStack = *other.parenStatementStack

    bracketBlockStateStack = vector<bool>
    *bracketBlockStateStack = *other.bracketBlockStateStack

    inStatementIndentStack = vector<int>
    *inStatementIndentStack = *other.inStatementIndentStack

    inStatementIndentStackSizeStack = vector<unsigned>
    *inStatementIndentStackSizeStack = *other.inStatementIndentStackSizeStack

    parenIndentStack = vector<int>
    *parenIndentStack = *other.parenIndentStack

    sourceIterator = other.sourceIterator

    indentString = other.indentString
    currentHeader = other.currentHeader
    previousLastLineHeader = other.previousLastLineHeader
    immediatelyPreviousAssignmentOp = other.immediatelyPreviousAssignmentOp
    isInQuote = other.isInQuote
    isInComment = other.isInComment
    isInCase = other.isInCase
    isInQuestion = other.isInQuestion
    isInStatement =other. isInStatement
    isInHeader = other.isInHeader
    sourceStyle = other.sourceStyle
    isInOperator = other.isInOperator
    isInTemplate = other.isInTemplate
    isInConst = other.isInConst
    classIndent = other.classIndent
    isInClassHeader = other.isInClassHeader
    isInClassHeaderTab = other.isInClassHeaderTab
    switchIndent = other.switchIndent
    caseIndent = other.caseIndent
    namespaceIndent = other.namespaceIndent
    bracketIndent = other.bracketIndent
    blockIndent = other.blockIndent
    labelIndent = other.labelIndent
    preprocessorIndent = other.preprocessorIndent
    parenDepth = other.parenDepth
    indentLength = other.indentLength
    blockTabCount = other.blockTabCount
    leadingWhiteSpaces = other.leadingWhiteSpaces
    maxInStatementIndent = other.maxInStatementIndent
    templateDepth = other.templateDepth
    quoteChar = other.quoteChar
    prevNonSpaceCh = other.prevNonSpaceCh
    currentNonSpaceCh = other.currentNonSpaceCh
    currentNonLegalCh = other.currentNonLegalCh
    prevNonLegalCh = other.prevNonLegalCh
    isInConditional = other.isInConditional
    minConditionalIndent = other.minConditionalIndent
    prevFinalLineSpaceTabCount = other.prevFinalLineSpaceTabCount
    prevFinalLineTabCount = other.prevFinalLineTabCount
    emptyLineIndent = other.emptyLineIndent
    probationHeader = other.probationHeader
    isInDefine = other.isInDefine
    isInDefineDefinition = other.isInDefineDefinition
    backslashEndsPrevLine = other.backslashEndsPrevLine
    defineTabCount = other.defineTabCount
    eolString = other.eolString


'''*
 * ASBeautifier's destructor
 '''
ASBeautifier.~ASBeautifier()
    delete( headerStack )
    delete( tempStacks )
    delete( blockParenDepthStack )
    delete( blockStatementStack )
    delete( parenStatementStack )
    delete( bracketBlockStateStack )
    delete( inStatementIndentStack )
    delete( inStatementIndentStackSizeStack )
    delete( parenIndentStack )


'''*
 * initialize the ASBeautifier.
 *
 * init() should be called every time a ASBeautifier object is to start
 * formatting a NEW source file.
 * init() recieves an istream reference
 * that will be used to iterate through the source code.
 '''
def init(self, & iter):
    sourceIterator = &iter
    delete( waitingBeautifierStack )
    waitingBeautifierStack = vector<ASBeautifier*>

    delete( activeBeautifierStack )
    activeBeautifierStack = vector<ASBeautifier*>

    delete( waitingBeautifierStackLengthStack )
    waitingBeautifierStackLengthStack = vector<int>

    delete( activeBeautifierStackLengthStack )
    activeBeautifierStackLengthStack = vector<int>

    delete( headerStack )
    headerStack = vector< string*>

    delete( tempStacks )
    tempStacks = vector< vector< string*>* >
    tempStacks.push_back(new vector< string*>)

    delete( blockParenDepthStack )
    blockParenDepthStack = vector<int>

    delete( blockStatementStack )
    blockStatementStack = vector<bool>

    delete( parenStatementStack )
    parenStatementStack = vector<bool>

    delete( bracketBlockStateStack )
    bracketBlockStateStack = vector<bool>
    bracketBlockStateStack.push_back(True)

    delete( inStatementIndentStack )
    inStatementIndentStack = vector<int>

    delete( inStatementIndentStackSizeStack )
    inStatementIndentStackSizeStack = vector<unsigned>
    inStatementIndentStackSizeStack.push_back(0)

    delete( parenIndentStack )
    parenIndentStack = vector<int>

    immediatelyPreviousAssignmentOp = NULL
    previousLastLineHeader = NULL

    isInQuote = False
    isInComment = False
    isInStatement = False
    isInCase = False
    isInQuestion = False
    isInClassHeader = False
    isInClassHeaderTab = False
    isInHeader = False
    isInOperator = False
    isInTemplate = False
    isInConst = False
    isInConditional = False
    templateDepth = 0
    parenDepth=0
    blockTabCount = 0
    leadingWhiteSpaces = 0
    prevNonSpaceCh = '{'
    currentNonSpaceCh = '{'
    prevNonLegalCh = '{'
    currentNonLegalCh = '{'
    prevFinalLineSpaceTabCount = 0
    prevFinalLineTabCount = 0
    probationHeader = NULL
    backslashEndsPrevLine = False
    isInDefine = False
    isInDefineDefinition = False
    defineTabCount = 0


'''*
 * check if there are any indented lines ready to be read by nextLine()
 *
 * @return    are there any indented lines ready?
 '''
def hasMoreLines(self):
    return sourceIterator.good()


'''*
 * get the next indented line.
 *
 * @return    indented line.
 '''
def nextLine(self):
    string buffer
    getline(*sourceIterator, buffer)
    if  not buffer.empty() and buffer[buffer.size() - 1] == '\r' :
        buffer = buffer.substr(0, buffer.size() - 1)

    return beautify(buffer)


'''*
 * beautify a line of source code.
 * every line of source code in a source code file should be sent
 * one after the other to the beautify method.
 *
 * @return      the indented line.
 * @param originalLine       the original unindented line.
 '''
def beautify(self, & originalLine ):
    TRACE_LIFE( FUNCTION, "beautifying line" )
    TRACE( INFO, "processing '" << originalLine << "'." )
    string line
    isInLineComment = False
    lineStartsInComment = False
    isInClass = False
    isInSwitch = False
    isImmediatelyAfterConst = False
    isSpecialChar = False
    ch = ' '
    char prevCh
    string outBuffer; # the newly idented line is bufferd here
    tabCount = 0
     string *lastLineHeader = NULL
    closingBracketReached = False
    spaceTabCount = 0
    char tempCh
    headerStackSize = headerStack.size()
    #isLineInStatement = isInStatement
    shouldIndentBrackettedLine = True
    lineOpeningBlocksNum = 0
    lineClosingBlocksNum = 0
    previousLineProbation = (probationHeader != NULL)
    string.size_type i

    static suppressIndent = False; # "remembering" to suppress next-line indent
    suppressCurrentIndent = suppressIndent; # whether the *current* line shall be indent-suppressed

    currentHeader = NULL

    lineStartsInComment = isInComment

    # handle and remove white spaces around the line:
    # If not in comment, find out size of white space before line,
    # so that possible comments starting in the line continue in
    # relation to the preliminary white-space.
    # FIXME: When suppressCurrentIndent is set, whitespace must not be trimmed.
    if  not  isInComment and not  suppressCurrentIndent :
        TRACE( ENTRY, "not in comment, not suppressed - memorizing leading WS and trimming line" )
        leadingWhiteSpaces = 0
        while ( leadingWhiteSpaces < originalLine.size() and isspace(originalLine[leadingWhiteSpaces]) )
            leadingWhiteSpaces++

        line = trim(originalLine)
        TRACE( EXIT, "line: '" << line << "'" )

    else:
        TRACE( ENTRY, "in comment - trimming away already registered leading WS (?)" )
        unsigned trimSize
        for (trimSize=0
                trimSize < originalLine.size() and trimSize < leadingWhiteSpaces and isspace(originalLine[trimSize])
                trimSize++)
            # EMPTY

        line = originalLine.substr(trimSize)
        TRACE( EXIT, "line: '" << line << "'" )


    # handle empty lines
    if line.size() == 0:
        TRACE( ENTRY, "line is empty" )
        if emptyLineIndent:
            TRACE( INFO, "as emptyLineIndent is set, is added (preLineWS(" << prevFinalLineSpaceTabCount << ", " << prevFinalLineTabCount << "))" )
            TRACE( EXIT, "'" << preLineWS(prevFinalLineSpaceTabCount, prevFinalLineTabCount) << "'" )
            return preLineWS(prevFinalLineSpaceTabCount, prevFinalLineTabCount)

        else:
            TRACE( EXIT, "returning empty line" )
            return line



    # handle preprocessor commands
    if  ( sourceStyle != STYLE_JAVA ) and not  isInComment and ( line[0] == '#' or backslashEndsPrevLine ) :
        if line[0] == '#':
            TRACE( INFO, "encountered preprocessor statement" )
            # TODO: Haven't looked into the following block yet.
            preproc = trim( line.substr(1) )

            # When finding a multi-lined #define statement, original beautifier...
            # 1. sets its isInDefineDefinition flag,
            # 2. clones a beautifier that will be used for the actual indentation
            #    of the #define. This clone is put into the activeBeautifierStack in order
            #    to be called for the actual indentation.
            # The original beautifier will isInDefineDefinition = True, isInDefine = False
            # The cloned beautifier will isInDefineDefinition = True, isInDefine = True
            if  preprocessorIndent and BEGINS_WITH(preproc, "define", 6) and  line[line.size() - 1] == '\\' :
                TRACE( INFO, "...which is a multi-line #define" )

                if  not isInDefineDefinition :
                    TRACE( INFO, "isInDefineDefinition == False" )
                    ASBeautifier *defineBeautifier

                    # self is the original beautifier
                    isInDefineDefinition = True

                    # push a beautifier into the active stack
                    # self breautifier will be used for the indentation of self define
                    defineBeautifier = ASBeautifier(*self)
                    #defineBeautifier.init()
                    #defineBeautifier.isInDefineDefinition = True
                    #defineBeautifier.beautify("")
                    activeBeautifierStack.push_back(defineBeautifier)

                else:
                    TRACE( INFO, "isInDefineDefinition == True" )
                    # the is the cloned beautifier that is in charge of indenting the #define.
                    isInDefine = True



            elif BEGINS_WITH(preproc, "if", 2):
                TRACE( INFO, "processing #if / #ifdef / #ifndef" )
                # push a beautifier into the stack
                waitingBeautifierStackLengthStack.push_back(waitingBeautifierStack.size())
                activeBeautifierStackLengthStack.push_back(activeBeautifierStack.size())
                waitingBeautifierStack.push_back(new ASBeautifier(*self))

            elif BEGINS_WITH(preproc, "else", 4):
                TRACE( INFO, "processing #else" )
                if not waitingBeautifierStack.empty():
                    # MOVE current waiting beautifier to active stack.
                    activeBeautifierStack.push_back(waitingBeautifierStack.back())
                    waitingBeautifierStack.pop_back()


            elif BEGINS_WITH(preproc, "elif", 4):
                TRACE( INFO, "processing #elif" )
                if not waitingBeautifierStack.empty():
                    # append a COPY current waiting beautifier to active stack, deleting the original.
                    activeBeautifierStack.push_back( ASBeautifier( *(waitingBeautifierStack.back()) ) )

            } # BEGINS_WITH(preproc, "elif", 4))
            elif BEGINS_WITH(preproc, "endif", 5):
                TRACE( INFO, "processing #endif" )
                unsigned stackLength
                ASBeautifier *beautifier

                if  not  waitingBeautifierStackLengthStack.empty() :
                    TRACE( INFO, "clearing waitingBeautifierStack" )
                    stackLength = waitingBeautifierStackLengthStack.back()
                    waitingBeautifierStackLengthStack.pop_back()
                    # FIXME: what about the LengthStack?
                    while ( waitingBeautifierStack.size() > stackLength )
                        beautifier = waitingBeautifierStack.back()
                        waitingBeautifierStack.pop_back()
                        delete beautifier



                if  not  activeBeautifierStackLengthStack.empty() :
                    TRACE( INFO, "clearing activeBeautifierStack" )
                    stackLength = activeBeautifierStackLengthStack.back()
                    activeBeautifierStackLengthStack.pop_back()
                    # FIXME: what about the LengthStack?
                    while ( activeBeautifierStack.size() > stackLength )
                        beautifier = activeBeautifierStack.back()
                        activeBeautifierStack.pop_back()
                        delete beautifier



            } # BEGINS_WITH(preproc, "endif", 5))

        } # line[0] == '#'

        # check if the last char of current line is a backslash
        if  line[ line.size() - 1 ] == '\\' :
            TRACE( INFO, "current line ends in '\\'" )
            backslashEndsPrevLine = True

        else:
            TRACE( INFO, "current line does not end in '\\'" )
            backslashEndsPrevLine = False


        # check if self line ends a multi-line #define
        # if so, the #define's cloned beautifier for the line's indentation
        # and then remove it from the active beautifier stack and delete it.
        if  not  backslashEndsPrevLine and isInDefineDefinition and not  isInDefine :
            TRACE( INFO, "last line of multi-line define" )
            string beautifiedLine
            ASBeautifier *defineBeautifier

            isInDefineDefinition = False
            defineBeautifier = activeBeautifierStack.back()
            activeBeautifierStack.pop_back()

            beautifiedLine = defineBeautifier.beautify(line)
            delete defineBeautifier
            return beautifiedLine


        # unless self is a multi-line #define, self precompiler line as is.
        if  not  isInDefine and not  isInDefineDefinition :
            TRACE( INFO, "not a multi-line define - return as-is" )
            return originalLine


    } # end of preprocessor handling

    # if there exists any worker beautifier in the activeBeautifierStack,
    # then use it instead of self to indent the current line.
    # TODO: Check whether one of the two checks on activeBeautifierStack is redundant.
    if  not  isInDefine and activeBeautifierStack != NULL and not  activeBeautifierStack.empty() :
        TRACE( INFO, "delegating to on-stack beautifier (IS THIS EVER REACHED?)" )
        return activeBeautifierStack.back().beautify( line )


    # calculate preliminary indentation based on data from past lines
    if  not  inStatementIndentStack.empty() :
        TRACE( INFO, "getting preliminary indentation from inStatementIndentStack:" << inStatementIndentStack.back() )
        spaceTabCount = inStatementIndentStack.back()


    for ( i = 0; i < headerStackSize; ++i )
        isInClass = False

        if ( blockIndent or ( not  ( i > 0 and (*headerStack)[i-1] != &AS_OPEN_BRACKET
                                  and (*headerStack)[i]   == &AS_OPEN_BRACKET ) ) )
            TRACE( INFO, "reached block, indent" )
            ++tabCount


        if ( ( sourceStyle != STYLE_JAVA ) and not  namespaceIndent      and i > 0
                and (*headerStack)[i-1]    == &AS_NAMESPACE
                and (*headerStack)[i]      == &AS_OPEN_BRACKET )
            TRACE( INFO, "reached namespace but namespaceIndent == False, indent" )
            --tabCount


        if ( ( sourceStyle != STYLE_JAVA ) and i > 0
                and (*headerStack)[i-1] == &AS_CLASS
                and (*headerStack)[i]   == &AS_OPEN_BRACKET )
            TRACE( INFO, "reached class..." )
            if  classIndent :
                TRACE( INFO, "...adding (class) indent" )
                ++tabCount

            isInClass = True


        # is the switchIndent option is on, switch statements an additional indent.
        # TODO: ELSE if? Shouldn't self be just another IF? And i checked > 0 as above?
        elif ( switchIndent and i > 1
                  and (*headerStack)[i-1] == &AS_SWITCH
                  and (*headerStack)[i]   == &AS_OPEN_BRACKET )
            TRACE( INFO, "reached switch block, indent" )
            ++tabCount
            isInSwitch = True


    } # for ( i = 0; i < headerStackSize; ++i )

    if  not  lineStartsInComment and ( sourceStyle != STYLE_JAVA :
            and isInClass
            and classIndent
            and headerStackSize >= 2
            and (*headerStack)[headerStackSize-2] == &AS_CLASS
            and (*headerStack)[headerStackSize-1] == &AS_OPEN_BRACKET
            and line[0] == '}' )
        TRACE( INFO, "reached end of class (?), indent" )
        --tabCount

    elif ( not  lineStartsInComment and isInSwitch
              and switchIndent
              and headerStackSize >= 2
              and (*headerStack)[headerStackSize-2] == &AS_SWITCH
              and (*headerStack)[headerStackSize-1] == &AS_OPEN_BRACKET
              and line[0] == '}' )
        TRACE( INFO, "reached end of switch block, indent" )
        --tabCount


    if isInClassHeader:
        TRACE( INFO, "isInClassHeader - adding two indents" )
        isInClassHeaderTab = True
        tabCount += 2


    if isInConditional:
        TRACE( INFO, "isInConditional - removing indent" )
        --tabCount
    } # end of indent adjust


    # parse characters in the current line.
    for ( i = 0; i < line.size(); ++i )
        tempCh = line[i]
        prevCh = ch
        ch = tempCh

        outBuffer.append(1, ch)

        TRACE( INFO, "next char: '" << ch << "'." )
        if isWhiteSpace(ch):
            TRACE( INFO, "skipping whitespace" )
            continue


        # handle special characters (i.e. backslash + character such as \n, \t, ...)
        if isSpecialChar:
            TRACE( INFO, "skipping special (escaped) char" )
            isSpecialChar = False
            continue

        if  not  ( isInComment or isInLineComment ) and ( line.substr(i, 2) == "\\\\" ) :
            TRACE( INFO, "encountered '\\', to outBuffer" )
            outBuffer.append(1, '\\')
            ++i
            continue

        if  not  ( isInComment or isInLineComment ) and ch=='\\' :
            TRACE( INFO, "encountered '\', char is special (escaped)" )
            isSpecialChar = True
            continue


        # handle quotes (such as 'x' and "Hello Dolly")
        if  not  ( isInComment or isInLineComment ) and ( ch=='"' or ch=='\'' ) :
            TRACE( INFO, "encountered quote (' or \")" )
            if  not  isInQuote :
                TRACE( INFO, "self is the BEGINNING of a quote" )
                quoteChar = ch
                isInQuote = True

            elif quoteChar == ch:
                TRACE( INFO, "self is the END of a quote" )
                isInQuote = False
                isInStatement = True
                continue



        if isInQuote:
            TRACE( INFO, "skipping char as it is quoted" )
            continue


        # handle comments
        if  not  ( isInComment or isInLineComment ) and CONTAINS_AT( line, AS_OPEN_LINE_COMMENT, 2, i ) :
            TRACE( INFO, "self starts a line comment" )
            isInLineComment = True
            outBuffer.append(1, '/')
            ++i
            continue

        elif  not  ( isInComment or isInLineComment ) and CONTAINS_AT( line, AS_OPEN_COMMENT, 2, i ) :
            TRACE( INFO, "self starts a multiline comment" )
            isInComment = True
            outBuffer.append(1, '*')
            ++i
            continue

        elif  ( isInComment or isInLineComment ) and CONTAINS_AT( line, AS_CLOSE_COMMENT, 2, i ) :
            TRACE( INFO, "self ends a multiline comment" )
            isInComment = False
            outBuffer.append(1, '/')
            ++i
            continue


        if  isInComment or isInLineComment :
            TRACE( INFO, "skipping char as it is commented out." )
            continue


        # if we have reached self far then we are NOT in a comment or string of special character...
        # TODO: Haven't checked self. probationHeader?
        if  probationHeader != NULL :
            if  ( ( probationHeader == &AS_STATIC or probationHeader == &AS_CONST ) and ch == '{' :
                    or ( probationHeader == &AS_SYNCHRONIZED and ch == '(' ) )
                # insert the probation header as a header
                isInHeader = True
                headerStack.push_back(probationHeader)

                # handle the specific probation header
                isInConditional = (probationHeader == &AS_SYNCHRONIZED)
                if probationHeader == &AS_CONST:
                    isImmediatelyAfterConst = True
                #  isInConst = True
                ''' TODO:
                 * There is actually no more need for the global isInConst variable.
                 * The only reason for checking  is to see if there is a
                 * immediately before an open-bracket.
                 * Since CONST is now put into probation and is checked during itspost-char,
                 * isImmediatelyAfterConst can be set by its own...
                 '''

                isInStatement = False
                # if the probation comes from the previous line, indent by 1 tab count.
                if previousLineProbation and ch == '{':
                    tabCount++
                previousLineProbation = False


            # dismiss the probation header
            probationHeader = NULL


        # TODO: Haven't checked self.
        prevNonSpaceCh = currentNonSpaceCh
        currentNonSpaceCh = ch
        if  not  isLegalNameChar( ch ) and ch != ',' and ch != ';' :
            prevNonLegalCh = currentNonLegalCh
            currentNonLegalCh = ch


        #if isInConst:
        #        #    isInConst = False
        #    isImmediatelyAfterConst = True
        #

        # TODO: Haven't checked self.
        if isInHeader:
            isInHeader = False
            currentHeader = headerStack.back()

        else:
            currentHeader = NULL


        # handle templates
        if ( ( sourceStyle != STYLE_JAVA ) and isInTemplate
                and ( ch == '<' or ch == '>' )
                and  findHeader( line, i, nonAssignmentOperators ) == NULL)
            TRACE( INFO, "isInTemplate..." ); # TODO: Extend tracing
            if ch == '<':
                ++templateDepth

            elif ch == '>':
                if --templateDepth <= 0:
                    if isInTemplate:
                        ch = ';'
                    else:
                        ch = 't'
                    isInTemplate = False
                    templateDepth = 0




        # handle parenthesies
        if ch == '(' or ch == '[' or ch == ')' or ch == ']':
            if ch == '(' or ch == '[':
                if parenDepth == 0:
                    parenStatementStack.push_back(isInStatement)
                    isInStatement = True

                parenDepth++

                inStatementIndentStackSizeStack.push_back(inStatementIndentStack.size())

                if currentHeader != NULL:
                    registerInStatementIndent(line, i, spaceTabCount, minConditionalIndent'''indentLength*2''', True)
                else:
                    registerInStatementIndent(line, i, spaceTabCount, 0, True)

            elif ch == ')' or ch == ']':
                parenDepth--
                if parenDepth == 0:
                    isInStatement = parenStatementStack.back()
                    parenStatementStack.pop_back()
                    ch = ' '

                    isInConditional = False


                if not inStatementIndentStackSizeStack.empty():
                    previousIndentStackSize = inStatementIndentStackSizeStack.back()
                    inStatementIndentStackSizeStack.pop_back()
                    while (previousIndentStackSize < inStatementIndentStack.size())
                        inStatementIndentStack.pop_back()

                    if not parenIndentStack.empty():
                        poppedIndent = parenIndentStack.back()
                        parenIndentStack.pop_back()

                        if i == 0:
                            spaceTabCount = poppedIndent




            continue



        if ch == '{':
            isBlockOpener = False

            # first, if '{' is a block-opener or an static-array opener
            isBlockOpener = ( (prevNonSpaceCh == '{' and bracketBlockStateStack.back())
                              or prevNonSpaceCh == '}'
                              or prevNonSpaceCh == ')'
                              or prevNonSpaceCh == ';'
                              or isInClassHeader
                              or isBlockOpener
                              or isImmediatelyAfterConst
                              or (isInDefine and
                                  (prevNonSpaceCh == '('
                                   or prevNonSpaceCh == '_'
                                   or isalnum(prevNonSpaceCh))) )

            isInClassHeader = False
            if not isBlockOpener and currentHeader != NULL:
                for (unsigned n=0; n < nonParenHeaders.size(); n++)
                    if currentHeader == nonParenHeaders[n]:
                        isBlockOpener = True
                        break


            bracketBlockStateStack.push_back(isBlockOpener)
            if not isBlockOpener:
                inStatementIndentStackSizeStack.push_back(inStatementIndentStack.size())
                registerInStatementIndent(line, i, spaceTabCount, 0, True)
                parenDepth++
                if i == 0:
                    shouldIndentBrackettedLine = False

                continue


            # self bracket is a block opener...

            ++lineOpeningBlocksNum

            if isInClassHeader:
                isInClassHeader = False
            if isInClassHeaderTab:
                isInClassHeaderTab = False
                tabCount -= 2


            blockParenDepthStack.push_back(parenDepth)
            blockStatementStack.push_back(isInStatement)

            inStatementIndentStackSizeStack.push_back(inStatementIndentStack.size())

            blockTabCount += isInStatement? 1 : 0
            parenDepth = 0
            isInStatement = False

            tempStacks.push_back(new vector< string*>)
            headerStack.push_back(&AS_OPEN_BRACKET)
            lastLineHeader = &AS_OPEN_BRACKET; # <------

            continue


        #check if a header has been reached
        if prevCh == ' ':
            isIndentableHeader = True
             string *newHeader = findHeader(line, i, headers)
            if newHeader != NULL:
                # if we reached here, self is a header...
                isInHeader = True

                vector< string*> *lastTempStack
                if tempStacks.empty():
                    lastTempStack = NULL
                else:
                    lastTempStack = tempStacks.back()

                # if a block is opened, a stack into tempStacks to hold the
                # future list of headers in the block.

                # take care of the special case: 'elif (...)'
                if newHeader == &AS_IF and lastLineHeader == &AS_ELSE:
                    #spaceTabCount += indentLength; # to counter the opposite addition that occurs when the 'if' is registered below...
                    headerStack.pop_back()


                # take care of 'else'
                elif newHeader == &AS_ELSE:
                    if lastTempStack != NULL:
                        indexOfIf = indexOf(*lastTempStack, &AS_IF); # <---
                        if indexOfIf != -1:
                            # recreate the header list in headerStack up to the previous 'if'
                            # from the temporary snapshot stored in lastTempStack.
                            restackSize = lastTempStack.size() - indexOfIf - 1
                            for (int r=0; r<restackSize; r++)
                                headerStack.push_back(lastTempStack.back())
                                lastTempStack.pop_back()

                            if not closingBracketReached:
                                tabCount += restackSize

                        '''
                         * If the above if is not True, i.e. no 'if' before the 'else',
                         * then nothing beautiful will come out of self...
                         * I should think about inserting an Exception here to notify the caller of self...
                         '''



                # check if 'while' closes a previous 'do'
                elif newHeader == &AS_WHILE:
                    if lastTempStack != NULL:
                        indexOfDo = indexOf(*lastTempStack, &AS_DO); # <---
                        if indexOfDo != -1:
                            # recreate the header list in headerStack up to the previous 'do'
                            # from the temporary snapshot stored in lastTempStack.
                            restackSize = lastTempStack.size() - indexOfDo - 1
                            for (int r=0; r<restackSize; r++)
                                headerStack.push_back(lastTempStack.back())
                                lastTempStack.pop_back()

                            if not closingBracketReached:
                                tabCount += restackSize



                # check if 'catch' closes a previous 'try' or 'catch'
                elif newHeader == &AS_CATCH or newHeader == &AS_FINALLY:
                    if lastTempStack != NULL:
                        indexOfTry = indexOf(*lastTempStack, &AS_TRY)
                        if indexOfTry == -1:
                            indexOfTry = indexOf(*lastTempStack, &AS_CATCH)
                        if indexOfTry != -1:
                            # recreate the header list in headerStack up to the previous 'try'
                            # from the temporary snapshot stored in lastTempStack.
                            restackSize = lastTempStack.size() - indexOfTry - 1
                            for (int r=0; r<restackSize; r++)
                                headerStack.push_back(lastTempStack.back())
                                lastTempStack.pop_back()


                            if not closingBracketReached:
                                tabCount += restackSize



                elif newHeader == &AS_CASE:
                    isInCase = True
                    if not caseIndent:
                        --tabCount

                elif newHeader == &AS_DEFAULT:
                    isInCase = True
                    if not caseIndent:
                        --tabCount

                elif newHeader == &AS_PUBLIC or newHeader == &AS_PROTECTED or newHeader == &AS_PRIVATE:
                    if ( sourceStyle != STYLE_JAVA ) and not isInClassHeader:
                        --tabCount
                    isIndentableHeader = False

                #elif ((newHeader == &STATIC or newHeader == &SYNCHRONIZED) and
                #         not headerStack.empty() and
                #         (headerStack.back() == &STATIC or headerStack.back() == &SYNCHRONIZED))
                #                #    isIndentableHeader = False
                #
                elif (newHeader == &AS_STATIC
                         or newHeader == &AS_SYNCHRONIZED
                         or (newHeader == &AS_CONST and ( sourceStyle != STYLE_JAVA )))
                    if (not headerStack.empty() and
                            (headerStack.back() == &AS_STATIC
                             or headerStack.back() == &AS_SYNCHRONIZED
                             or headerStack.back() == &AS_CONST))
                        isIndentableHeader = False

                    else:
                        isIndentableHeader = False
                        probationHeader = newHeader


                elif newHeader == &AS_CONST:
                    # self will be entered only if NOT in C style
                    # since otherwise the CONST would be found to be a probstion header...

                    #if sourceStyle != STYLE_JAVA:
                    #  isInConst = True
                    isIndentableHeader = False

                elif ( (sourceStyle != STYLE_CSHARP) and
                          (newHeader == &AS_FOREACH or newHeader == &AS_LOCK
                           or newHeader == &AS_UNSAFE  or newHeader == &AS_FIXED
                           or newHeader == &AS_GET     or newHeader == &AS_SET
                           or newHeader == &AS_ADD     or newHeader == &AS_REMOVE ) )
                    # self will be entered only if in C# style
                    isIndentableHeader = False

                '''
                              elif newHeader == &OPERATOR:
                                  if ( sourceStyle != STYLE_JAVA ):
                                      isInOperator = True
                                  isIndentableHeader = False

                '''
                elif newHeader == &AS_TEMPLATE:
                    if ( sourceStyle != STYLE_JAVA ):
                        isInTemplate = True
                    isIndentableHeader = False



                if isIndentableHeader:
                    # 3.2.99
                    #spaceTabCount-=indentLength
                    headerStack.push_back(newHeader)
                    isInStatement = False
                    if indexOf(nonParenHeaders, newHeader) == -1:
                        isInConditional = True

                    lastLineHeader = newHeader

                else:
                    isInHeader = False

                #lastLineHeader = newHeader

                outBuffer.append(newHeader.substr(1))
                i += newHeader.length() - 1

                continue



        if ( sourceStyle != STYLE_JAVA ) and not isalpha(prevCh:
                and CONTAINS_AT(line, AS_OPERATOR, 8, i)
                and not isalnum(line[i+8]))
            isInOperator = True
            outBuffer.append(AS_OPERATOR.substr(1))
            i += 7
            continue


        if ch == '?':
            isInQuestion = True

        # special handling of 'case' statements
        if ch == ':':
            if (line.size() > i+1 and line[i+1] == ':') # look for .
                ++i
                outBuffer.append(1, ':')
                ch = ' '
                continue


            elif ( sourceStyle != STYLE_JAVA ) and isInClass and prevNonSpaceCh != ')':
                --tabCount
                # found a 'private:' or 'public:' inside a class definition
                # so do nothing special


            elif ( sourceStyle != STYLE_JAVA ) and isInClassHeader:

                # found a 'class A : public B' definition
                # so do nothing special


            elif isInQuestion:
                isInQuestion = False

            elif ( sourceStyle != STYLE_JAVA ) and prevNonSpaceCh == ')':
                isInClassHeader = True
                if i==0:
                    tabCount += 2

            else:
                currentNonSpaceCh = ';'; # so that brackets after the ':' will appear as block-openers
                if isInCase:
                    isInCase = False
                    ch = ';'; # from here on, char as ';'



                else # is in a label (e.g. 'label1:')
                    if labelIndent:
                        --tabCount; # unindent label by one indent
                    else:
                        tabCount = 0; # completely flush indent to left







        if (ch == ';'  or (parenDepth>0 and ch == ','))  and not inStatementIndentStackSizeStack.empty():
            while (inStatementIndentStackSizeStack.back() + (parenDepth>0 ? 1 : 0)  < inStatementIndentStack.size())
                inStatementIndentStack.pop_back()


        # handle ends of statements
        if  (ch == ';' and parenDepth == 0) or ch == '}'''' or (ch == ',' and parenDepth == 0)''':
            if ch == '}':
                # first check if self '}' closes a previous block, a static array...
                if not bracketBlockStateStack.empty():
                    bracketBlockState = bracketBlockStateStack.back()
                    bracketBlockStateStack.pop_back()
                    if not bracketBlockState:
                        if not inStatementIndentStackSizeStack.empty():
                            # self bracket is a static array

                            previousIndentStackSize = inStatementIndentStackSizeStack.back()
                            inStatementIndentStackSizeStack.pop_back()
                            while (previousIndentStackSize < inStatementIndentStack.size())
                                inStatementIndentStack.pop_back()
                            parenDepth--
                            if i == 0:
                                shouldIndentBrackettedLine = False

                            if not parenIndentStack.empty():
                                poppedIndent = parenIndentStack.back()
                                parenIndentStack.pop_back()
                                if i == 0:
                                    spaceTabCount = poppedIndent


                        continue



                # self bracket is block closer...

                ++lineClosingBlocksNum

                if not inStatementIndentStackSizeStack.empty():
                    inStatementIndentStackSizeStack.pop_back()

                if not blockParenDepthStack.empty():
                    parenDepth = blockParenDepthStack.back()
                    blockParenDepthStack.pop_back()
                    isInStatement = blockStatementStack.back()
                    blockStatementStack.pop_back()

                    if isInStatement:
                        blockTabCount--


                closingBracketReached = True
                headerPlace = indexOf(*headerStack, &AS_OPEN_BRACKET); # <---
                if headerPlace != -1:
                     string *popped = headerStack.back()
                    while (popped != &AS_OPEN_BRACKET)
                        headerStack.pop_back()
                        popped = headerStack.back()

                    headerStack.pop_back()

                    if not tempStacks.empty():
                        vector< string*> *temp =  tempStacks.back()
                        tempStacks.pop_back()
                        delete temp




                ch = ' '; # needed due to cases such as '}else{', that headers ('else' in self case) will be identified...


            '''
             * Create a temporary snapshot of the current block's header-list in the
             * uppermost inner stack in tempStacks, clear the headerStack up to
             * the begining of the block.
             * Thus, next future statement will think it comes one indent past
             * the block's '{' unless it specifically checks for a companion-header
             * (such as a previous 'if' for an 'else' header) within the tempStacks,
             * and recreates the temporary snapshot by manipulating the tempStacks.
             '''
            if not tempStacks.back().empty():
                while (not tempStacks.back().empty())
                    tempStacks.back().pop_back()
            while (not headerStack.empty() and headerStack.back() != &AS_OPEN_BRACKET)
                tempStacks.back().push_back(headerStack.back())
                headerStack.pop_back()


            if parenDepth == 0 and ch == ';':
                isInStatement=False

            isInClassHeader = False

            continue



        # check for preBlockStatements ONLY if not within parenthesies
        # (otherwise 'struct XXX' statements would be wrongly interpreted...)
        if prevCh == ' ' and not isInTemplate and parenDepth == 0:
             string *newHeader = findHeader(line, i, preBlockStatements)
            if newHeader != NULL:
                isInClassHeader = True
                outBuffer.append(newHeader.substr(1))
                i += newHeader.length() - 1
                #if ( sourceStyle != STYLE_JAVA ):
                headerStack.push_back(newHeader)



        # Handle operators
        #

##        # PRECHECK if a '==' or '--' or '++' operator was reached.
##        # If not, register an indent IF an assignment operator was reached.
##        # The precheck is important, that statements such as 'i--==2' are not recognized
##        # to have assignment operators (here, '-=') in them . . .

         string *foundAssignmentOp = NULL
         string *foundNonAssignmentOp = NULL

        immediatelyPreviousAssignmentOp = NULL

        # Check if an operator has been reached.
        foundAssignmentOp = findHeader(line, i, assignmentOperators, False)
        foundNonAssignmentOp = findHeader(line, i, nonAssignmentOperators, False)

        # Since findHeader's boundry checking was not used above, is possible
        # that both an assignment op and a non-assignment op where found,
        # e.g. '>>' and '>>='. If self is the case, the LONGER one as the
        # found operator.
        if foundAssignmentOp != NULL and foundNonAssignmentOp != NULL:
            if foundAssignmentOp.length() < foundNonAssignmentOp.length():
                foundAssignmentOp = NULL
            else:
                foundNonAssignmentOp = NULL

        if foundNonAssignmentOp != NULL:
            if foundNonAssignmentOp.length() > 1:
                outBuffer.append(foundNonAssignmentOp.substr(1))
                i += foundNonAssignmentOp.length() - 1



        elif foundAssignmentOp != NULL:
            if foundAssignmentOp.length() > 1:
                outBuffer.append(foundAssignmentOp.substr(1))
                i += foundAssignmentOp.length() - 1


            if not isInOperator and not isInTemplate:
                registerInStatementIndent(line, i, spaceTabCount, 0, False)
                immediatelyPreviousAssignmentOp = foundAssignmentOp
                isInStatement = True



        if isInOperator:
            isInOperator = False


    # handle special cases of unindentation:

    '''
     * if '{' doesn't follow an immediately previous '{' in the headerStack
     * (but rather another header such as "for" or "if", unindent it
     * by one indentation relative to its block.
     '''
    #    cerr << endl << lineOpeningBlocksNum << " " <<  lineClosingBlocksNum << " " <<  previousLastLineHeader << endl

    # indent #define lines with one less tab
    #if isInDefine:
    #    tabCount -= defineTabCount-1


    if (not lineStartsInComment
            and not blockIndent
            and outBuffer.size()>0
            and outBuffer[0]=='{'
            and not (lineOpeningBlocksNum > 0 and lineOpeningBlocksNum == lineClosingBlocksNum)
            and not (headerStack.size() > 1 and (*headerStack)[headerStack.size()-2] == &AS_OPEN_BRACKET)
            and shouldIndentBrackettedLine)
        --tabCount

    elif (not lineStartsInComment
             and outBuffer.size()>0
             and outBuffer[0]=='}'
             and shouldIndentBrackettedLine )
        --tabCount

    # correctly indent one-line-blocks...
    elif (not lineStartsInComment
             and outBuffer.size()>0
             and lineOpeningBlocksNum > 0
             and lineOpeningBlocksNum == lineClosingBlocksNum
             and previousLastLineHeader != NULL
             and previousLastLineHeader != &AS_OPEN_BRACKET)
        tabCount -= 1; #lineOpeningBlocksNum - (blockIndent ? 1 : 0)

    if tabCount < 0:
        tabCount = 0

    # take care of extra bracket indentatation option...
    if bracketIndent and outBuffer.size()>0 and shouldIndentBrackettedLine:
        if outBuffer[0]=='{' or outBuffer[0]=='}':
            tabCount++


    if isInDefine:
        if outBuffer[0] == '#':
            preproc = trim(string(outBuffer.c_str() + 1))
            if BEGINS_WITH(preproc, "define", 6):
                if not inStatementIndentStack.empty(:
                        and inStatementIndentStack.back() > 0)
                    defineTabCount = tabCount

                else:
                    defineTabCount = tabCount - 1
                    tabCount--




        tabCount -= defineTabCount


    if tabCount < 0:
        tabCount = 0

    # For multi-line string constants, indent of next line (bug #417767).
    if  isInQuote and line[ line.size() - 1 ] == '\\' :
        TRACE( INFO, "Line ends with continued quote - suppressing indent of next line." )
        suppressIndent = True

    else:
        suppressIndent = False


    # finally, indentations into begining of line
    prevFinalLineSpaceTabCount = spaceTabCount
    prevFinalLineTabCount = tabCount

    if forceTabIndent:
        tabCount += spaceTabCount / indentLength
        spaceTabCount = spaceTabCount % indentLength


    # attempted bugfix #417767
    if  not  suppressCurrentIndent :
        outBuffer = preLineWS(spaceTabCount,tabCount) + outBuffer


    if lastLineHeader != NULL:
        previousLastLineHeader = lastLineHeader


    return outBuffer



def preLineWS(self, spaceTabCount, tabCount):
    string ws

    for (int i=0; i<tabCount; i++)
        ws += indentString

    while ((spaceTabCount--) > 0)
        ws += string(" ")

    return ws


'''
 * register an in-statement indent.
 '''
void ASBeautifier.registerInStatementIndent( string &line, i, spaceTabCount,
        int minIndent, updateParenStack)
    int inStatementIndent
    remainingCharNum = line.size() - i
    nextNonWSChar = 1

    nextNonWSChar = getNextProgramCharDistance(line, i)

    # if indent is around the last char in the line, instead 2 spaces from the previous indent
    if nextNonWSChar == remainingCharNum:
        previousIndent = spaceTabCount
        if not inStatementIndentStack.empty():
            previousIndent = inStatementIndentStack.back()

        inStatementIndentStack.push_back('''2''' indentLength + previousIndent )
        if updateParenStack:
            parenIndentStack.push_back( previousIndent )
        return


    if updateParenStack:
        parenIndentStack.push_back(i+spaceTabCount)

    inStatementIndent = i + nextNonWSChar + spaceTabCount

    if i + nextNonWSChar < minIndent:
        inStatementIndent = minIndent + spaceTabCount

    if i + nextNonWSChar > maxInStatementIndent:
        inStatementIndent =  indentLength*2 + spaceTabCount



    if (not inStatementIndentStack.empty() and
            inStatementIndent < inStatementIndentStack.back())
        inStatementIndent = inStatementIndentStack.back()

    inStatementIndentStack.push_back(inStatementIndent)


'''*
 * get distance to the next non-white sspace, non-comment character in the line.
 * if no such character exists, the length remaining to the end of the line.
 '''
def getNextProgramCharDistance(self, &line, i):
    inComment = False
    remainingCharNum = line.size() - i
    charDistance = 1
    int ch

    for (charDistance = 1; charDistance < remainingCharNum; charDistance++)
        ch = line[i + charDistance]
        if inComment:
            if CONTAINS_AT(line, AS_CLOSE_COMMENT, 2, i + charDistance):
                charDistance++
                inComment = False

            continue

        elif isWhiteSpace(ch):
            continue
        elif ch == '/':
            if CONTAINS_AT(line, AS_OPEN_LINE_COMMENT, 2, i + charDistance):
                return remainingCharNum
            elif CONTAINS_AT(line, AS_OPEN_COMMENT, 2, i + charDistance):
                charDistance++
                inComment = True


        else:
            return charDistance


    return charDistance



'''*
 * check if a specific character can be used in a legal variable/method/class name
 *
 * @return          legality of the char.
 * @param ch        the character to be checked.
 '''
def isLegalNameChar(self, ch):
    return (isalnum(ch) #(ch>='a' and ch<='z') or (ch>='A' and ch<='Z') or (ch>='0' and ch<='9') or
            or ch=='.' or ch=='_' or (not ( sourceStyle != STYLE_JAVA ) and ch=='$') or (( sourceStyle != STYLE_JAVA ) and ch=='~'))


'''*
 * check if a specific line position contains a header, of several possible headers.
 *
 * @return    a pointer to the found header. if no header was found then return NULL.
 '''
 string *ASBeautifier.findHeader( string &line, i, string*> &possibleHeaders, checkBoundry)
    maxHeaders = possibleHeaders.size()
     string *header = NULL
    int p

    for (p=0; p < maxHeaders; p++)
        header = possibleHeaders[p]

        if CONTAINS_AT(line, *header, header.size(), i):
            # check that self is a header and not a part of a longer word
            # (e.g. not at its begining, at its middle...)

            lineLength = line.size()
            headerEnd = i + header.length()
            startCh = (*header)[0];   # first char of header
            endCh = 0;                # char just after header
            prevCh = 0;               # char just before header

            if headerEnd < lineLength:
                endCh = line[headerEnd]

            if i > 0:
                prevCh = line[i-1]


            if not checkBoundry:
                return header

            elif (prevCh != 0
                     and isLegalNameChar(startCh)
                     and isLegalNameChar(prevCh))
                return NULL

            elif (headerEnd >= lineLength
                     or not isLegalNameChar(startCh)
                     or not isLegalNameChar(endCh))
                return header

            else:
                return NULL




    return NULL



'''*
 * check if a specific character can be used in a legal variable/method/class name
 *
 * @return          legality of the char.
 * @param ch        the character to be checked.
 '''
def isWhiteSpace(self, ch):
    return (ch == ' ' or ch == '\t')


'''*
 * find the index number of a string element in a container of strings
 *
 * @return              the index number of element in the ocntainer. -1 if element not found.
 * @param container     a vector of strings.
 * @param element       the element to find .
 '''
def indexOf(self, string*> &container, *element):
    vector< string*>.const_iterator where

    where= find(container.begin(), container.end(), element)
    if where == container.end():
        return -1
    else:
        return where - container.begin()


'''*
 * trim removes the white space surrounding a line.
 *
 * @return          the trimmed line.
 * @param str       the line to trim.
 '''
def trim(self, &str):
    start = 0
    end = str.size() - 1

    while (start < end and isWhiteSpace(str[start]))
        start++

    while (start <= end and isWhiteSpace(str[end]))
        end--

    string returnStr(str, start, end+1-start)
    return returnStr


} # namespace astyle
