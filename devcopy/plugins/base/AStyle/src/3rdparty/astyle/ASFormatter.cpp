# $Id: ASFormatter.cpp, 1.4 2005/07/01 18:58:17 mandrav Exp $
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
# Patches:
# 26 November 1998 - Richard Bullington -
#        A correction of line-breaking in headers following '}',
#        was created using a variation of a  patch by Richard Bullington.

#include "astyle.h"

#include <string>
#include <cctype>
#include <vector>
#include <algorithm>
#include <iostream>

using namespace std

namespace astyle

int Tracer.mIndent = 0

AS_IF = "if"
AS_ELSE = "else"
AS_FOR = "for"
AS_DO = "do"
AS_WHILE = "while"
AS_SWITCH = "switch"
AS_CASE = "case"
AS_DEFAULT = "default"
AS_CLASS = "class"
AS_STRUCT = "struct"
AS_UNION = "union"
AS_INTERFACE = "interface"
AS_NAMESPACE = "namespace"
AS_EXTERN = "extern"
AS_PUBLIC = "public"
AS_PROTECTED = "protected"
AS_PRIVATE = "private"
AS_STATIC = "static"
AS_SYNCHRONIZED = "synchronized"
AS_OPERATOR = "operator"
AS_TEMPLATE = "template"
AS_TRY = "try"
AS_CATCH = "catch"
AS_FINALLY = "finally"
AS_THROWS = "throws"
AS_CONST = "const"

AS_ASM = "asm"

AS_BAR_DEFINE = "#define"
AS_BAR_INCLUDE = "#include"
AS_BAR_IF = "#if"
AS_BAR_EL = "#el"
AS_BAR_ENDIF = "#endif"

AS_OPEN_BRACKET = "{"
AS_CLOSE_BRACKET = "}"
AS_OPEN_LINE_COMMENT = "#"
AS_OPEN_COMMENT = "'''"
AS_CLOSE_COMMENT = "'''"

AS_ASSIGN = "="
AS_PLUS_ASSIGN = "+="
AS_MINUS_ASSIGN = "-="
AS_MULT_ASSIGN = "*="
AS_DIV_ASSIGN = "/="
AS_MOD_ASSIGN = "%="
AS_OR_ASSIGN = "|="
AS_AND_ASSIGN = "&="
AS_XOR_ASSIGN = "^="
AS_GR_GR_ASSIGN = ">>="
AS_LS_LS_ASSIGN = "<<="
AS_GR_GR_GR_ASSIGN = ">>>="
AS_LS_LS_LS_ASSIGN = "<<<="
AS_RETURN = "return"

AS_EQUAL = "=="
AS_PLUS_PLUS = "++"
AS_MINUS_MINUS = "--"
AS_NOT_EQUAL = "!="
AS_GR_EQUAL = ">="
AS_GR_GR = ">>"
AS_GR_GR_GR = ">>>"
AS_LS_EQUAL = "<="
AS_LS_LS = "<<"
AS_LS_LS_LS = "<<<"
AS_ARROW = "."
AS_AND = "and"
AS_OR = "or"
AS_COLON_COLON = "."
AS_PAREN_PAREN = "()"
AS_BLPAREN_BLPAREN = "[]"

AS_PLUS = "+"
AS_MINUS = "-"
AS_MULT = "*"
AS_DIV = "/"
AS_MOD = "%"
AS_GR = ">"
AS_LS = "<"
AS_NOT = "not "
AS_BIT_OR = "|"
AS_BIT_AND = "&"
AS_BIT_NOT = "~"
AS_BIT_XOR = "^"
AS_QUESTION = "?"
AS_COLON = ":"
AS_COMMA = ","
AS_SEMICOLON = ";"

AS_FOREACH = "foreach"
AS_LOCK = "lock"
AS_UNSAFE = "unsafe"
AS_FIXED = "fixed"
AS_GET = "get"
AS_SET = "set"
AS_ADD = "add"
AS_REMOVE = "remove"

