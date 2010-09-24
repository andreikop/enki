// $Id: ASBeautifier.cpp,v 1.4 2005/07/01 18:58:17 mandrav Exp $
// --------------------------------------------------------------------------
//
// Copyright (C) 1998,1999,2000,2001,2002 Tal Davidson.
// Copyright (C) 2004 Martin Baute.
// All rights reserved.
//
// This file is a part of "Artistic Style" - an indentation and reformatting
// tool for C, C++, C# and Java source files - http://astyle.sourceforge.net
//
// --------------------------------------------------------------------------
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
// --------------------------------------------------------------------------
//
// Patches:
// 18 March 1999 - Brian Rampel -
//       Fixed inverse insertion of spaces vs. tabs when in -t mode.

#include "astyle.h"

#include <vector>
#include <string>
#include <cctype>
#include <algorithm>
#include <iostream>

using namespace std;

namespace astyle
{

static const string * headers_[] = { &AS_IF, &AS_ELSE, &AS_FOR, &AS_WHILE,
    &AS_DO, &AS_TRY, &AS_CATCH, &AS_FINALLY, &AS_SYNCHRONIZED, &AS_SWITCH,
    &AS_CASE, &AS_DEFAULT, &AS_FOREACH, &AS_LOCK, &AS_UNSAFE, &AS_FIXED,
    &AS_GET, &AS_SET, &AS_ADD, &AS_REMOVE, &AS_TEMPLATE, &AS_CONST, &AS_STATIC,
    &AS_EXTERN
    //, &AS_PUBLIC, &AS_PRIVATE, &AS_PROTECTED, &AS_OPERATOR
};
static vector < const string * > headers( headers_, headers_ + ( sizeof(headers_) / sizeof(headers_[0]) ) );

static const string * nonParenHeaders_[] = { &AS_ELSE, &AS_DO, &AS_TRY, &AS_FINALLY,
    &AS_STATIC, &AS_CONST, &AS_EXTERN, &AS_CASE, &AS_DEFAULT, &AS_UNSAFE,
    &AS_GET, &AS_SET, &AS_ADD, &AS_REMOVE, &AS_PUBLIC, &AS_PRIVATE,
    &AS_PROTECTED, &AS_TEMPLATE, &AS_CONST
    //, &AS_ASM
};
static vector < const string * > nonParenHeaders( nonParenHeaders_, nonParenHeaders_ + ( sizeof(nonParenHeaders_) / sizeof(nonParenHeaders_[0]) ) );

static const string * preBlockStatements_[] = { &AS_CLASS, &AS_STRUCT, &AS_UNION,
    &AS_INTERFACE, &AS_NAMESPACE, &AS_THROWS, &AS_EXTERN
};
static vector < const string * > preBlockStatements( preBlockStatements_, preBlockStatements_ + ( sizeof(preBlockStatements_) / sizeof(preBlockStatements_[0]) ) );

static const string * assignmentOperators_[] = { &AS_ASSIGN, &AS_PLUS_ASSIGN,
    &AS_MINUS_ASSIGN, &AS_MULT_ASSIGN, &AS_DIV_ASSIGN, &AS_MOD_ASSIGN,
    &AS_OR_ASSIGN, &AS_AND_ASSIGN, &AS_XOR_ASSIGN, &AS_GR_GR_GR_ASSIGN,
    &AS_GR_GR_ASSIGN, &AS_LS_LS_LS_ASSIGN, &AS_LS_LS_ASSIGN, &AS_RETURN
};
static vector < const string * > assignmentOperators( assignmentOperators_, assignmentOperators_ + ( sizeof(assignmentOperators_) / sizeof( assignmentOperators_[0]) ) );

static const string * nonAssignmentOperators_[] = { &AS_EQUAL, &AS_PLUS_PLUS,
    &AS_MINUS_MINUS, &AS_NOT_EQUAL, &AS_GR_EQUAL, &AS_GR_GR_GR, &AS_GR_GR,
    &AS_LS_EQUAL, &AS_LS_LS_LS, &AS_LS_LS, &AS_ARROW, &AS_AND, &AS_OR
};
static vector < const string * > nonAssignmentOperators( nonAssignmentOperators_, nonAssignmentOperators_ + ( sizeof(nonAssignmentOperators_) / sizeof(nonAssignmentOperators_[0]) ) );

ASBeautifier::ASBeautifier(const ASBeautifier &other)
{
    waitingBeautifierStack = NULL;
    activeBeautifierStack = NULL;
    waitingBeautifierStackLengthStack = NULL;
    activeBeautifierStackLengthStack = NULL;
    headerStack  = new vector<const string*>;
    *headerStack = *other.headerStack;
    tempStacks = new vector< vector<const string*>* >;
    vector< vector<const string*>* >::iterator iter;
    for (iter = other.tempStacks->begin();
         iter != other.tempStacks->end();
         ++iter)
    {
        vector<const string*> *newVec = new vector<const string*>;
        *newVec = **iter;
        tempStacks->push_back(newVec);
    }
    blockParenDepthStack = new vector<int>;
    *blockParenDepthStack = *other.blockParenDepthStack;

    blockStatementStack = new vector<bool>;
    *blockStatementStack = *other.blockStatementStack;

    parenStatementStack =  new vector<bool>;
    *parenStatementStack = *other.parenStatementStack;

    bracketBlockStateStack = new vector<bool>;
    *bracketBlockStateStack = *other.bracketBlockStateStack;

    inStatementIndentStack = new vector<int>;
    *inStatementIndentStack = *other.inStatementIndentStack;

    inStatementIndentStackSizeStack = new vector<unsigned>;
    *inStatementIndentStackSizeStack = *other.inStatementIndentStackSizeStack;

    parenIndentStack = new vector<int>;
    *parenIndentStack = *other.parenIndentStack;

    sourceIterator = other.sourceIterator;

    indentString = other.indentString;
    currentHeader = other.currentHeader;
    previousLastLineHeader = other.previousLastLineHeader;
    immediatelyPreviousAssignmentOp = other.immediatelyPreviousAssignmentOp;
    isInQuote = other.isInQuote;
    isInComment = other.isInComment;
    isInCase = other.isInCase;
    isInQuestion = other.isInQuestion;
    isInStatement =other. isInStatement;
    isInHeader = other.isInHeader;
    sourceStyle = other.sourceStyle;
    isInOperator = other.isInOperator;
    isInTemplate = other.isInTemplate;
    isInConst = other.isInConst;
    classIndent = other.classIndent;
    isInClassHeader = other.isInClassHeader;
    isInClassHeaderTab = other.isInClassHeaderTab;
    switchIndent = other.switchIndent;
    caseIndent = other.caseIndent;
    namespaceIndent = other.namespaceIndent;
    bracketIndent = other.bracketIndent;
    blockIndent = other.blockIndent;
    labelIndent = other.labelIndent;
    preprocessorIndent = other.preprocessorIndent;
    parenDepth = other.parenDepth;
    indentLength = other.indentLength;
    blockTabCount = other.blockTabCount;
    leadingWhiteSpaces = other.leadingWhiteSpaces;
    maxInStatementIndent = other.maxInStatementIndent;
    templateDepth = other.templateDepth;
    quoteChar = other.quoteChar;
    prevNonSpaceCh = other.prevNonSpaceCh;
    currentNonSpaceCh = other.currentNonSpaceCh;
    currentNonLegalCh = other.currentNonLegalCh;
    prevNonLegalCh = other.prevNonLegalCh;
    isInConditional = other.isInConditional;
    minConditionalIndent = other.minConditionalIndent;
    prevFinalLineSpaceTabCount = other.prevFinalLineSpaceTabCount;
    prevFinalLineTabCount = other.prevFinalLineTabCount;
    emptyLineIndent = other.emptyLineIndent;
    probationHeader = other.probationHeader;
    isInDefine = other.isInDefine;
    isInDefineDefinition = other.isInDefineDefinition;
    backslashEndsPrevLine = other.backslashEndsPrevLine;
    defineTabCount = other.defineTabCount;
    eolString = other.eolString;
}

/**
 * ASBeautifier's destructor
 */
ASBeautifier::~ASBeautifier()
{
    delete( headerStack );
    delete( tempStacks );
    delete( blockParenDepthStack );
    delete( blockStatementStack );
    delete( parenStatementStack );
    delete( bracketBlockStateStack );
    delete( inStatementIndentStack );
    delete( inStatementIndentStackSizeStack );
    delete( parenIndentStack );
}

/**
 * initialize the ASBeautifier.
 *
 * init() should be called every time a ASBeautifier object is to start
 * formatting a NEW source file.
 * init() recieves an istream reference
 * that will be used to iterate through the source code.
 */
void ASBeautifier::init(istream & iter)
{
    sourceIterator = &iter;
    delete( waitingBeautifierStack );
    waitingBeautifierStack = new vector<ASBeautifier*>;

    delete( activeBeautifierStack );
    activeBeautifierStack = new vector<ASBeautifier*>;

    delete( waitingBeautifierStackLengthStack );
    waitingBeautifierStackLengthStack = new vector<int>;

    delete( activeBeautifierStackLengthStack );
    activeBeautifierStackLengthStack = new vector<int>;

    delete( headerStack );
    headerStack = new vector<const string*>;

    delete( tempStacks );
    tempStacks = new vector< vector<const string*>* >;
    tempStacks->push_back(new vector<const string*>);

    delete( blockParenDepthStack );
    blockParenDepthStack = new vector<int>;

    delete( blockStatementStack );
    blockStatementStack = new vector<bool>;

    delete( parenStatementStack );
    parenStatementStack = new vector<bool>;

    delete( bracketBlockStateStack );
    bracketBlockStateStack = new vector<bool>;
    bracketBlockStateStack->push_back(true);

    delete( inStatementIndentStack );
    inStatementIndentStack = new vector<int>;

    delete( inStatementIndentStackSizeStack );
    inStatementIndentStackSizeStack = new vector<unsigned>;
    inStatementIndentStackSizeStack->push_back(0);

    delete( parenIndentStack );
    parenIndentStack = new vector<int>;

    immediatelyPreviousAssignmentOp = NULL;
    previousLastLineHeader = NULL;

    isInQuote = false;
    isInComment = false;
    isInStatement = false;
    isInCase = false;
    isInQuestion = false;
    isInClassHeader = false;
    isInClassHeaderTab = false;
    isInHeader = false;
    isInOperator = false;
    isInTemplate = false;
    isInConst = false;
    isInConditional = false;
    templateDepth = 0;
    parenDepth=0;
    blockTabCount = 0;
    leadingWhiteSpaces = 0;
    prevNonSpaceCh = '{';
    currentNonSpaceCh = '{';
    prevNonLegalCh = '{';
    currentNonLegalCh = '{';
    prevFinalLineSpaceTabCount = 0;
    prevFinalLineTabCount = 0;
    probationHeader = NULL;
    backslashEndsPrevLine = false;
    isInDefine = false;
    isInDefineDefinition = false;
    defineTabCount = 0;
}

/**
 * check if there are any indented lines ready to be read by nextLine()
 *
 * @return    are there any indented lines ready?
 */
bool ASBeautifier::hasMoreLines() const
{
    return sourceIterator->good();
}

/**
 * get the next indented line.
 *
 * @return    indented line.
 */
string ASBeautifier::nextLine()
{
    string buffer;
    getline(*sourceIterator, buffer);
    if ( !buffer.empty() && buffer[buffer.size() - 1] == '\r' )
    {
        buffer = buffer.substr(0, buffer.size() - 1);
    }
    return beautify(buffer);
}

/**
 * beautify a line of source code.
 * every line of source code in a source code file should be sent
 * one after the other to the beautify method.
 *
 * @return      the indented line.
 * @param originalLine       the original unindented line.
 */
string ASBeautifier::beautify( const string & originalLine )
{
    TRACE_LIFE( FUNCTION, "beautifying new line" );
    TRACE( INFO, "processing '" << originalLine << "'." );
    string line;
    bool isInLineComment = false;
    bool lineStartsInComment = false;
    bool isInClass = false;
    bool isInSwitch = false;
    bool isImmediatelyAfterConst = false;
    bool isSpecialChar = false;
    char ch = ' ';
    char prevCh;
    string outBuffer; // the newly idented line is bufferd here
    int tabCount = 0;
    const string *lastLineHeader = NULL;
    bool closingBracketReached = false;
    int spaceTabCount = 0;
    char tempCh;
    unsigned headerStackSize = headerStack->size();
    //bool isLineInStatement = isInStatement;
    bool shouldIndentBrackettedLine = true;
    int lineOpeningBlocksNum = 0;
    int lineClosingBlocksNum = 0;
    bool previousLineProbation = (probationHeader != NULL);
    string::size_type i;

    static bool suppressIndent = false; // "remembering" to suppress next-line indent
    bool suppressCurrentIndent = suppressIndent; // whether the *current* line shall be indent-suppressed

    currentHeader = NULL;

    lineStartsInComment = isInComment;

    // handle and remove white spaces around the line:
    // If not in comment, first find out size of white space before line,
    // so that possible comments starting in the line continue in
    // relation to the preliminary white-space.
    // FIXME: When suppressCurrentIndent is set, LEADING whitespace must not be trimmed.
    if ( ! isInComment && ! suppressCurrentIndent )
    {
        TRACE( ENTRY, "not in comment, indent not suppressed - memorizing leading WS and trimming line" );
        leadingWhiteSpaces = 0;
        while ( leadingWhiteSpaces < originalLine.size() && isspace(originalLine[leadingWhiteSpaces]) )
        {
            leadingWhiteSpaces++;
        }
        line = trim(originalLine);
        TRACE( EXIT, "line: '" << line << "'" );
    }
    else
    {
        TRACE( ENTRY, "in comment - trimming away already registered leading WS (?)" );
        unsigned trimSize;
        for (trimSize=0;
             trimSize < originalLine.size() && trimSize < leadingWhiteSpaces && isspace(originalLine[trimSize]);
             trimSize++)
        {
            // EMPTY
        }
        line = originalLine.substr(trimSize);
        TRACE( EXIT, "line: '" << line << "'" );
    }

    // handle empty lines
    if (line.size() == 0)
    {
        TRACE( ENTRY, "line is empty" );
        if (emptyLineIndent)
        {
            TRACE( INFO, "as emptyLineIndent is set, WS is added (preLineWS(" << prevFinalLineSpaceTabCount << ", " << prevFinalLineTabCount << "))" );
            TRACE( EXIT, "'" << preLineWS(prevFinalLineSpaceTabCount, prevFinalLineTabCount) << "'" );
            return preLineWS(prevFinalLineSpaceTabCount, prevFinalLineTabCount);
        }
        else
        {
            TRACE( EXIT, "returning empty line" );
            return line;
        }
    }

    // handle preprocessor commands
    if ( ( sourceStyle != STYLE_JAVA ) && ! isInComment && ( line[0] == '#' || backslashEndsPrevLine ) )
    {
        if (line[0] == '#')
        {
            TRACE( INFO, "encountered preprocessor statement" );
            // TODO: Haven't looked into the following block yet.
            string preproc = trim( line.substr(1) );

            // When finding a multi-lined #define statement, the original beautifier...
            // 1. sets its isInDefineDefinition flag,
            // 2. clones a new beautifier that will be used for the actual indentation
            //    of the #define. This clone is put into the activeBeautifierStack in order
            //    to be called for the actual indentation.
            // The original beautifier will have isInDefineDefinition = true, isInDefine = false
            // The cloned beautifier will have   isInDefineDefinition = true, isInDefine = true
            if ( preprocessorIndent && BEGINS_WITH(preproc, "define", 6) &&  line[line.size() - 1] == '\\' )
            {
                TRACE( INFO, "...which is a multi-line #define" );

                if ( !isInDefineDefinition )
                {
                    TRACE( INFO, "isInDefineDefinition == false" );
                    ASBeautifier *defineBeautifier;

                    // this is the original beautifier
                    isInDefineDefinition = true;

                    // push a new beautifier into the active stack;
                    // this breautifier will be used for the indentation of this define
                    defineBeautifier = new ASBeautifier(*this);
                    //defineBeautifier->init();
                    //defineBeautifier->isInDefineDefinition = true;
                    //defineBeautifier->beautify("");
                    activeBeautifierStack->push_back(defineBeautifier);
                }
                else
                {
                    TRACE( INFO, "isInDefineDefinition == true" );
                    // the is the cloned beautifier that is in charge of indenting the #define.
                    isInDefine = true;
                }

            }
            else if (BEGINS_WITH(preproc, "if", 2))
            {
                TRACE( INFO, "processing #if / #ifdef / #ifndef" );
                // push a new beautifier into the stack
                waitingBeautifierStackLengthStack->push_back(waitingBeautifierStack->size());
                activeBeautifierStackLengthStack->push_back(activeBeautifierStack->size());
                waitingBeautifierStack->push_back(new ASBeautifier(*this));
            }
            else if (BEGINS_WITH(preproc, "else", 4))
            {
                TRACE( INFO, "processing #else" );
                if (!waitingBeautifierStack->empty())
                {
                    // MOVE current waiting beautifier to active stack.
                    activeBeautifierStack->push_back(waitingBeautifierStack->back());
                    waitingBeautifierStack->pop_back();
                }
            }
            else if (BEGINS_WITH(preproc, "elif", 4))
            {
                TRACE( INFO, "processing #elif" );
                if (!waitingBeautifierStack->empty())
                {
                    // append a COPY current waiting beautifier to active stack, WITHOUT deleting the original.
                    activeBeautifierStack->push_back( new ASBeautifier( *(waitingBeautifierStack->back()) ) );
                }
            } // BEGINS_WITH(preproc, "elif", 4))
            else if (BEGINS_WITH(preproc, "endif", 5))
            {
                TRACE( INFO, "processing #endif" );
                unsigned stackLength;
                ASBeautifier *beautifier;

                if ( ! waitingBeautifierStackLengthStack->empty() )
                {
                    TRACE( INFO, "clearing waitingBeautifierStack" );
                    stackLength = waitingBeautifierStackLengthStack->back();
                    waitingBeautifierStackLengthStack->pop_back();
                    // FIXME: what about the LengthStack?
                    while ( waitingBeautifierStack->size() > stackLength )
                    {
                        beautifier = waitingBeautifierStack->back();
                        waitingBeautifierStack->pop_back();
                        delete beautifier;
                    }
                }

                if ( ! activeBeautifierStackLengthStack->empty() )
                {
                    TRACE( INFO, "clearing activeBeautifierStack" );
                    stackLength = activeBeautifierStackLengthStack->back();
                    activeBeautifierStackLengthStack->pop_back();
                    // FIXME: what about the LengthStack?
                    while ( activeBeautifierStack->size() > stackLength )
                    {
                        beautifier = activeBeautifierStack->back();
                        activeBeautifierStack->pop_back();
                        delete beautifier;
                    }
                }

            } // BEGINS_WITH(preproc, "endif", 5))

        } // line[0] == '#'

        // check if the last char of current line is a backslash
        if ( line[ line.size() - 1 ] == '\\' )
        {
            TRACE( INFO, "current line ends in '\\'" );
            backslashEndsPrevLine = true;
        }
        else
        {
            TRACE( INFO, "current line does not end in '\\'" );
            backslashEndsPrevLine = false;
        }

        // check if this line ends a multi-line #define
        // if so, use the #define's cloned beautifier for the line's indentation
        // and then remove it from the active beautifier stack and delete it.
        if ( ! backslashEndsPrevLine && isInDefineDefinition && ! isInDefine )
        {
            TRACE( INFO, "last line of multi-line define" );
            string beautifiedLine;
            ASBeautifier *defineBeautifier;

            isInDefineDefinition = false;
            defineBeautifier = activeBeautifierStack->back();
            activeBeautifierStack->pop_back();

            beautifiedLine = defineBeautifier->beautify(line);
            delete defineBeautifier;
            return beautifiedLine;
        }

        // unless this is a multi-line #define, return this precompiler line as is.
        if ( ! isInDefine && ! isInDefineDefinition )
        {
            TRACE( INFO, "not a multi-line define - return as-is" );
            return originalLine;
        }

    } // end of preprocessor handling

    // if there exists any worker beautifier in the activeBeautifierStack,
    // then use it instead of this to indent the current line.
    // TODO: Check whether one of the two checks on activeBeautifierStack is redundant.
    if ( ! isInDefine && activeBeautifierStack != NULL && ! activeBeautifierStack->empty() )
    {
        TRACE( INFO, "delegating to on-stack beautifier (IS THIS EVER REACHED?)" );
        return activeBeautifierStack->back()->beautify( line );
    }

    // calculate preliminary indentation based on data from past lines
    if ( ! inStatementIndentStack->empty() )
    {
        TRACE( INFO, "getting preliminary indentation from inStatementIndentStack:" << inStatementIndentStack->back() );
        spaceTabCount = inStatementIndentStack->back();
    }

    for ( i = 0; i < headerStackSize; ++i )
    {
        isInClass = false;

        if ( blockIndent || ( ! ( i > 0 && (*headerStack)[i-1] != &AS_OPEN_BRACKET
                                        && (*headerStack)[i]   == &AS_OPEN_BRACKET ) ) )
        {
            TRACE( INFO, "reached block, adding indent" );
            ++tabCount;
        }

        if ( ( sourceStyle != STYLE_JAVA ) && ! namespaceIndent      && i > 0
                                           && (*headerStack)[i-1]    == &AS_NAMESPACE
                                           && (*headerStack)[i]      == &AS_OPEN_BRACKET )
        {
            TRACE( INFO, "reached namespace but namespaceIndent == false, removing indent" );
            --tabCount;
        }

        if ( ( sourceStyle != STYLE_JAVA ) && i > 0
                                           && (*headerStack)[i-1] == &AS_CLASS
                                           && (*headerStack)[i]   == &AS_OPEN_BRACKET )
        {
            TRACE( INFO, "reached class..." );
            if ( classIndent )
            {
                TRACE( INFO, "...adding (class) indent" );
                ++tabCount;
            }
            isInClass = true;
        }

        // is the switchIndent option is on, indent switch statements an additional indent.
        // TODO: ELSE if? Shouldn't this be just another IF? And i checked > 0 as above?
        else if ( switchIndent && i > 1
                               && (*headerStack)[i-1] == &AS_SWITCH
                               && (*headerStack)[i]   == &AS_OPEN_BRACKET )
        {
            TRACE( INFO, "reached switch block, assing indent" );
            ++tabCount;
            isInSwitch = true;
        }

    } // for ( i = 0; i < headerStackSize; ++i )

    if ( ! lineStartsInComment && ( sourceStyle != STYLE_JAVA )
                               && isInClass
                               && classIndent
                               && headerStackSize >= 2
                               && (*headerStack)[headerStackSize-2] == &AS_CLASS
                               && (*headerStack)[headerStackSize-1] == &AS_OPEN_BRACKET
                               && line[0] == '}' )
    {
        TRACE( INFO, "reached end of class (?), removing indent" );
        --tabCount;
    }
    else if ( ! lineStartsInComment && isInSwitch
                                    && switchIndent
                                    && headerStackSize >= 2
                                    && (*headerStack)[headerStackSize-2] == &AS_SWITCH
                                    && (*headerStack)[headerStackSize-1] == &AS_OPEN_BRACKET
                                    && line[0] == '}' )
    {
        TRACE( INFO, "reached end of switch block, removing indent" );
        --tabCount;
    }

    if (isInClassHeader)
    {
        TRACE( INFO, "isInClassHeader - adding two indents" );
        isInClassHeaderTab = true;
        tabCount += 2;
    }

    if (isInConditional)
    {
        TRACE( INFO, "isInConditional - removing indent" );
        --tabCount;
    } // end of indent adjust


    // parse characters in the current line.
    for ( i = 0; i < line.size(); ++i )
    {
        tempCh = line[i];
        prevCh = ch;
        ch = tempCh;

        outBuffer.append(1, ch);

        TRACE( INFO, "next char: '" << ch << "'." );
        if (isWhiteSpace(ch))
        {
            TRACE( INFO, "skipping whitespace" );
            continue;
        }

        // handle special characters (i.e. backslash + character such as \n, \t, ...)
        if (isSpecialChar)
        {
            TRACE( INFO, "skipping special (escaped) char" );
            isSpecialChar = false;
            continue;
        }
        if ( ! ( isInComment || isInLineComment ) && ( line.substr(i, 2) == "\\\\" ) )
        {
            TRACE( INFO, "encountered '\\', appending to outBuffer" );
            outBuffer.append(1, '\\');
            ++i;
            continue;
        }
        if ( ! ( isInComment || isInLineComment ) && ch=='\\' )
        {
            TRACE( INFO, "encountered '\', next char is special (escaped)" );
            isSpecialChar = true;
            continue;
        }

        // handle quotes (such as 'x' and "Hello Dolly")
        if ( ! ( isInComment || isInLineComment ) && ( ch=='"' || ch=='\'' ) )
        {
            TRACE( INFO, "encountered quote (' or \")" );
            if ( ! isInQuote )
            {
                TRACE( INFO, "this is the BEGINNING of a quote" );
                quoteChar = ch;
                isInQuote = true;
            }
            else if (quoteChar == ch)
            {
                TRACE( INFO, "this is the END of a quote" );
                isInQuote = false;
                isInStatement = true;
                continue;
            }
        }

        if (isInQuote)
        {
            TRACE( INFO, "skipping char as it is quoted" );
            continue;
        }

        // handle comments
        if ( ! ( isInComment || isInLineComment ) && CONTAINS_AT( line, AS_OPEN_LINE_COMMENT, 2, i ) )
        {
            TRACE( INFO, "this starts a line comment" );
            isInLineComment = true;
            outBuffer.append(1, '/');
            ++i;
            continue;
        }
        else if ( ! ( isInComment || isInLineComment ) && CONTAINS_AT( line, AS_OPEN_COMMENT, 2, i ) )
        {
            TRACE( INFO, "this starts a multiline comment" );
            isInComment = true;
            outBuffer.append(1, '*');
            ++i;
            continue;
        }
        else if ( ( isInComment || isInLineComment ) && CONTAINS_AT( line, AS_CLOSE_COMMENT, 2, i ) )
        {
            TRACE( INFO, "this ends a multiline comment" );
            isInComment = false;
            outBuffer.append(1, '/');
            ++i;
            continue;
        }

        if ( isInComment || isInLineComment )
        {
            TRACE( INFO, "skipping char as it is commented out." );
            continue;
        }

        // if we have reached this far then we are NOT in a comment or string of special character...
        // TODO: Haven't checked this. probationHeader?
        if ( probationHeader != NULL )
        {
            if ( ( ( probationHeader == &AS_STATIC || probationHeader == &AS_CONST ) && ch == '{' )
                 || ( probationHeader == &AS_SYNCHRONIZED && ch == '(' ) )
            {
                // insert the probation header as a new header
                isInHeader = true;
                headerStack->push_back(probationHeader);

                // handle the specific probation header
                isInConditional = (probationHeader == &AS_SYNCHRONIZED);
                if (probationHeader == &AS_CONST)
                    isImmediatelyAfterConst = true;
                //  isInConst = true;
                /* TODO:
                 * There is actually no more need for the global isInConst variable.
                 * The only reason for checking const is to see if there is a const
                 * immediately before an open-bracket.
                 * Since CONST is now put into probation and is checked during itspost-char,
                 * isImmediatelyAfterConst can be set by its own...
                 */

                isInStatement = false;
                // if the probation comes from the previous line, then indent by 1 tab count.
                if (previousLineProbation && ch == '{')
                    tabCount++;
                previousLineProbation = false;
            }

            // dismiss the probation header
            probationHeader = NULL;
        }

        // TODO: Haven't checked this.
        prevNonSpaceCh = currentNonSpaceCh;
        currentNonSpaceCh = ch;
        if ( ! isLegalNameChar( ch ) && ch != ',' && ch != ';' )
        {
            prevNonLegalCh = currentNonLegalCh;
            currentNonLegalCh = ch;
        }

        //if (isInConst)
        //{
        //    isInConst = false;
        //    isImmediatelyAfterConst = true;
        //}

        // TODO: Haven't checked this.
        if (isInHeader)
        {
            isInHeader = false;
            currentHeader = headerStack->back();
        }
        else
        {
            currentHeader = NULL;
        }

        // handle templates
        if ( ( sourceStyle != STYLE_JAVA ) && isInTemplate
                                           && ( ch == '<' || ch == '>' )
                                           &&  findHeader( line, i, nonAssignmentOperators ) == NULL)
        {
            TRACE( INFO, "isInTemplate..." ); // TODO: Extend tracing
            if (ch == '<')
            {
                ++templateDepth;
            }
            else if (ch == '>')
            {
                if (--templateDepth <= 0)
                {
                    if (isInTemplate)
                        ch = ';';
                    else
                        ch = 't';
                    isInTemplate = false;
                    templateDepth = 0;
                }
            }
        }

        // handle parenthesies
        if (ch == '(' || ch == '[' || ch == ')' || ch == ']')
        {
            if (ch == '(' || ch == '[')
            {
                if (parenDepth == 0)
                {
                    parenStatementStack->push_back(isInStatement);
                    isInStatement = true;
                }
                parenDepth++;

                inStatementIndentStackSizeStack->push_back(inStatementIndentStack->size());

                if (currentHeader != NULL)
                    registerInStatementIndent(line, i, spaceTabCount, minConditionalIndent/*indentLength*2*/, true);
                else
                    registerInStatementIndent(line, i, spaceTabCount, 0, true);
            }
            else if (ch == ')' || ch == ']')
            {
                parenDepth--;
                if (parenDepth == 0)
                {
                    isInStatement = parenStatementStack->back();
                    parenStatementStack->pop_back();
                    ch = ' ';

                    isInConditional = false;
                }

                if (!inStatementIndentStackSizeStack->empty())
                {
                    unsigned previousIndentStackSize = inStatementIndentStackSizeStack->back();
                    inStatementIndentStackSizeStack->pop_back();
                    while (previousIndentStackSize < inStatementIndentStack->size())
                        inStatementIndentStack->pop_back();

                    if (!parenIndentStack->empty())
                    {
                        int poppedIndent = parenIndentStack->back();
                        parenIndentStack->pop_back();

                        if (i == 0)
                            spaceTabCount = poppedIndent;
                    }
                }
            }

            continue;
        }


        if (ch == '{')
        {
            bool isBlockOpener = false;

            // first, check if '{' is a block-opener or an static-array opener
            isBlockOpener = ( (prevNonSpaceCh == '{' && bracketBlockStateStack->back())
                              || prevNonSpaceCh == '}'
                              || prevNonSpaceCh == ')'
                              || prevNonSpaceCh == ';'
                              || isInClassHeader
                              || isBlockOpener
                              || isImmediatelyAfterConst
                              || (isInDefine &&
                                  (prevNonSpaceCh == '('
                                   || prevNonSpaceCh == '_'
                                   || isalnum(prevNonSpaceCh))) );

            isInClassHeader = false;
            if (!isBlockOpener && currentHeader != NULL)
            {
                for (unsigned n=0; n < nonParenHeaders.size(); n++)
                    if (currentHeader == nonParenHeaders[n])
                    {
                        isBlockOpener = true;
                        break;
                    }
            }
            bracketBlockStateStack->push_back(isBlockOpener);
            if (!isBlockOpener)
            {
                inStatementIndentStackSizeStack->push_back(inStatementIndentStack->size());
                registerInStatementIndent(line, i, spaceTabCount, 0, true);
                parenDepth++;
                if (i == 0)
                    shouldIndentBrackettedLine = false;

                continue;
            }

            // this bracket is a block opener...

            ++lineOpeningBlocksNum;

            if (isInClassHeader)
                isInClassHeader = false;
            if (isInClassHeaderTab)
            {
                isInClassHeaderTab = false;
                tabCount -= 2;
            }

            blockParenDepthStack->push_back(parenDepth);
            blockStatementStack->push_back(isInStatement);

            inStatementIndentStackSizeStack->push_back(inStatementIndentStack->size());

            blockTabCount += isInStatement? 1 : 0;
            parenDepth = 0;
            isInStatement = false;

            tempStacks->push_back(new vector<const string*>);
            headerStack->push_back(&AS_OPEN_BRACKET);
            lastLineHeader = &AS_OPEN_BRACKET; // <------

            continue;
        }

        //check if a header has been reached
        if (prevCh == ' ')
        {
            bool isIndentableHeader = true;
            const string *newHeader = findHeader(line, i, headers);
            if (newHeader != NULL)
            {
                // if we reached here, then this is a header...
                isInHeader = true;

                vector<const string*> *lastTempStack;
                if (tempStacks->empty())
                    lastTempStack = NULL;
                else
                    lastTempStack = tempStacks->back();

                // if a new block is opened, push a new stack into tempStacks to hold the
                // future list of headers in the new block.

                // take care of the special case: 'else if (...)'
                if (newHeader == &AS_IF && lastLineHeader == &AS_ELSE)
                {
                    //spaceTabCount += indentLength; // to counter the opposite addition that occurs when the 'if' is registered below...
                    headerStack->pop_back();
                }

                // take care of 'else'
                else if (newHeader == &AS_ELSE)
                {
                    if (lastTempStack != NULL)
                    {
                        int indexOfIf = indexOf(*lastTempStack, &AS_IF); // <---
                        if (indexOfIf != -1)
                        {
                            // recreate the header list in headerStack up to the previous 'if'
                            // from the temporary snapshot stored in lastTempStack.
                            int restackSize = lastTempStack->size() - indexOfIf - 1;
                            for (int r=0; r<restackSize; r++)
                            {
                                headerStack->push_back(lastTempStack->back());
                                lastTempStack->pop_back();
                            }
                            if (!closingBracketReached)
                                tabCount += restackSize;
                        }
                        /*
                         * If the above if is not true, i.e. no 'if' before the 'else',
                         * then nothing beautiful will come out of this...
                         * I should think about inserting an Exception here to notify the caller of this...
                         */
                    }
                }

                // check if 'while' closes a previous 'do'
                else if (newHeader == &AS_WHILE)
                {
                    if (lastTempStack != NULL)
                    {
                        int indexOfDo = indexOf(*lastTempStack, &AS_DO); // <---
                        if (indexOfDo != -1)
                        {
                            // recreate the header list in headerStack up to the previous 'do'
                            // from the temporary snapshot stored in lastTempStack.
                            int restackSize = lastTempStack->size() - indexOfDo - 1;
                            for (int r=0; r<restackSize; r++)
                            {
                                headerStack->push_back(lastTempStack->back());
                                lastTempStack->pop_back();
                            }
                            if (!closingBracketReached)
                                tabCount += restackSize;
                        }
                    }
                }
                // check if 'catch' closes a previous 'try' or 'catch'
                else if (newHeader == &AS_CATCH || newHeader == &AS_FINALLY)
                {
                    if (lastTempStack != NULL)
                    {
                        int indexOfTry = indexOf(*lastTempStack, &AS_TRY);
                        if (indexOfTry == -1)
                            indexOfTry = indexOf(*lastTempStack, &AS_CATCH);
                        if (indexOfTry != -1)
                        {
                            // recreate the header list in headerStack up to the previous 'try'
                            // from the temporary snapshot stored in lastTempStack.
                            int restackSize = lastTempStack->size() - indexOfTry - 1;
                            for (int r=0; r<restackSize; r++)
                            {
                                headerStack->push_back(lastTempStack->back());
                                lastTempStack->pop_back();
                            }

                            if (!closingBracketReached)
                                tabCount += restackSize;
                        }
                    }
                }
                else if (newHeader == &AS_CASE)
                {
                    isInCase = true;
                    if (!caseIndent)
                        --tabCount;
                }
                else if(newHeader == &AS_DEFAULT)
                {
                    isInCase = true;
                    if (!caseIndent)
                        --tabCount;
                }
                else if (newHeader == &AS_PUBLIC || newHeader == &AS_PROTECTED || newHeader == &AS_PRIVATE)
                {
                    if (( sourceStyle != STYLE_JAVA ) && !isInClassHeader)
                        --tabCount;
                    isIndentableHeader = false;
                }
                //else if ((newHeader == &STATIC || newHeader == &SYNCHRONIZED) &&
                //         !headerStack->empty() &&
                //         (headerStack->back() == &STATIC || headerStack->back() == &SYNCHRONIZED))
                //{
                //    isIndentableHeader = false;
                //}
                else if (newHeader == &AS_STATIC
                         || newHeader == &AS_SYNCHRONIZED
                         || (newHeader == &AS_CONST && ( sourceStyle != STYLE_JAVA )))
                {
                    if (!headerStack->empty() &&
                            (headerStack->back() == &AS_STATIC
                             || headerStack->back() == &AS_SYNCHRONIZED
                             || headerStack->back() == &AS_CONST))
                    {
                        isIndentableHeader = false;
                    }
                    else
                    {
                        isIndentableHeader = false;
                        probationHeader = newHeader;
                    }
                }
                else if (newHeader == &AS_CONST)
                {
                    // this will be entered only if NOT in C style
                    // since otherwise the CONST would be found to be a probstion header...

                    //if (sourceStyle != STYLE_JAVA)
                    //  isInConst = true;
                    isIndentableHeader = false;
                }
                else if ( (sourceStyle != STYLE_CSHARP) &&
                          (newHeader == &AS_FOREACH || newHeader == &AS_LOCK
                        || newHeader == &AS_UNSAFE  || newHeader == &AS_FIXED
                        || newHeader == &AS_GET     || newHeader == &AS_SET
                        || newHeader == &AS_ADD     || newHeader == &AS_REMOVE ) )
                {
                    // this will be entered only if in C# style
                    isIndentableHeader = false;
                }
                /*
                              else if (newHeader == &OPERATOR)
                              {
                                  if (( sourceStyle != STYLE_JAVA ))
                                      isInOperator = true;
                                  isIndentableHeader = false;
                              }
                */
                else if (newHeader == &AS_TEMPLATE)
                {
                    if (( sourceStyle != STYLE_JAVA ))
                        isInTemplate = true;
                    isIndentableHeader = false;
                }


                if (isIndentableHeader)
                {
                    // 3.2.99
                    //spaceTabCount-=indentLength;
                    headerStack->push_back(newHeader);
                    isInStatement = false;
                    if (indexOf(nonParenHeaders, newHeader) == -1)
                    {
                        isInConditional = true;
                    }
                    lastLineHeader = newHeader;
                }
                else
                    isInHeader = false;

                //lastLineHeader = newHeader;

                outBuffer.append(newHeader->substr(1));
                i += newHeader->length() - 1;

                continue;
            }
        }

        if (( sourceStyle != STYLE_JAVA ) && !isalpha(prevCh)
                                          && CONTAINS_AT(line, AS_OPERATOR, 8, i)
                                          && !isalnum(line[i+8]))
        {
            isInOperator = true;
            outBuffer.append(AS_OPERATOR.substr(1));
            i += 7;
            continue;
        }

        if (ch == '?')
            isInQuestion = true;

        // special handling of 'case' statements
        if (ch == ':')
        {
            if (line.size() > i+1 && line[i+1] == ':') // look for ::
            {
                ++i;
                outBuffer.append(1, ':');
                ch = ' ';
                continue;
            }

            else if (( sourceStyle != STYLE_JAVA ) && isInClass && prevNonSpaceCh != ')')
            {
                --tabCount;
                // found a 'private:' or 'public:' inside a class definition
                // so do nothing special
            }

            else if (( sourceStyle != STYLE_JAVA ) && isInClassHeader)
            {

                // found a 'class A : public B' definition
                // so do nothing special
            }

            else if (isInQuestion)
            {
                isInQuestion = false;
            }
            else if (( sourceStyle != STYLE_JAVA ) && prevNonSpaceCh == ')')
            {
                isInClassHeader = true;
                if (i==0)
                    tabCount += 2;
            }
            else
            {
                currentNonSpaceCh = ';'; // so that brackets after the ':' will appear as block-openers
                if (isInCase)
                {
                    isInCase = false;
                    ch = ';'; // from here on, treat char as ';'
                }


                else // is in a label (e.g. 'label1:')
                {
                    if (labelIndent)
                        --tabCount; // unindent label by one indent
                    else
                        tabCount = 0; // completely flush indent to left
                }



            }
        }

        if ((ch == ';'  || (parenDepth>0 && ch == ','))  && !inStatementIndentStackSizeStack->empty())
            while (inStatementIndentStackSizeStack->back() + (parenDepth>0 ? 1 : 0)  < inStatementIndentStack->size())
                inStatementIndentStack->pop_back();


        // handle ends of statements
        if ( (ch == ';' && parenDepth == 0) || ch == '}'/* || (ch == ',' && parenDepth == 0)*/)
        {
            if (ch == '}')
            {
                // first check if this '}' closes a previous block, or a static array...
                if (!bracketBlockStateStack->empty())
                {
                    bool bracketBlockState = bracketBlockStateStack->back();
                    bracketBlockStateStack->pop_back();
                    if (!bracketBlockState)
                    {
                        if (!inStatementIndentStackSizeStack->empty())
                        {
                            // this bracket is a static array

                            unsigned previousIndentStackSize = inStatementIndentStackSizeStack->back();
                            inStatementIndentStackSizeStack->pop_back();
                            while (previousIndentStackSize < inStatementIndentStack->size())
                                inStatementIndentStack->pop_back();
                            parenDepth--;
                            if (i == 0)
                                shouldIndentBrackettedLine = false;

                            if (!parenIndentStack->empty())
                            {
                                int poppedIndent = parenIndentStack->back();
                                parenIndentStack->pop_back();
                                if (i == 0)
                                    spaceTabCount = poppedIndent;
                            }
                        }
                        continue;
                    }
                }

                // this bracket is block closer...

                ++lineClosingBlocksNum;

                if(!inStatementIndentStackSizeStack->empty())
                    inStatementIndentStackSizeStack->pop_back();

                if (!blockParenDepthStack->empty())
                {
                    parenDepth = blockParenDepthStack->back();
                    blockParenDepthStack->pop_back();
                    isInStatement = blockStatementStack->back();
                    blockStatementStack->pop_back();

                    if (isInStatement)
                        blockTabCount--;
                }

                closingBracketReached = true;
                int headerPlace = indexOf(*headerStack, &AS_OPEN_BRACKET); // <---
                if (headerPlace != -1)
                {
                    const string *popped = headerStack->back();
                    while (popped != &AS_OPEN_BRACKET)
                    {
                        headerStack->pop_back();
                        popped = headerStack->back();
                    }
                    headerStack->pop_back();

                    if (!tempStacks->empty())
                    {
                        vector<const string*> *temp =  tempStacks->back();
                        tempStacks->pop_back();
                        delete temp;
                    }
                }


                ch = ' '; // needed due to cases such as '}else{', so that headers ('else' in this case) will be identified...
            }

            /*
             * Create a temporary snapshot of the current block's header-list in the
             * uppermost inner stack in tempStacks, and clear the headerStack up to
             * the begining of the block.
             * Thus, the next future statement will think it comes one indent past
             * the block's '{' unless it specifically checks for a companion-header
             * (such as a previous 'if' for an 'else' header) within the tempStacks,
             * and recreates the temporary snapshot by manipulating the tempStacks.
             */
            if (!tempStacks->back()->empty())
                while (!tempStacks->back()->empty())
                    tempStacks->back()->pop_back();
            while (!headerStack->empty() && headerStack->back() != &AS_OPEN_BRACKET)
            {
                tempStacks->back()->push_back(headerStack->back());
                headerStack->pop_back();
            }

            if (parenDepth == 0 && ch == ';')
                isInStatement=false;

            isInClassHeader = false;

            continue;
        }


        // check for preBlockStatements ONLY if not within parenthesies
        // (otherwise 'struct XXX' statements would be wrongly interpreted...)
        if (prevCh == ' ' && !isInTemplate && parenDepth == 0)
        {
            const string *newHeader = findHeader(line, i, preBlockStatements);
            if (newHeader != NULL)
            {
                isInClassHeader = true;
                outBuffer.append(newHeader->substr(1));
                i += newHeader->length() - 1;
                //if (( sourceStyle != STYLE_JAVA ))
                headerStack->push_back(newHeader);
            }
        }

        // Handle operators
        //

////        // PRECHECK if a '==' or '--' or '++' operator was reached.
////        // If not, then register an indent IF an assignment operator was reached.
////        // The precheck is important, so that statements such as 'i--==2' are not recognized
////        // to have assignment operators (here, '-=') in them . . .

        const string *foundAssignmentOp = NULL;
        const string *foundNonAssignmentOp = NULL;

        immediatelyPreviousAssignmentOp = NULL;

        // Check if an operator has been reached.
        foundAssignmentOp = findHeader(line, i, assignmentOperators, false);
        foundNonAssignmentOp = findHeader(line, i, nonAssignmentOperators, false);

        // Since findHeader's boundry checking was not used above, it is possible
        // that both an assignment op and a non-assignment op where found,
        // e.g. '>>' and '>>='. If this is the case, treat the LONGER one as the
        // found operator.
        if (foundAssignmentOp != NULL && foundNonAssignmentOp != NULL)
            if (foundAssignmentOp->length() < foundNonAssignmentOp->length())
                foundAssignmentOp = NULL;
            else
                foundNonAssignmentOp = NULL;

        if (foundNonAssignmentOp != NULL)
        {
            if (foundNonAssignmentOp->length() > 1)
            {
                outBuffer.append(foundNonAssignmentOp->substr(1));
                i += foundNonAssignmentOp->length() - 1;
            }
        }

        else if (foundAssignmentOp != NULL)
        {
            if (foundAssignmentOp->length() > 1)
            {
                outBuffer.append(foundAssignmentOp->substr(1));
                i += foundAssignmentOp->length() - 1;
            }

            if (!isInOperator && !isInTemplate)
            {
                registerInStatementIndent(line, i, spaceTabCount, 0, false);
                immediatelyPreviousAssignmentOp = foundAssignmentOp;
                isInStatement = true;
            }
        }

        if (isInOperator)
            isInOperator = false;
    }

    // handle special cases of unindentation:

    /*
     * if '{' doesn't follow an immediately previous '{' in the headerStack
     * (but rather another header such as "for" or "if", then unindent it
     * by one indentation relative to its block.
     */
    //    cerr << endl << lineOpeningBlocksNum << " " <<  lineClosingBlocksNum << " " <<  previousLastLineHeader << endl;

    // indent #define lines with one less tab
    //if (isInDefine)
    //    tabCount -= defineTabCount-1;


    if (!lineStartsInComment
            && !blockIndent
            && outBuffer.size()>0
            && outBuffer[0]=='{'
            && !(lineOpeningBlocksNum > 0 && lineOpeningBlocksNum == lineClosingBlocksNum)
            && !(headerStack->size() > 1 && (*headerStack)[headerStack->size()-2] == &AS_OPEN_BRACKET)
            && shouldIndentBrackettedLine)
        --tabCount;

    else if (!lineStartsInComment
            && outBuffer.size()>0
            && outBuffer[0]=='}'
            && shouldIndentBrackettedLine )
        --tabCount;

    // correctly indent one-line-blocks...
    else if (!lineStartsInComment
             && outBuffer.size()>0
             && lineOpeningBlocksNum > 0
             && lineOpeningBlocksNum == lineClosingBlocksNum
             && previousLastLineHeader != NULL
             && previousLastLineHeader != &AS_OPEN_BRACKET)
        tabCount -= 1; //lineOpeningBlocksNum - (blockIndent ? 1 : 0);

    if (tabCount < 0)
        tabCount = 0;

    // take care of extra bracket indentatation option...
    if (bracketIndent && outBuffer.size()>0 && shouldIndentBrackettedLine)
        if (outBuffer[0]=='{' || outBuffer[0]=='}')
            tabCount++;


    if (isInDefine)
    {
        if (outBuffer[0] == '#')
        {
            string preproc = trim(string(outBuffer.c_str() + 1));
            if (BEGINS_WITH(preproc, "define", 6))
            {
                if (!inStatementIndentStack->empty()
                        && inStatementIndentStack->back() > 0)
                {
                    defineTabCount = tabCount;
                }
                else
                {
                    defineTabCount = tabCount - 1;
                    tabCount--;
                }
            }
        }

        tabCount -= defineTabCount;
    }

    if (tabCount < 0)
        tabCount = 0;

    // For multi-line string constants, suppress indent of next line (bug #417767).
    if ( isInQuote && line[ line.size() - 1 ] == '\\' )
    {
        TRACE( INFO, "Line ends with continued quote - suppressing indent of next line." );
        suppressIndent = true;
    }
    else
    {
        suppressIndent = false;
    }

    // finally, insert indentations into begining of line
    prevFinalLineSpaceTabCount = spaceTabCount;
    prevFinalLineTabCount = tabCount;
 
    if (forceTabIndent)
    {
        tabCount += spaceTabCount / indentLength;
        spaceTabCount = spaceTabCount % indentLength;
    }

    // attempted bugfix #417767
    if ( ! suppressCurrentIndent )
    {
        outBuffer = preLineWS(spaceTabCount,tabCount) + outBuffer;
    }

    if (lastLineHeader != NULL)
    {
        previousLastLineHeader = lastLineHeader;
    }

    return outBuffer;
}


string ASBeautifier::preLineWS(int spaceTabCount, int tabCount)
{
    string ws;

    for (int i=0; i<tabCount; i++)
        ws += indentString;

    while ((spaceTabCount--) > 0)
        ws += string(" ");

    return ws;
}

/*
 * register an in-statement indent.
 */
void ASBeautifier::registerInStatementIndent(const string &line, int i, int spaceTabCount,
        int minIndent, bool updateParenStack)
{
    int inStatementIndent;
    int remainingCharNum = line.size() - i;
    int nextNonWSChar = 1;

    nextNonWSChar = getNextProgramCharDistance(line, i);

    // if indent is around the last char in the line, indent instead 2 spaces from the previous indent
    if (nextNonWSChar == remainingCharNum)
    {
        int previousIndent = spaceTabCount;
        if (!inStatementIndentStack->empty())
            previousIndent = inStatementIndentStack->back();

        inStatementIndentStack->push_back(/*2*/ indentLength + previousIndent );
        if (updateParenStack)
            parenIndentStack->push_back( previousIndent );
        return;
    }

    if (updateParenStack)
        parenIndentStack->push_back(i+spaceTabCount);

    inStatementIndent = i + nextNonWSChar + spaceTabCount;

    if (i + nextNonWSChar < minIndent)
        inStatementIndent = minIndent + spaceTabCount;

    if (i + nextNonWSChar > maxInStatementIndent)
        inStatementIndent =  indentLength*2 + spaceTabCount;



    if (!inStatementIndentStack->empty() &&
            inStatementIndent < inStatementIndentStack->back())
        inStatementIndent = inStatementIndentStack->back();

    inStatementIndentStack->push_back(inStatementIndent);
}

/**
 * get distance to the next non-white sspace, non-comment character in the line.
 * if no such character exists, return the length remaining to the end of the line.
 */
int ASBeautifier::getNextProgramCharDistance(const string &line, int i)
{
    bool inComment = false;
    int remainingCharNum = line.size() - i;
    int charDistance = 1;
    int ch;

    for (charDistance = 1; charDistance < remainingCharNum; charDistance++)
    {
        ch = line[i + charDistance];
        if (inComment)
        {
            if (CONTAINS_AT(line, AS_CLOSE_COMMENT, 2, i + charDistance))
            {
                charDistance++;
                inComment = false;
            }
            continue;
        }
        else if (isWhiteSpace(ch))
            continue;
        else if (ch == '/')
        {
            if (CONTAINS_AT(line, AS_OPEN_LINE_COMMENT, 2, i + charDistance))
                return remainingCharNum;
            else if (CONTAINS_AT(line, AS_OPEN_COMMENT, 2, i + charDistance))
            {
                charDistance++;
                inComment = true;
            }
        }
        else
            return charDistance;
    }

    return charDistance;
}


/**
 * check if a specific character can be used in a legal variable/method/class name
 *
 * @return          legality of the char.
 * @param ch        the character to be checked.
 */
bool ASBeautifier::isLegalNameChar(char ch) const
{
    return (isalnum(ch) //(ch>='a' && ch<='z') || (ch>='A' && ch<='Z') || (ch>='0' && ch<='9') ||
            || ch=='.' || ch=='_' || (!( sourceStyle != STYLE_JAVA ) && ch=='$') || (( sourceStyle != STYLE_JAVA ) && ch=='~'));
}

/**
 * check if a specific line position contains a header, out of several possible headers.
 *
 * @return    a pointer to the found header. if no header was found then return NULL.
 */
const string *ASBeautifier::findHeader(const string &line, int i, const vector<const string*> &possibleHeaders, bool checkBoundry)
{
    int maxHeaders = possibleHeaders.size();
    const string *header = NULL;
    int p;

    for (p=0; p < maxHeaders; p++)
    {
        header = possibleHeaders[p];

        if (CONTAINS_AT(line, *header, header->size(), i))
        {
            // check that this is a header and not a part of a longer word
            // (e.g. not at its begining, not at its middle...)

            int lineLength = line.size();
            int headerEnd = i + header->length();
            char startCh = (*header)[0];   // first char of header
            char endCh = 0;                // char just after header
            char prevCh = 0;               // char just before header

            if (headerEnd < lineLength)
            {
                endCh = line[headerEnd];
            }
            if (i > 0)
            {
                prevCh = line[i-1];
            }

            if (!checkBoundry)
            {
                return header;
            }
            else if (prevCh != 0
                        && isLegalNameChar(startCh)
                        && isLegalNameChar(prevCh))
            {
                return NULL;
            }
            else if (headerEnd >= lineLength
                    || !isLegalNameChar(startCh)
                    || !isLegalNameChar(endCh))
            {
                return header;
            }
            else
            {
                return NULL;
            }
        }
    }

    return NULL;
}


/**
 * check if a specific character can be used in a legal variable/method/class name
 *
 * @return          legality of the char.
 * @param ch        the character to be checked.
 */
bool ASBeautifier::isWhiteSpace(char ch) const
{
    return (ch == ' ' || ch == '\t');
}

/**
 * find the index number of a string element in a container of strings
 *
 * @return              the index number of element in the ocntainer. -1 if element not found.
 * @param container     a vector of strings.
 * @param element       the element to find .
 */
int ASBeautifier::indexOf(vector<const string*> &container, const string *element)
{
    vector<const string*>::const_iterator where;

    where= find(container.begin(), container.end(), element);
    if (where == container.end())
        return -1;
    else
        return where - container.begin();
}

/**
 * trim removes the white space surrounding a line.
 *
 * @return          the trimmed line.
 * @param str       the line to trim.
 */
string ASBeautifier::trim(const string &str)
{
    int start = 0;
    int end = str.size() - 1;

    while (start < end && isWhiteSpace(str[start]))
        start++;

    while (start <= end && isWhiteSpace(str[end]))
        end--;

    string returnStr(str, start, end+1-start);
    return returnStr;
}

} // namespace astyle