static  string * headers_[] = { &AS_IF, &AS_ELSE, &AS_DO, &AS_WHILE, &AS_FOR,
    &AS_SYNCHRONIZED, &AS_TRY, &AS_CATCH, &AS_FINALLY, &AS_SWITCH, &AS_TEMPLATE,
    &AS_FOREACH, &AS_LOCK, &AS_UNSAFE, &AS_FIXED, &AS_GET, &AS_SET, &AS_ADD,
    &AS_REMOVE

static vector<  string * > headers( headers_, headers_ + ( sizeof(headers_) / sizeof(headers_[0] ) ) )

static  string * nonParenHeaders_[] = { &AS_ELSE, &AS_DO, &AS_TRY, &AS_FINALLY,
    &AS_UNSAFE, &AS_GET, &AS_SET, &AS_ADD, &AS_REMOVE
    #, &AS_TEMPLATE

static vector<  string * > nonParenHeaders( nonParenHeaders_, nonParenHeaders_ + ( sizeof(nonParenHeaders_) / sizeof(nonParenHeaders_[0] ) ) )

static  string * preDefinitionHeaders_[] = { &AS_CLASS, &AS_INTERFACE,
    &AS_NAMESPACE, &AS_STRUCT

static vector<  string * > preDefinitionHeaders( preDefinitionHeaders_, preDefinitionHeaders_ + ( sizeof(preDefinitionHeaders_) / sizeof(preDefinitionHeaders_[0] ) ) )

static  string * preCommandHeaders_[] = { &AS_EXTERN, &AS_THROWS, &AS_CONST

static vector<  string * > preCommandHeaders( preCommandHeaders_, preCommandHeaders_ + ( sizeof(preCommandHeaders_) / sizeof(preCommandHeaders_[0] ) ) )

static  string * preprocessorHeaders_[] = { &AS_BAR_DEFINE
    #, &AS_BAR_INCLUDE, &AS_BAR_IF, &AS_BAR_EL, &AS_BAR_ENDIF

static vector<  string * > preprocessorHeaders( preprocessorHeaders_, preprocessorHeaders_+ ( sizeof(preprocessorHeaders_) / sizeof(preprocessorHeaders_[0] ) ) )

static  string * operators_[] = { &AS_PLUS_ASSIGN, &AS_MINUS_ASSIGN,
    &AS_MULT_ASSIGN, &AS_DIV_ASSIGN, &AS_MOD_ASSIGN, &AS_OR_ASSIGN,
    &AS_AND_ASSIGN, &AS_XOR_ASSIGN, &AS_EQUAL, &AS_PLUS_PLUS,
    &AS_MINUS_MINUS, &AS_NOT_EQUAL, &AS_GR_EQUAL, &AS_GR_GR_GR_ASSIGN,
    &AS_GR_GR_ASSIGN, &AS_GR_GR_GR, &AS_GR_GR, &AS_LS_EQUAL,
    &AS_LS_LS_LS_ASSIGN, &AS_LS_LS_ASSIGN, &AS_LS_LS_LS, &AS_LS_LS,
    &AS_ARROW, &AS_AND, &AS_OR, &AS_COLON_COLON, &AS_PLUS, &AS_MINUS,
    &AS_MULT, &AS_DIV, &AS_MOD, &AS_QUESTION, &AS_COLON, &AS_ASSIGN,
    &AS_LS, &AS_GR, &AS_NOT, &AS_BIT_OR, &AS_BIT_AND, &AS_BIT_NOT,
    &AS_BIT_XOR, &AS_OPERATOR, &AS_COMMA, &AS_RETURN
    #, &AS_PAREN_PAREN, &AS_BLPAREN_BLPAREN, &AS_SEMICOLON

static vector<  string * > operators( operators_, operators_ + ( sizeof(operators_) / sizeof(operators_[0]) ) )

static  string * assignmentOperators_[] = { &AS_PLUS_ASSIGN, &AS_MINUS_ASSIGN,
    &AS_MULT_ASSIGN, &AS_DIV_ASSIGN, &AS_MOD_ASSIGN, &AS_XOR_ASSIGN,
    &AS_OR_ASSIGN, &AS_AND_ASSIGN, &AS_GR_GR_GR_ASSIGN, &AS_LS_LS_LS_ASSIGN,
    &AS_ASSIGN

static vector<  string * > assignmentOperators( assignmentOperators_, assignmentOperators_ + ( sizeof(assignmentOperators_) / sizeof(assignmentOperators_[0]) ) )

'''*
 * initialize the ASFormatter.
 *
 * init() should be called every time a ASFormatter object is to start
 * formatting a NEW source file.
 * init() recieves an istream reference
 * that will be used to iterate through the source code.
 '''
def init(self, & si):
    ASBeautifier.init(si)
    sourceIterator = &si

    delete( preBracketHeaderStack )
    preBracketHeaderStack = vector< string*>

    delete( bracketTypeStack )
    bracketTypeStack = vector<BracketType>
    bracketTypeStack.push_back(DEFINITION_TYPE)

    delete( parenStack )
    parenStack = vector<int>
    parenStack.push_back(0)

    currentHeader = NULL
    currentLine = string("")
    formattedLine = ""
    currentChar = ' '
    previousCommandChar = ' '
    previousNonWSChar = ' '
    quoteChar = '"'
    charNum = 0
    previousOperator = NULL

    isVirgin = True
    isInLineComment = False
    isInComment = False
    isInPreprocessor = False
    doesLineStartComment = False
    isInQuote = False
    isSpecialChar = False
    isNonParenHeader = True
    foundPreDefinitionHeader = False
    foundPreCommandHeader = False
    foundQuestionMark = False
    isInLineBreak = False
    endOfCodeReached = False
    isLineReady = False
    isPreviousBracketBlockRelated = True
    isInPotentialCalculation = False
    #foundOneLineBlock = False
    shouldReparseCurrentChar = False
    passedSemicolon = False
    passedColon = False
    isInTemplate = False
    shouldBreakLineAfterComments = False
    isImmediatelyPostComment = False
    isImmediatelyPostLineComment = False
    isImmediatelyPostEmptyBlock = False

    isPrependPostBlockEmptyLineRequested = False
    isAppendPostBlockEmptyLineRequested = False
    prependEmptyLine = False

    foundClosingHeader = False
    previousReadyFormattedLineLength = 0

    isImmediatelyPostHeader = False
    isInHeader = False


'''*
 * get the next formatted line.
 *
 * @return    formatted line.
 '''
def nextLine(self):
    TRACE_LIFE( FUNCTION, "formatting line." )
     string *newHeader
    isCharImmediatelyPostComment = False
    isPreviousCharPostComment = False
    isCharImmediatelyPostLineComment = False
    isInVirginLine = isVirgin
    isCharImmediatelyPostOpenBlock = False
    isCharImmediatelyPostCloseBlock = False
    isCharImmediatelyPostTemplate = False
    isCharImmediatelyPostHeader = False

    if  not  isFormattingEnabled() :
        TRACE( INFO, "formatting not enabled - delegating to ASBeautifier." )
        return ASBeautifier.nextLine()


    while ( not  isLineReady )
        if  shouldReparseCurrentChar :
            TRACE( INFO, "reparsing character..." )
            shouldReparseCurrentChar = False

        elif  not  getNextChar() :
            TRACE( INFO, "no more characters - breaking line and delegating to ASBeautifier." )
            breakLine()
            return beautify(readyFormattedLine)

        else # stuff to do when reading a character...
            # make sure that a virgin '{' at the begining of the file will be treated as a block...
            if  isInVirginLine and currentChar == '{' :
                TRACE( INFO, "virgin '{'" )
                previousCommandChar = '{'

            isPreviousCharPostComment = isCharImmediatelyPostComment
            isCharImmediatelyPostComment = False
            isCharImmediatelyPostTemplate = False
            isCharImmediatelyPostHeader = False


        # handle comments
        if  isInLineComment :
            appendCurrentChar()

            # explicitely break a line when a line comment's end is found.
            if  ''' bracketFormatMode == ATTACH_MODE and ''' charNum + 1 == currentLine.size():
                isInLineBreak = True
                isInLineComment = False
                isImmediatelyPostLineComment = True
                currentChar = 0;  #make sure it is a neutral char.

            continue

        elif  isInComment :
            if  isSequenceReached( AS_CLOSE_COMMENT ) :
                isInComment = False
                isImmediatelyPostComment = True
                appendSequence( AS_CLOSE_COMMENT )
                goForward( 1 )

            else:
                appendCurrentChar()

            continue


        # handle quotes
        if  isInQuote :
            if  isSpecialChar :
                isSpecialChar = False
                appendCurrentChar()

            elif  currentChar == '\\' :
                TRACE( INFO, "special (escaped) char entcountered" )
                isSpecialChar = True
                appendCurrentChar()

            elif  quoteChar == currentChar :
                TRACE( INFO, "end of quote encountered" )
                isInQuote = False
                appendCurrentChar()

            else:
                appendCurrentChar()

            continue



        # handle white space or preprocessor statements (simplifies the rest)
        if  isWhiteSpace( currentChar ) or isInPreprocessor :
            # TODO: stale comment: if  isLegalNameChar( previousChar ) and isLegalNameChar( peekNextChar() ) :
            appendCurrentChar()
            continue


        # detect BEGIN of comments or quotes
        if  isSequenceReached( AS_OPEN_LINE_COMMENT ) :
            TRACE( INFO, "beginning of line comment encountered" )
            isInLineComment = True
            if  padOperators :
                appendSpacePad()

            appendSequence( AS_OPEN_LINE_COMMENT )
            goForward( 1 )
            continue

        elif  isSequenceReached( AS_OPEN_COMMENT ) :
            TRACE( INFO, "beginning of multi-line comment encountered" )
            isInComment = True
            if  padOperators :
                appendSpacePad()

            appendSequence( AS_OPEN_COMMENT )
            goForward( 1 )
            continue

        elif  currentChar == '"' or currentChar == '\'' :
            TRACE( INFO, "beginning of quote encountered" )
            isInQuote = True
            quoteChar = currentChar
            # if (padOperators)     # BUGFIX: these two lines removed. seem to be unneeded, interfere with L"
            #     appendSpacePad(); # BUGFIX: TODO: make sure the removal of these lines doesn't reopen old bugs...
            appendCurrentChar()
            continue


        # not in quote or comment or white-space of any type ...

        # check if in preprocessor
        # ** isInPreprocessor will be automatically reset at the begining of a line in getNextChar()
        if  currentChar == '#' :
            TRACE( INFO, "beginning of preprocessor statement encountered" )
            isInPreprocessor = True

        # TODO: Should not be reached; candidate for removal
        if  isInPreprocessor :
            TRACE( INFO, "being inside preprocessor. IS THIS EVER ACTUALLY REACHED?" )
            appendCurrentChar()
            continue


        # not in preprocessor ...
        if  isImmediatelyPostComment :
            TRACE( INFO, "isImmediatelyPostComment" )
            isImmediatelyPostComment = False
            isCharImmediatelyPostComment = True


        if  isImmediatelyPostLineComment :
            TRACE( INFO, "isImmediatelyPostLineComment" )
            isImmediatelyPostLineComment = False
            isCharImmediatelyPostLineComment = True


        if  shouldBreakLineAfterComments :
            TRACE( INFO, "breaking line after comments" )
            shouldBreakLineAfterComments = False
            shouldReparseCurrentChar = True
            breakLine()
            continue


        if  isImmediatelyPostHeader :
            TRACE( INFO, "isImmediatelyPostHeader" )

            # reset post-header information
            isImmediatelyPostHeader = False
            isCharImmediatelyPostHeader = True

            # If configured, headers from their succeeding blocks.
            # Make sure that elif()'s are excepted unless configured
            # to be broken too.
            if ( breakOneLineStatements and 
                 ( breakElseIfs or 
                 ( currentHeader != &AS_ELSE or findHeader( headers ) != &AS_IF ) ) )
                TRACE( INFO, "breaking line after header" )
                isInLineBreak = True



        if  passedSemicolon :
            TRACE( INFO, "passedSemicolon" )
            passedSemicolon = False
            if  parenStack.back() == 0 :
                TRACE( INFO, "parenStack.back() == 0" )
                shouldReparseCurrentChar = True
                isInLineBreak = True
                continue



        if  passedColon :
            TRACE( INFO, "passedColon" )
            passedColon = False
            if  parenStack.back() == 0 :
                TRACE( INFO, "parenStack.back() == 0" )
                shouldReparseCurrentChar = True
                isInLineBreak = True
                continue



        # Check if in template declaration, e.g. foo<bar> or foo<bar,fig>
        if  not  isInTemplate and currentChar == '<' :
            TRACE( ENTRY, "checking for template..." )
            templateDepth = 0; # TODO: hides astyle.ASBeautifier.templateDepth
             string *oper
            for ( i = charNum; i < currentLine.size(); i += ( oper ? oper.length() : 1 ) )
                oper = ASBeautifier.findHeader( currentLine, i, operators )

                if  oper == &AS_LS :
                    templateDepth++

                elif  oper == &AS_GR :
                    templateDepth--
                    if  templateDepth == 0 :
                        TRACE( EXIT, "template encounterednot " )
                        isInTemplate = True
                        break


                elif ( oper == &AS_COMMA            # comma,     e.g. A<int, char>
                       or oper == &AS_BIT_AND          # reference, e.g. A<int&>
                       or oper == &AS_MULT             # pointer,   e.g. A<int*>
                       or oper == &AS_COLON_COLON)     # .,        e.g. std.string
                    continue

                elif  not  isLegalNameChar( currentLine[i] ) and not  isWhiteSpace( currentLine[i] ) :
                    TRACE( EXIT, "False alarm - not a template" )
                    isInTemplate = False
                    break




        # handle parenthesies
        if  currentChar == '(' or currentChar == '[' or ( isInTemplate and currentChar == '<' ) :
            TRACE( ENTRY, "opening paren '" << currentChar << "' encountered." )
            parenStack.back()++

        elif  currentChar == ')' or currentChar == ']' or ( isInTemplate and currentChar == '>' ) :
            TRACE( EXIT, "closing paren '" << currentChar << "' encountered." )
            parenStack.back()--

            if  isInTemplate and parenStack.back() == 0 :
                TRACE( INFO, "(also marks end of template)" )
                isInTemplate = False
                isCharImmediatelyPostTemplate = True


            # check if self parenthesis closes a header, e.g. if ...), while (...:
            if  isInHeader and parenStack.back() == 0 :
                TRACE( INFO, "(also marks end of header)" )
                isInHeader = False
                isImmediatelyPostHeader = True




        # handle brackets
        bracketType = NULL_TYPE

        if  currentChar == '{' :
            TRACE( ENTRY, "opening bracket encountered" )
            bracketType = getBracketType()
            foundPreDefinitionHeader = False
            foundPreCommandHeader = False

            bracketTypeStack.push_back(bracketType)
            preBracketHeaderStack.push_back(currentHeader)
            currentHeader = NULL

            isPreviousBracketBlockRelated = (bracketType != ARRAY_TYPE)

        elif  currentChar == '}' :
            TRACE( EXIT, "closing bracket encountered" )

            # if a request has been made to append a post block empty line,
            # but the block exists immediately before a closing bracket,
            # then there is no need for the empty line.
            isAppendPostBlockEmptyLineRequested = False

            if  not  bracketTypeStack.empty() :
                TRACE( INFO, "popping from bracketTypeStack..." )
                bracketType = bracketTypeStack.back()
                bracketTypeStack.pop_back()

                isPreviousBracketBlockRelated = ( bracketType != ARRAY_TYPE )


            if  not  preBracketHeaderStack.empty() :
                TRACE( INFO, "popping from preBracketHeaderStack..." )
                currentHeader = preBracketHeaderStack.back()
                preBracketHeaderStack.pop_back()

            else:
                TRACE( INFO, "currentHeader = NULL" )
                currentHeader = NULL



        if  bracketType != ARRAY_TYPE :
            TRACE( INFO, "bracket is not of ARRAY_TYPE" )

            if  currentChar == '{' :
                TRACE( INFO, "pushing zero to parenStack" )
                parenStack.push_back(0)

            elif  currentChar == '}' and not  parenStack.empty() :
                TRACE( INFO, "popping from parenStack" )
                parenStack.pop_back()


            if  bracketFormatMode != NONE_MODE :
                TRACE( INFO, "bracketFormatMode != NONE_MODE" )
                
                # TODO: Haven't looked at self yet.
                if  currentChar == '{' :
                    if ( ( bracketFormatMode == ATTACH_MODE
                            or bracketFormatMode == BDAC_MODE and bracketTypeStack.size() >= 2
                            and ( (*bracketTypeStack)[ bracketTypeStack.size() - 2 ] == COMMAND_TYPE ) '''and isInLineBreak''')
                            and not  isCharImmediatelyPostLineComment )
                        appendSpacePad()
                        if ( not  isCharImmediatelyPostComment   # do not attach '{' to lines that end with '''''' comments.
                               and previousCommandChar != '{'
                               and previousCommandChar != '}'
                               and previousCommandChar != ';') # '}' , ';' chars added for proper handling of '{' immediately after a '}' or ';'
                            appendCurrentChar(False)

                        else:
                            appendCurrentChar(True)

                        continue

                    elif ( bracketFormatMode == BREAK_MODE
                               or bracketFormatMode == BDAC_MODE and bracketTypeStack.size() >= 2
                               and ( (*bracketTypeStack)[ bracketTypeStack.size() - 2 ] == DEFINITION_TYPE))
                        if  breakOneLineBlocks or (bracketType != SINGLE_LINE_TYPE) :
                            breakLine()

                        appendCurrentChar()
                        continue


                elif  currentChar == '}' :
                    # origLineBreak = isInLineBreak

                    # mark state of immediately after empty block
                    # self state will be used for locating brackets that appear immedately AFTER an empty block (e.g. '{} \n}').
                    if  previousCommandChar == '{' :
                        isImmediatelyPostEmptyBlock = True


                    if ( ( not  ( previousCommandChar == '{' and isPreviousBracketBlockRelated ) ) # self '{' does not close an empty block
                          and ( breakOneLineBlocks or ( bracketType != SINGLE_LINE_TYPE ) )     # astyle is allowed to break on line blocks
                          and not  isImmediatelyPostEmptyBlock)                                    # self '}' does not immediately follow an empty block
                        breakLine()
                        appendCurrentChar()

                    else:
                        if  not  isCharImmediatelyPostComment :
                            isInLineBreak = False

                        appendCurrentChar()
                        if  breakOneLineBlocks or ( bracketType != SINGLE_LINE_TYPE ) :
                            shouldBreakLineAfterComments = True



                    if  breakBlocks :
                        isAppendPostBlockEmptyLineRequested =True


                    continue


        } # bracketType != ARRAY_TYPE

        # TODO: What's self? An attempt at the longest conditional in the world?
        if  ( ( previousCommandChar == '{' and isPreviousBracketBlockRelated:
            or ( previousCommandChar == '}' and not  isImmediatelyPostEmptyBlock   # <--
                                            and isPreviousBracketBlockRelated
                                            and not  isPreviousCharPostComment    # <-- Fixes wrongly appended newlines after '}' immediately after comments... 10/9/1999
                                            and peekNextChar() != ' ' ) )
            and ( breakOneLineBlocks or ( bracketTypeStack.back() != SINGLE_LINE_TYPE ) ) )
            isCharImmediatelyPostOpenBlock = (previousCommandChar == '{')
            isCharImmediatelyPostCloseBlock = (previousCommandChar == '}')

            previousCommandChar = ' '
            isInLineBreak = True;  # <----


        # reset block handling flag
        isImmediatelyPostEmptyBlock = False

        # look for headers
        if  not  isInTemplate :
            if  (newHeader = findHeader(headers)) != NULL:
                foundClosingHeader = False
                 string *previousHeader

                # recognize closing headers of do..while, if..else, try..catch..finally
                if  (newHeader == &AS_ELSE and currentHeader == &AS_IF:
                        or (newHeader == &AS_WHILE and currentHeader == &AS_DO)
                        or (newHeader == &AS_CATCH and currentHeader == &AS_TRY)
                        or (newHeader == &AS_CATCH and currentHeader == &AS_CATCH)
                        or (newHeader == &AS_FINALLY and currentHeader == &AS_TRY)
                        or (newHeader == &AS_FINALLY and currentHeader == &AS_CATCH) )
                    foundClosingHeader = True

                previousHeader = currentHeader
                currentHeader = newHeader

                # If in ATTACH or LINUX bracket modes, closing headers (e.g. 'else', 'catch')
                # to their preceding bracket,
                # But do not perform the attachment if the breakClosingHeaderBrackets is set!
                if not breakClosingHeaderBrackets and foundClosingHeader and (bracketFormatMode == ATTACH_MODE or bracketFormatMode == BDAC_MODE) and previousNonWSChar == '}':
                    isInLineBreak = False
                    appendSpacePad()

                    if breakBlocks:
                        isAppendPostBlockEmptyLineRequested = False


                #Check if a template definition as been reached, e.g. template<class A>
                if newHeader == &AS_TEMPLATE:
                    isInTemplate = True


                # check if the found header is non-paren header
                isNonParenHeader = ( find(nonParenHeaders.begin(), nonParenHeaders.end(),
                                          newHeader) != nonParenHeaders.end() )
                # added C# support
                if ( ( sourceStyle != STYLE_CSHARP ) and ( newHeader == &AS_UNSAFE
                    or newHeader == &AS_GET or newHeader == &AS_SET
                    or newHeader == &AS_ADD or newHeader == &AS_REMOVE ) )
                    isNonParenHeader = False
                appendSequence(*currentHeader)
                goForward(currentHeader.length() - 1)
                # if padding is on, a paren-header is found
                # then add a space pad after it.
                if padOperators and not isNonParenHeader:
                    appendSpacePad()


                # Signal that a header has been reached
                # *** But treat a closing while() (as in do...while)
                #     as if it where NOT a header since a closing while()
                #     should never have a block after it!
                if not (foundClosingHeader and currentHeader == &AS_WHILE):
                    isInHeader = True
                    if isNonParenHeader:
                        isImmediatelyPostHeader = True
                        isInHeader = False



                if currentHeader == &AS_IF and previousHeader == &AS_ELSE:
                    isInLineBreak = False

                if breakBlocks:
                    if (previousHeader == NULL
                            and not foundClosingHeader
                            and not isCharImmediatelyPostOpenBlock)
                        isPrependPostBlockEmptyLineRequested = True


                    if (currentHeader == &AS_ELSE
                            or currentHeader == &AS_CATCH
                            or currentHeader == &AS_FINALLY
                            or foundClosingHeader)
                        isPrependPostBlockEmptyLineRequested = False


                    if (breakClosingHeaderBlocks
                            and  isCharImmediatelyPostCloseBlock)
                        isPrependPostBlockEmptyLineRequested = True




                continue

            elif  (newHeader = findHeader(preDefinitionHeaders)) != NULL:
                foundPreDefinitionHeader = True
                appendSequence(*newHeader)
                goForward(newHeader.length() - 1)

                if breakBlocks:
                    isPrependPostBlockEmptyLineRequested = True

                continue

            elif  (newHeader = findHeader(preCommandHeaders)) != NULL:
                foundPreCommandHeader = True
                appendSequence(*newHeader)
                goForward(newHeader.length() - 1)

                continue



        if previousNonWSChar == '}' or currentChar == ';':
            if (breakOneLineStatements and currentChar == ';'
                    and (breakOneLineBlocks or (bracketTypeStack.back() != SINGLE_LINE_TYPE)))
                passedSemicolon = True


            if breakBlocks and currentHeader != NULL and parenStack.back() == 0:
                isAppendPostBlockEmptyLineRequested = True


            if currentChar != ';':
                currentHeader = NULL; #DEVEL: is self ok?

            foundQuestionMark = False
            foundPreDefinitionHeader = False
            foundPreCommandHeader = False
            isInPotentialCalculation = False



        if (currentChar == ':'
                and breakOneLineStatements
                and not foundQuestionMark # not in a ... ? ... : ... sequence
                and not foundPreDefinitionHeader # not in a definition block (e.g. class foo : public bar
                and previousCommandChar != ')' # not immediately after closing paren of a method header, e.g. ASFormatter.ASFormatter(...) : ASBeautifier(...)
                and previousChar != ':' # not part of '.'
                and peekNextChar() != ':') # not part of '.'
            passedColon = True
            if breakBlocks:
                isPrependPostBlockEmptyLineRequested = True


        if currentChar == '?':
            foundQuestionMark = True

        if padOperators:
            if (newHeader = findHeader(operators)) != NULL:
                shouldPad = (newHeader != &AS_COLON_COLON
                                  and newHeader != &AS_PAREN_PAREN
                                  and newHeader != &AS_BLPAREN_BLPAREN
                                  and newHeader != &AS_PLUS_PLUS
                                  and newHeader != &AS_MINUS_MINUS
                                  and newHeader != &AS_NOT
                                  and newHeader != &AS_BIT_NOT
                                  and newHeader != &AS_ARROW
                                  and newHeader != &AS_OPERATOR
                                  and not (newHeader == &AS_MINUS and isInExponent())
                                  and not (newHeader == &AS_PLUS and isInExponent())
                                  and previousOperator != &AS_OPERATOR
                                  and not ((newHeader == &AS_MULT or newHeader == &AS_BIT_AND)
                                       and isPointerOrReference())
                                  and not ( (isInTemplate or isCharImmediatelyPostTemplate)
                                        and (newHeader == &AS_LS or newHeader == &AS_GR))
                                 )

                if not isInPotentialCalculation:
                    if find(assignmentOperators.begin(), assignmentOperators.end(), newHeader:
                            != assignmentOperators.end())
                        isInPotentialCalculation = True

                # pad before operator
                if (shouldPad
                        and not (newHeader == &AS_COLON and not foundQuestionMark)
                        and newHeader != &AS_SEMICOLON
                        and newHeader != &AS_COMMA)
                    appendSpacePad()
                appendSequence(*newHeader)
                goForward(newHeader.length() - 1)

                # since self block handles '()' and '[]',
                # the parenStack must be updated here accordingly!
                if (newHeader == &AS_PAREN_PAREN
                        or newHeader == &AS_BLPAREN_BLPAREN)
                    parenStack.back()--

                currentChar = (*newHeader)[newHeader.length() - 1]
                # pad after operator
                # but do not pad after a '-' that is a unary-minus.
                if  shouldPad and not (newHeader == &AS_MINUS and isUnaryMinus()) :
                    appendSpacePad()

                previousOperator = newHeader
                continue


        if padParen:
            if currentChar == '(' or currentChar == '[' :
                peekedChar = peekNextChar()

                isInPotentialCalculation = True
                appendCurrentChar()
                if not (currentChar == '(' and peekedChar == ')':
                        and not (currentChar == '[' and peekedChar == ']'))
                    appendSpacePad()
                continue

            elif currentChar == ')' or currentChar == ']':
                peekedChar = peekNextChar()

                if not (previousChar == '(' and currentChar == ')':
                        and not (previousChar == '[' and currentChar == ']'))
                    appendSpacePad()

                appendCurrentChar()

                if (peekedChar != ';' and peekedChar != ',' and peekedChar != '.'
                        and not (currentChar == ']' and peekedChar == '['))
                    appendSpacePad()
                continue



        appendCurrentChar()


    # return a beautified (i.e. correctly indented) line.

    string beautifiedLine
    readyFormattedLineLength = trim(readyFormattedLine).size()

    if (prependEmptyLine
            and readyFormattedLineLength > 0
            and previousReadyFormattedLineLength > 0)
        TRACE( INFO, "delegation point 2" )
        isLineReady = True; # signal that a readyFormattedLine is still waiting
        beautifiedLine = beautify("")

    else:
        TRACE( INFO, "delegation point 3" )
        isLineReady = False
        beautifiedLine = beautify(readyFormattedLine)


    prependEmptyLine = False
    previousReadyFormattedLineLength = readyFormattedLineLength

    return beautifiedLine



'''*
* check if there are any indented lines ready to be read by nextLine()
*
* @return    are there any indented lines ready?
'''
def hasMoreLines(self):
    if not isFormattingEnabled():
        return ASBeautifier.hasMoreLines()
    else:
        return not endOfCodeReached


'''*
 * check if formatting options are enabled, addition to indentation.
 *
 * @return     are formatting options enabled?
 '''
def isFormattingEnabled(self):
    return (bracketFormatMode != NONE_MODE
            or padOperators
            or convertTabs2Space)


'''*
 * check if a specific sequence exists in the current placement of the current line
 *
 * @return             whether sequence has been reached.
 * @param sequence     the sequence to be checked
 '''
def isSequenceReached(self, &sequence):
    return CONTAINS_AT(currentLine, sequence, sequence.size(), charNum)


'''*
 * jump over several characters.
 *
 * @param i       the number of characters to jump over.
 '''
def goForward(self, i):
    while (--i >= 0)
        getNextChar()


'''*
* peek at the next unread character.
*
* @return     the next unread character.
'''
def peekNextChar(self):
    peekNum = charNum + 1
    len = currentLine.size()
    ch = ' '

    while (peekNum < len)
        ch = currentLine[peekNum++]
        if not isWhiteSpace(ch):
            return ch


    if convertTabs2Space and ch == '\t':
        ch = ' '

    return ch


'''*
* check if current placement is before a comment or line-comment
*
* @return     is before a comment or line-comment.
'''
def isBeforeComment(self):
    peekNum = charNum + 1
    len = currentLine.size()
    # ch = ' '
    foundComment = False

    for (peekNum = charNum + 1
            peekNum < len and isWhiteSpace(currentLine[peekNum])
            ++peekNum)
        

    if peekNum < len:
        foundComment = ( CONTAINS_AT(currentLine, AS_OPEN_COMMENT, 2, peekNum)
                         or CONTAINS_AT(currentLine, AS_OPEN_LINE_COMMENT, 2, peekNum) )

    return foundComment


'''*
* get the next character, the current placement in the process.
* the character is inserted into the variable currentChar.
*
* @return   whether succeded to recieve the character.
'''
def getNextChar(self):
    isInLineBreak = False
    isAfterFormattedWhiteSpace = False

    if (padOperators and not isInComment and not isInLineComment
            and not isInQuote and not doesLineStartComment and not isInPreprocessor
            and not isBeforeComment())
        len = formattedLine.size()
        if len > 0 and isWhiteSpace(formattedLine[len-1]):
            isAfterFormattedWhiteSpace = True


    previousChar = currentChar
    if not isWhiteSpace(currentChar):
        previousNonWSChar = currentChar
        if (not isInComment and not isInLineComment and not isInQuote
                and not isSequenceReached(AS_OPEN_COMMENT)
                and not isSequenceReached(AS_OPEN_LINE_COMMENT) )
            previousCommandChar = previousNonWSChar


    currentLineLength = currentLine.size()

    if (charNum+1 < currentLineLength
            and (not isWhiteSpace(peekNextChar()) or isInComment or isInLineComment))
        currentChar = currentLine[++charNum]
        if isAfterFormattedWhiteSpace:
            while (isWhiteSpace(currentChar) and charNum+1 < currentLineLength)
                currentChar = currentLine[++charNum]

        if convertTabs2Space and currentChar == '\t':
            currentChar = ' '

        return True

    else:
        if *sourceIterator:
            getline(*sourceIterator, currentLine)
            if  not currentLine.empty() and currentLine[currentLine.size() - 1] == '\r' :
                currentLine = currentLine.substr(0, currentLine.size() - 1)

            if currentLine.empty():
                currentLine = string(" "); # think

            # unless reading in the first line of the file,
            # break a line.
            if not isVirgin:
                isInLineBreak = True
            else:
                isVirgin = False

            if isInLineComment:
                isImmediatelyPostLineComment = True
            isInLineComment = False

            trimNewLine()
            currentChar = currentLine[charNum]

            # check if is in preprocessor right after the line break and line trimming
            if previousNonWSChar != '\\':
                isInPreprocessor = False
            else:
                TRACE( INFO, "previousNonWSChar == '\\'" )

            if convertTabs2Space and currentChar == '\t':
                currentChar = ' '

            return True

        else:
            endOfCodeReached = True
            return False




'''*
* jump over the leading white space in the current line,
* IF the line does not begin a comment or is in a preprocessor definition.
'''
def trimNewLine(self):
    len = currentLine.size()
    charNum = 0

    if isInComment or isInPreprocessor:
        return

    while (isWhiteSpace(currentLine[charNum]) and charNum+1 < len)
        ++charNum

    doesLineStartComment = False
    if isSequenceReached(string("'''")):
        charNum = 0
        doesLineStartComment = True



'''*
 * append the CURRENT character (curentChar)to the current
 * formatted line. Unless disabled (via canBreakLine == False),
 * first check if a line-break has been registered, if so
 * break the formatted line, only then append the character
 * into the next formatted line.
 *
 * @param canBreakLine     if True, registered line-break
 '''
def appendCurrentChar(self, canBreakLine):
    # TODO: This is probably where win / mac / linux line breaks can be enforced
    if canBreakLine and isInLineBreak:
        breakLine()
    formattedLine.append(1, currentChar)


'''*
 * append a string sequence to the current formatted line.
 * Unless disabled (via canBreakLine == False), check if a
 * line-break has been registered, if so break the
 * formatted line, only then append the sequence into
 * the next formatted line.
 *
 * @param sequence         the sequence to append.
 * @param canBreakLine     if True, registered line-break
 '''
def appendSequence(self, &sequence, canBreakLine):
    if canBreakLine and isInLineBreak:
        breakLine()
    formattedLine.append(sequence)


'''*
 * append a space to the current formattedline, the
 * last character is already a white-space character.
 '''
def appendSpacePad(self):
    len = formattedLine.size()
    if len == 0 or not isWhiteSpace(formattedLine[len-1]):
        formattedLine.append(1, ' ')


'''*
 * register a line break for the formatted line.
 '''
def breakLine(self):
    isLineReady = True
    isInLineBreak = False

    # queue an empty line prepend request if one exists
    prependEmptyLine = isPrependPostBlockEmptyLineRequested

    readyFormattedLine =  formattedLine
    if isAppendPostBlockEmptyLineRequested:
        isAppendPostBlockEmptyLineRequested = False
        isPrependPostBlockEmptyLineRequested = True

    else:
        isPrependPostBlockEmptyLineRequested = False


    formattedLine = ""


'''*
 * check if the currently reached open-bracket (i.e. '{')
 * opens a:
 * - a definition type block (such as a class or namespace),
 * - a command block (such as a method block)
 * - a static array
 * self method takes for granted that the current character
 * is an opening bracket.
 *
 * @return    the type of the opened block.
 '''
def getBracketType(self):
    BracketType returnVal

    if foundPreDefinitionHeader:
        returnVal = DEFINITION_TYPE
    else:
        bool isCommandType
        isCommandType = ( foundPreCommandHeader
                          or ( currentHeader != NULL and isNonParenHeader )
                          or ( previousCommandChar == ')' )
                          or ( previousCommandChar == ':' and not foundQuestionMark )
                          or ( previousCommandChar == ';' )
                          or ( ( previousCommandChar == '{' or  previousCommandChar == '}')
                               and isPreviousBracketBlockRelated ) )

        returnVal = (isCommandType ? COMMAND_TYPE : ARRAY_TYPE)


    if isOneLineBlockReached():
        returnVal = (BracketType) (returnVal | SINGLE_LINE_TYPE)

    return returnVal


'''*
 * check if the currently reached  '*' or '&' character is
 * a pointer-or-reference symbol, another operator.
 * self method takes for granted that the current character
 * is either a '*' or '&'.
 *
 * @return        whether current character is a reference-or-pointer
 '''
def isPointerOrReference(self):
    bool isPR
    isPR = ( not isInPotentialCalculation
             or (bracketTypeStack.back() == DEFINITION_TYPE)
             or (not isLegalNameChar(previousNonWSChar)
                 and previousNonWSChar != ')'
                 and previousNonWSChar != ']')
           )

    if not isPR:
        nextChar = peekNextChar()
        isPR |= (not isWhiteSpace(nextChar)
                 and nextChar != '-'
                 and nextChar != '('
                 and nextChar != '['
                 and not isLegalNameChar(nextChar))


    return isPR



'''*
 * check if the currently reached '-' character is
 * a unary minus
 * self method takes for granted that the current character
 * is a '-'.
 *
 * @return        whether the current '-' is a unary minus.
 '''
def isUnaryMinus(self):
    return ( (previousOperator == &AS_RETURN or not isalnum(previousCommandChar))
             and previousCommandChar != '.'
             and previousCommandChar != ')'
             and previousCommandChar != ']' )



'''*
 * check if the currently reached '-' or '+' character is
 * part of an exponent, i.e. 0.2E-5.
 * self method takes for granted that the current character
 * is a '-' or '+'.
 *
 * @return        whether the current '-' is in an exponent.
 '''
def isInExponent(self):
    formattedLineLength = formattedLine.size()
    if formattedLineLength >= 2:
        prevPrevFormattedChar = formattedLine[formattedLineLength - 2]
        prevFormattedChar = formattedLine[formattedLineLength - 1]

        return ( (prevFormattedChar == 'e' or prevFormattedChar == 'E')
                 and (prevPrevFormattedChar == '.' or isdigit(prevPrevFormattedChar)) )

    else:
        return False


'''*
 * check if a one-line bracket has been reached,
 * i.e. if the currently reached '{' character is closed
 * with a complimentry '}' elsewhere on the current line,
 *.
 * @return        has a one-line bracket been reached?
 '''
def isOneLineBlockReached(self):
    isInComment = False; # hides astyle.ASFormatter.isInComment
    isInQuote = False;   # hides astyle.ASFormatter.isInQuote
    bracketCount = 1
    currentLineLength = currentLine.size()
    i = 0
    ch = ' '
    quoteChar = ' ';     # hides astyle.ASFormatter.quoteChar

    for (i = charNum + 1; i < currentLineLength; ++i)
        ch = currentLine[i]

        if isInComment:
            if CONTAINS_AT(currentLine, AS_CLOSE_COMMENT, 2, i):
                isInComment = False
                ++i

            continue


        if ch == '\\':
            TRACE( INFO, "ch == '\\'" )
            ++i
            continue


        if isInQuote:
            if ch == quoteChar:
                isInQuote = False
            continue


        if ch == '"' or ch == '\'':
            isInQuote = True
            quoteChar = ch
            continue


        if CONTAINS_AT(currentLine, AS_OPEN_LINE_COMMENT, 2, i):
            break

        if CONTAINS_AT(currentLine, AS_OPEN_LINE_COMMENT, 2, i):
            isInComment = True
            ++i
            continue


        if ch == '{':
            ++bracketCount
        elif ch == '}':
            --bracketCount

        if bracketCount == 0:
            return True


    return False



'''*
 * check if one of a set of headers has been reached in the
 * current position of the current line.
 *
 * @return             a pointer to the found header. Or a NULL if no header has been reached.
 * @param headers      a vector of headers
 * @param checkBoundry
 '''
 string *ASFormatter.findHeader( vector< string*> &headers, checkBoundry)
    return ASBeautifier.findHeader(currentLine, charNum, headers, checkBoundry)


} # namespace astyle
