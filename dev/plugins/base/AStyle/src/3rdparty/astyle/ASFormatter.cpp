// $Id: ASFormatter.cpp,v 1.4 2005/07/01 18:58:17 mandrav Exp $
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
// Patches:
// 26 November 1998 - Richard Bullington -
//        A correction of line-breaking in headers following '}',
//        was created using a variation of a  patch by Richard Bullington.

#include "astyle.h"

#include <string>
#include <cctype>
#include <vector>
#include <algorithm>
#include <iostream>

using namespace std;

namespace astyle
{

int Tracer::mIndent = 0;

std::string const AS_IF                = "if";
std::string const AS_ELSE              = "else";
std::string const AS_FOR               = "for";
std::string const AS_DO                = "do";
std::string const AS_WHILE             = "while";
std::string const AS_SWITCH            = "switch";
std::string const AS_CASE              = "case";
std::string const AS_DEFAULT           = "default";
std::string const AS_CLASS             = "class";
std::string const AS_STRUCT            = "struct";
std::string const AS_UNION             = "union";
std::string const AS_INTERFACE         = "interface";
std::string const AS_NAMESPACE         = "namespace";
std::string const AS_EXTERN            = "extern";
std::string const AS_PUBLIC            = "public";
std::string const AS_PROTECTED         = "protected";
std::string const AS_PRIVATE           = "private";
std::string const AS_STATIC            = "static";
std::string const AS_SYNCHRONIZED      = "synchronized";
std::string const AS_OPERATOR          = "operator";
std::string const AS_TEMPLATE          = "template";
std::string const AS_TRY               = "try";
std::string const AS_CATCH             = "catch";
std::string const AS_FINALLY           = "finally";
std::string const AS_THROWS            = "throws";
std::string const AS_CONST             = "const";

std::string const AS_ASM               = "asm";

std::string const AS_BAR_DEFINE        = "#define";
std::string const AS_BAR_INCLUDE       = "#include";
std::string const AS_BAR_IF            = "#if";
std::string const AS_BAR_EL            = "#el";
std::string const AS_BAR_ENDIF         = "#endif";

std::string const AS_OPEN_BRACKET      = "{";
std::string const AS_CLOSE_BRACKET     = "}";
std::string const AS_OPEN_LINE_COMMENT = "//";
std::string const AS_OPEN_COMMENT      = "/*";
std::string const AS_CLOSE_COMMENT         = "*/";

std::string const AS_ASSIGN            = "=";
std::string const AS_PLUS_ASSIGN       = "+=";
std::string const AS_MINUS_ASSIGN      = "-=";
std::string const AS_MULT_ASSIGN       = "*=";
std::string const AS_DIV_ASSIGN        = "/=";
std::string const AS_MOD_ASSIGN        = "%=";
std::string const AS_OR_ASSIGN         = "|=";
std::string const AS_AND_ASSIGN        = "&=";
std::string const AS_XOR_ASSIGN        = "^=";
std::string const AS_GR_GR_ASSIGN      = ">>=";
std::string const AS_LS_LS_ASSIGN      = "<<=";
std::string const AS_GR_GR_GR_ASSIGN   = ">>>=";
std::string const AS_LS_LS_LS_ASSIGN   = "<<<=";
std::string const AS_RETURN            = "return";

std::string const AS_EQUAL             = "==";
std::string const AS_PLUS_PLUS         = "++";
std::string const AS_MINUS_MINUS       = "--";
std::string const AS_NOT_EQUAL         = "!=";
std::string const AS_GR_EQUAL          = ">=";
std::string const AS_GR_GR             = ">>";
std::string const AS_GR_GR_GR          = ">>>";
std::string const AS_LS_EQUAL          = "<=";
std::string const AS_LS_LS             = "<<";
std::string const AS_LS_LS_LS          = "<<<";
std::string const AS_ARROW             = "->";
std::string const AS_AND               = "&&";
std::string const AS_OR                = "||";
std::string const AS_COLON_COLON       = "::";
std::string const AS_PAREN_PAREN       = "()";
std::string const AS_BLPAREN_BLPAREN   = "[]";

std::string const AS_PLUS              = "+";
std::string const AS_MINUS             = "-";
std::string const AS_MULT              = "*";
std::string const AS_DIV               = "/";
std::string const AS_MOD               = "%";
std::string const AS_GR                = ">";
std::string const AS_LS                = "<";
std::string const AS_NOT               = "!";
std::string const AS_BIT_OR            = "|";
std::string const AS_BIT_AND           = "&";
std::string const AS_BIT_NOT           = "~";
std::string const AS_BIT_XOR           = "^";
std::string const AS_QUESTION          = "?";
std::string const AS_COLON             = ":";
std::string const AS_COMMA             = ",";
std::string const AS_SEMICOLON         = ";";

std::string const AS_FOREACH           = "foreach";
std::string const AS_LOCK              = "lock";
std::string const AS_UNSAFE            = "unsafe";
std::string const AS_FIXED             = "fixed";
std::string const AS_GET               = "get";
std::string const AS_SET               = "set";
std::string const AS_ADD               = "add";
std::string const AS_REMOVE            = "remove";

static const string * headers_[] = { &AS_IF, &AS_ELSE, &AS_DO, &AS_WHILE, &AS_FOR,
    &AS_SYNCHRONIZED, &AS_TRY, &AS_CATCH, &AS_FINALLY, &AS_SWITCH, &AS_TEMPLATE,
    &AS_FOREACH, &AS_LOCK, &AS_UNSAFE, &AS_FIXED, &AS_GET, &AS_SET, &AS_ADD,
    &AS_REMOVE
};
static vector< const string * > headers( headers_, headers_ + ( sizeof(headers_) / sizeof(headers_[0] ) ) );

static const string * nonParenHeaders_[] = { &AS_ELSE, &AS_DO, &AS_TRY, &AS_FINALLY,
    &AS_UNSAFE, &AS_GET, &AS_SET, &AS_ADD, &AS_REMOVE
    //, &AS_TEMPLATE
};
static vector< const string * > nonParenHeaders( nonParenHeaders_, nonParenHeaders_ + ( sizeof(nonParenHeaders_) / sizeof(nonParenHeaders_[0] ) ) );

static const string * preDefinitionHeaders_[] = { &AS_CLASS, &AS_INTERFACE,
    &AS_NAMESPACE, &AS_STRUCT
};
static vector< const string * > preDefinitionHeaders( preDefinitionHeaders_, preDefinitionHeaders_ + ( sizeof(preDefinitionHeaders_) / sizeof(preDefinitionHeaders_[0] ) ) );

static const string * preCommandHeaders_[] = { &AS_EXTERN, &AS_THROWS, &AS_CONST
};
static vector< const string * > preCommandHeaders( preCommandHeaders_, preCommandHeaders_ + ( sizeof(preCommandHeaders_) / sizeof(preCommandHeaders_[0] ) ) );

static const string * preprocessorHeaders_[] = { &AS_BAR_DEFINE
    //, &AS_BAR_INCLUDE, &AS_BAR_IF, &AS_BAR_EL, &AS_BAR_ENDIF
};
static vector< const string * > preprocessorHeaders( preprocessorHeaders_, preprocessorHeaders_+ ( sizeof(preprocessorHeaders_) / sizeof(preprocessorHeaders_[0] ) ) );

static const string * operators_[] = { &AS_PLUS_ASSIGN, &AS_MINUS_ASSIGN,
    &AS_MULT_ASSIGN, &AS_DIV_ASSIGN, &AS_MOD_ASSIGN, &AS_OR_ASSIGN,
    &AS_AND_ASSIGN, &AS_XOR_ASSIGN, &AS_EQUAL, &AS_PLUS_PLUS,
    &AS_MINUS_MINUS, &AS_NOT_EQUAL, &AS_GR_EQUAL, &AS_GR_GR_GR_ASSIGN,
    &AS_GR_GR_ASSIGN, &AS_GR_GR_GR, &AS_GR_GR, &AS_LS_EQUAL,
    &AS_LS_LS_LS_ASSIGN, &AS_LS_LS_ASSIGN, &AS_LS_LS_LS, &AS_LS_LS,
    &AS_ARROW, &AS_AND, &AS_OR, &AS_COLON_COLON, &AS_PLUS, &AS_MINUS,
    &AS_MULT, &AS_DIV, &AS_MOD, &AS_QUESTION, &AS_COLON, &AS_ASSIGN,
    &AS_LS, &AS_GR, &AS_NOT, &AS_BIT_OR, &AS_BIT_AND, &AS_BIT_NOT,
    &AS_BIT_XOR, &AS_OPERATOR, &AS_COMMA, &AS_RETURN
    //, &AS_PAREN_PAREN, &AS_BLPAREN_BLPAREN, &AS_SEMICOLON
};
static vector< const string * > operators( operators_, operators_ + ( sizeof(operators_) / sizeof(operators_[0]) ) );

static const string * assignmentOperators_[] = { &AS_PLUS_ASSIGN, &AS_MINUS_ASSIGN,
    &AS_MULT_ASSIGN, &AS_DIV_ASSIGN, &AS_MOD_ASSIGN, &AS_XOR_ASSIGN,
    &AS_OR_ASSIGN, &AS_AND_ASSIGN, &AS_GR_GR_GR_ASSIGN, &AS_LS_LS_LS_ASSIGN,
    &AS_ASSIGN
};
static vector< const string * > assignmentOperators( assignmentOperators_, assignmentOperators_ + ( sizeof(assignmentOperators_) / sizeof(assignmentOperators_[0]) ) );

/**
 * initialize the ASFormatter.
 *
 * init() should be called every time a ASFormatter object is to start
 * formatting a NEW source file.
 * init() recieves an istream reference
 * that will be used to iterate through the source code.
 */
void ASFormatter::init(istream & si)
{
    ASBeautifier::init(si);
    sourceIterator = &si;

    delete( preBracketHeaderStack );
    preBracketHeaderStack = new vector<const string*>;

    delete( bracketTypeStack );
    bracketTypeStack = new vector<BracketType>;
    bracketTypeStack->push_back(DEFINITION_TYPE);

    delete( parenStack );
    parenStack = new vector<int>;
    parenStack->push_back(0);

    currentHeader = NULL;
    currentLine = string("");
    formattedLine = "";
    currentChar = ' ';
    previousCommandChar = ' ';
    previousNonWSChar = ' ';
    quoteChar = '"';
    charNum = 0;
    previousOperator = NULL;

    isVirgin = true;
    isInLineComment = false;
    isInComment = false;
    isInPreprocessor = false;
    doesLineStartComment = false;
    isInQuote = false;
    isSpecialChar = false;
    isNonParenHeader = true;
    foundPreDefinitionHeader = false;
    foundPreCommandHeader = false;
    foundQuestionMark = false;
    isInLineBreak = false;
    endOfCodeReached = false;
    isLineReady = false;
    isPreviousBracketBlockRelated = true;
    isInPotentialCalculation = false;
    //foundOneLineBlock = false;
    shouldReparseCurrentChar = false;
    passedSemicolon = false;
    passedColon = false;
    isInTemplate = false;
    shouldBreakLineAfterComments = false;
    isImmediatelyPostComment = false;
    isImmediatelyPostLineComment = false;
    isImmediatelyPostEmptyBlock = false;

    isPrependPostBlockEmptyLineRequested = false;
    isAppendPostBlockEmptyLineRequested = false;
    prependEmptyLine = false;

    foundClosingHeader = false;
    previousReadyFormattedLineLength = 0;

    isImmediatelyPostHeader = false;
    isInHeader = false;
}

/**
 * get the next formatted line.
 *
 * @return    formatted line.
 */
string ASFormatter::nextLine()
{
    TRACE_LIFE( FUNCTION, "formatting new line." );
    const string *newHeader;
    bool isCharImmediatelyPostComment = false;
    bool isPreviousCharPostComment = false;
    bool isCharImmediatelyPostLineComment = false;
    bool isInVirginLine = isVirgin;
    bool isCharImmediatelyPostOpenBlock = false;
    bool isCharImmediatelyPostCloseBlock = false;
    bool isCharImmediatelyPostTemplate = false;
    bool isCharImmediatelyPostHeader = false;

    if ( ! isFormattingEnabled() )
    {
        TRACE( INFO, "formatting not enabled - delegating to ASBeautifier." );
        return ASBeautifier::nextLine();
    }

    while ( ! isLineReady )
    {
        if ( shouldReparseCurrentChar )
        {
            TRACE( INFO, "reparsing character..." );
            shouldReparseCurrentChar = false;
        }
        else if ( ! getNextChar() )
        {
            TRACE( INFO, "no more characters - breaking line and delegating to ASBeautifier." );
            breakLine();
            return beautify(readyFormattedLine);
        }
        else // stuff to do when reading a new character...
        {
            // make sure that a virgin '{' at the begining of the file will be treated as a block...
            if ( isInVirginLine && currentChar == '{' )
            {
                TRACE( INFO, "virgin '{'" );
                previousCommandChar = '{';
            }
            isPreviousCharPostComment = isCharImmediatelyPostComment;
            isCharImmediatelyPostComment = false;
            isCharImmediatelyPostTemplate = false;
            isCharImmediatelyPostHeader = false;
        }

        // handle comments
        if ( isInLineComment )
        {
            appendCurrentChar();

            // explicitely break a line when a line comment's end is found.
            if ( /* bracketFormatMode == ATTACH_MODE && */ charNum + 1 == currentLine.size())
            {
                isInLineBreak = true;
                isInLineComment = false;
                isImmediatelyPostLineComment = true;
                currentChar = 0;  //make sure it is a neutral char.
            }
            continue;
        }
        else if ( isInComment )
        {
            if ( isSequenceReached( AS_CLOSE_COMMENT ) )
            {
                isInComment = false;
                isImmediatelyPostComment = true;
                appendSequence( AS_CLOSE_COMMENT );
                goForward( 1 );
            }
            else
            {
                appendCurrentChar();
            }
            continue;
        }

        // handle quotes
        if ( isInQuote )
        {
            if ( isSpecialChar )
            {
                isSpecialChar = false;
                appendCurrentChar();
            }
            else if ( currentChar == '\\' )
            {
                TRACE( INFO, "special (escaped) char entcountered" );
                isSpecialChar = true;
                appendCurrentChar();
            }
            else if ( quoteChar == currentChar )
            {
                TRACE( INFO, "end of quote encountered" );
                isInQuote = false;
                appendCurrentChar();
            }
            else
            {
                appendCurrentChar();
            }
            continue;
        }


        // handle white space or preprocessor statements (simplifies the rest)
        if ( isWhiteSpace( currentChar ) || isInPreprocessor )
        {
            // TODO: stale comment: if ( isLegalNameChar( previousChar ) && isLegalNameChar( peekNextChar() ) )
            appendCurrentChar();
            continue;
        }

        // detect BEGIN of comments or quotes
        if ( isSequenceReached( AS_OPEN_LINE_COMMENT ) )
        {
            TRACE( INFO, "beginning of line comment encountered" );
            isInLineComment = true;
            if ( padOperators )
            {
                appendSpacePad();
            }
            appendSequence( AS_OPEN_LINE_COMMENT );
            goForward( 1 );
            continue;
        }
        else if ( isSequenceReached( AS_OPEN_COMMENT ) )
        {
            TRACE( INFO, "beginning of multi-line comment encountered" );
            isInComment = true;
            if ( padOperators )
            {
                appendSpacePad();
            }
            appendSequence( AS_OPEN_COMMENT );
            goForward( 1 );
            continue;
        }
        else if ( currentChar == '"' || currentChar == '\'' )
        {
            TRACE( INFO, "beginning of quote encountered" );
            isInQuote = true;
            quoteChar = currentChar;
            // if (padOperators)     // BUGFIX: these two lines removed. seem to be unneeded, and interfere with L"
            //     appendSpacePad(); // BUGFIX: TODO: make sure the removal of these lines doesn't reopen old bugs...
            appendCurrentChar();
            continue;
        }

        // not in quote or comment or white-space of any type ...

        // check if in preprocessor
        // ** isInPreprocessor will be automatically reset at the begining of a new line in getNextChar()
        if ( currentChar == '#' )
        {
            TRACE( INFO, "beginning of preprocessor statement encountered" );
            isInPreprocessor = true;
        }
        // TODO: Should not be reached; candidate for removal
        if ( isInPreprocessor )
        {
            TRACE( INFO, "being inside preprocessor. IS THIS EVER ACTUALLY REACHED?" );
            appendCurrentChar();
            continue;
        }

        // not in preprocessor ...
        if ( isImmediatelyPostComment )
        {
            TRACE( INFO, "isImmediatelyPostComment" );
            isImmediatelyPostComment = false;
            isCharImmediatelyPostComment = true;
        }

        if ( isImmediatelyPostLineComment )
        {
            TRACE( INFO, "isImmediatelyPostLineComment" );
            isImmediatelyPostLineComment = false;
            isCharImmediatelyPostLineComment = true;
        }

        if ( shouldBreakLineAfterComments )
        {
            TRACE( INFO, "breaking line after comments" );
            shouldBreakLineAfterComments = false;
            shouldReparseCurrentChar = true;
            breakLine();
            continue;
        }

        if ( isImmediatelyPostHeader )
        {
            TRACE( INFO, "isImmediatelyPostHeader" );

            // reset post-header information
            isImmediatelyPostHeader = false;
            isCharImmediatelyPostHeader = true;

            // If configured, break headers from their succeeding blocks.
            // Make sure that else if()'s are excepted unless configured
            // to be broken too.
            if ( breakOneLineStatements && 
                 ( breakElseIfs || 
                 ( currentHeader != &AS_ELSE || findHeader( headers ) != &AS_IF ) ) )
            {
                TRACE( INFO, "breaking line after header" );
                isInLineBreak = true;
            }
        }

        if ( passedSemicolon )
        {
            TRACE( INFO, "passedSemicolon" );
            passedSemicolon = false;
            if ( parenStack->back() == 0 )
            {
                TRACE( INFO, "parenStack->back() == 0" );
                shouldReparseCurrentChar = true;
                isInLineBreak = true;
                continue;
            }
        }

        if ( passedColon )
        {
            TRACE( INFO, "passedColon" );
            passedColon = false;
            if ( parenStack->back() == 0 )
            {
                TRACE( INFO, "parenStack->back() == 0" );
                shouldReparseCurrentChar = true;
                isInLineBreak = true;
                continue;
            }
        }

        // Check if in template declaration, e.g. foo<bar> or foo<bar,fig>
        if ( ! isInTemplate && currentChar == '<' )
        {
            TRACE( ENTRY, "checking for template..." );
            int templateDepth = 0; // TODO: hides astyle::ASBeautifier::templateDepth
            const string *oper;
            for ( unsigned i = charNum; i < currentLine.size(); i += ( oper ? oper->length() : 1 ) )
            {
                oper = ASBeautifier::findHeader( currentLine, i, operators );

                if ( oper == &AS_LS )
                {
                    templateDepth++;
                }
                else if ( oper == &AS_GR )
                {
                    templateDepth--;
                    if ( templateDepth == 0 )
                    {
                        TRACE( EXIT, "template encountered!" );
                        isInTemplate = true;
                        break;
                    }
                }
                else if ( oper == &AS_COMMA            // comma,     e.g. A<int, char>
                       || oper == &AS_BIT_AND          // reference, e.g. A<int&>
                       || oper == &AS_MULT             // pointer,   e.g. A<int*>
                       || oper == &AS_COLON_COLON)     // ::,        e.g. std::string
                {
                    continue;
                }
                else if ( ! isLegalNameChar( currentLine[i] ) && ! isWhiteSpace( currentLine[i] ) )
                {
                    TRACE( EXIT, "false alarm - not a template" );
                    isInTemplate = false;
                    break;
                }
            }
        }

        // handle parenthesies
        if ( currentChar == '(' || currentChar == '[' || ( isInTemplate && currentChar == '<' ) )
        {
            TRACE( ENTRY, "opening paren '" << currentChar << "' encountered." );
            parenStack->back()++;
        }
        else if ( currentChar == ')' || currentChar == ']' || ( isInTemplate && currentChar == '>' ) )
        {
            TRACE( EXIT, "closing paren '" << currentChar << "' encountered." );
            parenStack->back()--;

            if ( isInTemplate && parenStack->back() == 0 )
            {
                TRACE( INFO, "(also marks end of template)" );
                isInTemplate = false;
                isCharImmediatelyPostTemplate = true;
            }

            // check if this parenthesis closes a header, e.g. if (...), while (...)
            if ( isInHeader && parenStack->back() == 0 )
            {
                TRACE( INFO, "(also marks end of header)" );
                isInHeader = false;
                isImmediatelyPostHeader = true;
            }

        }

        // handle brackets
        BracketType bracketType = NULL_TYPE;

        if ( currentChar == '{' )
        {
            TRACE( ENTRY, "opening bracket encountered" );
            bracketType = getBracketType();
            foundPreDefinitionHeader = false;
            foundPreCommandHeader = false;

            bracketTypeStack->push_back(bracketType);
            preBracketHeaderStack->push_back(currentHeader);
            currentHeader = NULL;

            isPreviousBracketBlockRelated = (bracketType != ARRAY_TYPE);
        }
        else if ( currentChar == '}' )
        {
            TRACE( EXIT, "closing bracket encountered" );

            // if a request has been made to append a post block empty line,
            // but the block exists immediately before a closing bracket,
            // then there is no need for the empty line.
            isAppendPostBlockEmptyLineRequested = false;

            if ( ! bracketTypeStack->empty() )
            {
                TRACE( INFO, "popping from bracketTypeStack..." );
                bracketType = bracketTypeStack->back();
                bracketTypeStack->pop_back();

                isPreviousBracketBlockRelated = ( bracketType != ARRAY_TYPE );
            }

            if ( ! preBracketHeaderStack->empty() )
            {
                TRACE( INFO, "popping from preBracketHeaderStack..." );
                currentHeader = preBracketHeaderStack->back();
                preBracketHeaderStack->pop_back();
            }
            else
            {
                TRACE( INFO, "currentHeader = NULL" );
                currentHeader = NULL;
            }
        }

        if ( bracketType != ARRAY_TYPE )
        {
            TRACE( INFO, "bracket is not of ARRAY_TYPE" );

            if ( currentChar == '{' )
            {
                TRACE( INFO, "pushing zero to parenStack" );
                parenStack->push_back(0);
            }
            else if ( currentChar == '}' && ! parenStack->empty() )
            {
                TRACE( INFO, "popping from parenStack" );
                parenStack->pop_back();
            }

            if ( bracketFormatMode != NONE_MODE )
            {
                TRACE( INFO, "bracketFormatMode != NONE_MODE" );
                
                // TODO: Haven't looked at this yet.
                if ( currentChar == '{' )
                {
                    if ( ( bracketFormatMode == ATTACH_MODE
                            || bracketFormatMode == BDAC_MODE && bracketTypeStack->size() >= 2
                            && ( (*bracketTypeStack)[ bracketTypeStack->size() - 2 ] == COMMAND_TYPE ) /*&& isInLineBreak*/)
                            && ! isCharImmediatelyPostLineComment )
                    {
                        appendSpacePad();
                        if ( ! isCharImmediatelyPostComment   // do not attach '{' to lines that end with /**/ comments.
                               && previousCommandChar != '{'
                               && previousCommandChar != '}'
                               && previousCommandChar != ';') // '}' , ';' chars added for proper handling of '{' immediately after a '}' or ';'
                        {
                            appendCurrentChar(false);
                        }
                        else
                        {
                            appendCurrentChar(true);
                        }
                        continue;
                    }
                    else if ( bracketFormatMode == BREAK_MODE
                               || bracketFormatMode == BDAC_MODE && bracketTypeStack->size() >= 2
                               && ( (*bracketTypeStack)[ bracketTypeStack->size() - 2 ] == DEFINITION_TYPE))
                    {
                        if ( breakOneLineBlocks || (bracketType != SINGLE_LINE_TYPE) )
                        {
                            breakLine();
                        }
                        appendCurrentChar();
                        continue;
                    }
                }
                else if ( currentChar == '}' )
                {
                    // bool origLineBreak = isInLineBreak;

                    // mark state of immediately after empty block
                    // this state will be used for locating brackets that appear immedately AFTER an empty block (e.g. '{} \n}').
                    if ( previousCommandChar == '{' )
                    {
                        isImmediatelyPostEmptyBlock = true;
                    }

                    if ( ( ! ( previousCommandChar == '{' && isPreviousBracketBlockRelated ) ) // this '{' does not close an empty block
                          && ( breakOneLineBlocks || ( bracketType != SINGLE_LINE_TYPE ) )     // astyle is allowed to break on line blocks
                          && ! isImmediatelyPostEmptyBlock)                                    // this '}' does not immediately follow an empty block
                    {
                        breakLine();
                        appendCurrentChar();
                    }
                    else
                    {
                        if ( ! isCharImmediatelyPostComment )
                        {
                            isInLineBreak = false;
                        }
                        appendCurrentChar();
                        if ( breakOneLineBlocks || ( bracketType != SINGLE_LINE_TYPE ) )
                        {
                            shouldBreakLineAfterComments = true;
                        }
                    }

                    if ( breakBlocks )
                    {
                        isAppendPostBlockEmptyLineRequested =true;
                    }

                    continue;
                }
            }
        } // bracketType != ARRAY_TYPE

        // TODO: What's this? An attempt at the longest conditional in the world?
        if ( ( ( previousCommandChar == '{' && isPreviousBracketBlockRelated)
            || ( previousCommandChar == '}' && ! isImmediatelyPostEmptyBlock   // <--
                                            && isPreviousBracketBlockRelated
                                            && ! isPreviousCharPostComment    // <-- Fixes wrongly appended newlines after '}' immediately after comments... 10/9/1999
                                            && peekNextChar() != ' ' ) )
            && ( breakOneLineBlocks || ( bracketTypeStack->back() != SINGLE_LINE_TYPE ) ) )
        {
            isCharImmediatelyPostOpenBlock = (previousCommandChar == '{');
            isCharImmediatelyPostCloseBlock = (previousCommandChar == '}');

            previousCommandChar = ' ';
            isInLineBreak = true;  // <----
        }

        // reset block handling flag
        isImmediatelyPostEmptyBlock = false;

        // look for headers
        if ( ! isInTemplate )
        {
            if ( (newHeader = findHeader(headers)) != NULL)
            {
                foundClosingHeader = false;
                const string *previousHeader;

                // recognize closing headers of do..while, if..else, try..catch..finally
                if ( (newHeader == &AS_ELSE && currentHeader == &AS_IF)
                        || (newHeader == &AS_WHILE && currentHeader == &AS_DO)
                        || (newHeader == &AS_CATCH && currentHeader == &AS_TRY)
                        || (newHeader == &AS_CATCH && currentHeader == &AS_CATCH)
                        || (newHeader == &AS_FINALLY && currentHeader == &AS_TRY)
                        || (newHeader == &AS_FINALLY && currentHeader == &AS_CATCH) )
                    foundClosingHeader = true;

                previousHeader = currentHeader;
                currentHeader = newHeader;

                // If in ATTACH or LINUX bracket modes, attach closing headers (e.g. 'else', 'catch')
                // to their preceding bracket,
                // But do not perform the attachment if the breakClosingHeaderBrackets is set!
                if (!breakClosingHeaderBrackets && foundClosingHeader && (bracketFormatMode == ATTACH_MODE || bracketFormatMode == BDAC_MODE) && previousNonWSChar == '}')
                {
                    isInLineBreak = false;
                    appendSpacePad();

                    if (breakBlocks)
                        isAppendPostBlockEmptyLineRequested = false;
                }

                //Check if a template definition as been reached, e.g. template<class A>
                if (newHeader == &AS_TEMPLATE)
                {
                    isInTemplate = true;
                }

                // check if the found header is non-paren header
                isNonParenHeader = ( find(nonParenHeaders.begin(), nonParenHeaders.end(),
                                          newHeader) != nonParenHeaders.end() );
                // added C# support
                if ( ( sourceStyle != STYLE_CSHARP ) && ( newHeader == &AS_UNSAFE
                    || newHeader == &AS_GET || newHeader == &AS_SET
                    || newHeader == &AS_ADD || newHeader == &AS_REMOVE ) )
                    isNonParenHeader = false;
                appendSequence(*currentHeader);
                goForward(currentHeader->length() - 1);
                // if padding is on, and a paren-header is found
                // then add a space pad after it.
                if (padOperators && !isNonParenHeader)
                    appendSpacePad();


                // Signal that a header has been reached
                // *** But treat a closing while() (as in do...while)
                //     as if it where NOT a header since a closing while()
                //     should never have a block after it!
                if (!(foundClosingHeader && currentHeader == &AS_WHILE))
                {
                    isInHeader = true;
                    if (isNonParenHeader)
                    {
                        isImmediatelyPostHeader = true;
                        isInHeader = false;
                    }
                }

                if (currentHeader == &AS_IF && previousHeader == &AS_ELSE)
                    isInLineBreak = false;

                if (breakBlocks)
                {
                    if (previousHeader == NULL
                            && !foundClosingHeader
                            && !isCharImmediatelyPostOpenBlock)
                    {
                        isPrependPostBlockEmptyLineRequested = true;
                    }

                    if (currentHeader == &AS_ELSE
                            || currentHeader == &AS_CATCH
                            || currentHeader == &AS_FINALLY
                            || foundClosingHeader)
                    {
                        isPrependPostBlockEmptyLineRequested = false;
                    }

                    if (breakClosingHeaderBlocks
                            &&  isCharImmediatelyPostCloseBlock)
                    {
                        isPrependPostBlockEmptyLineRequested = true;
                    }

                }

                continue;
            }
            else if ( (newHeader = findHeader(preDefinitionHeaders)) != NULL)
            {
                foundPreDefinitionHeader = true;
                appendSequence(*newHeader);
                goForward(newHeader->length() - 1);

                if (breakBlocks)
                    isPrependPostBlockEmptyLineRequested = true;

                continue;
            }
            else if ( (newHeader = findHeader(preCommandHeaders)) != NULL)
            {
                foundPreCommandHeader = true;
                appendSequence(*newHeader);
                goForward(newHeader->length() - 1);

                continue;
            }
        }

        if (previousNonWSChar == '}' || currentChar == ';')
        {
            if (breakOneLineStatements && currentChar == ';'
                    && (breakOneLineBlocks || (bracketTypeStack->back() != SINGLE_LINE_TYPE)))
            {
                passedSemicolon = true;
            }

            if (breakBlocks && currentHeader != NULL && parenStack->back() == 0)
            {
                isAppendPostBlockEmptyLineRequested = true;
            }

            if (currentChar != ';')
                currentHeader = NULL; //DEVEL: is this ok?

            foundQuestionMark = false;
            foundPreDefinitionHeader = false;
            foundPreCommandHeader = false;
            isInPotentialCalculation = false;

        }

        if (currentChar == ':'
                && breakOneLineStatements
                && !foundQuestionMark // not in a ... ? ... : ... sequence
                && !foundPreDefinitionHeader // not in a definition block (e.g. class foo : public bar
                && previousCommandChar != ')' // not immediately after closing paren of a method header, e.g. ASFormatter::ASFormatter(...) : ASBeautifier(...)
                && previousChar != ':' // not part of '::'
                && peekNextChar() != ':') // not part of '::'
        {
            passedColon = true;
            if (breakBlocks)
                isPrependPostBlockEmptyLineRequested = true;
        }

        if (currentChar == '?')
            foundQuestionMark = true;

        if (padOperators)
        {
            if ((newHeader = findHeader(operators)) != NULL)
            {
                bool shouldPad = (newHeader != &AS_COLON_COLON
                                  && newHeader != &AS_PAREN_PAREN
                                  && newHeader != &AS_BLPAREN_BLPAREN
                                  && newHeader != &AS_PLUS_PLUS
                                  && newHeader != &AS_MINUS_MINUS
                                  && newHeader != &AS_NOT
                                  && newHeader != &AS_BIT_NOT
                                  && newHeader != &AS_ARROW
                                  && newHeader != &AS_OPERATOR
                                  && !(newHeader == &AS_MINUS && isInExponent())
                                  && !(newHeader == &AS_PLUS && isInExponent())
                                  && previousOperator != &AS_OPERATOR
                                  && !((newHeader == &AS_MULT || newHeader == &AS_BIT_AND)
                                       && isPointerOrReference())
                                  && !( (isInTemplate || isCharImmediatelyPostTemplate)
                                        && (newHeader == &AS_LS || newHeader == &AS_GR))
                                 );

                if (!isInPotentialCalculation)
                    if (find(assignmentOperators.begin(), assignmentOperators.end(), newHeader)
                            != assignmentOperators.end())
                        isInPotentialCalculation = true;

                // pad before operator
                if (shouldPad
                        && !(newHeader == &AS_COLON && !foundQuestionMark)
                        && newHeader != &AS_SEMICOLON
                        && newHeader != &AS_COMMA)
                    appendSpacePad();
                appendSequence(*newHeader);
                goForward(newHeader->length() - 1);

                // since this block handles '()' and '[]',
                // the parenStack must be updated here accordingly!
                if (newHeader == &AS_PAREN_PAREN
                        || newHeader == &AS_BLPAREN_BLPAREN)
                    parenStack->back()--;

                currentChar = (*newHeader)[newHeader->length() - 1];
                // pad after operator
                // but do not pad after a '-' that is a unary-minus.
                if ( shouldPad && !(newHeader == &AS_MINUS && isUnaryMinus()) )
                    appendSpacePad();

                previousOperator = newHeader;
                continue;
            }
        }
        if (padParen)
        {
            if (currentChar == '(' || currentChar == '[' )
            {
                char peekedChar = peekNextChar();

                isInPotentialCalculation = true;
                appendCurrentChar();
                if (!(currentChar == '(' && peekedChar == ')')
                        && !(currentChar == '[' && peekedChar == ']'))
                    appendSpacePad();
                continue;
            }
            else if (currentChar == ')' || currentChar == ']')
            {
                char peekedChar = peekNextChar();

                if (!(previousChar == '(' && currentChar == ')')
                        && !(previousChar == '[' && currentChar == ']'))
                    appendSpacePad();

                appendCurrentChar();

                if (peekedChar != ';' && peekedChar != ',' && peekedChar != '.'
                        && !(currentChar == ']' && peekedChar == '['))
                    appendSpacePad();
                continue;
            }
        }

        appendCurrentChar();
    }

    // return a beautified (i.e. correctly indented) line.

    string beautifiedLine;
    int readyFormattedLineLength = trim(readyFormattedLine).size();

    if (prependEmptyLine
            && readyFormattedLineLength > 0
            && previousReadyFormattedLineLength > 0)
    {
        TRACE( INFO, "delegation point 2" );
        isLineReady = true; // signal that a readyFormattedLine is still waiting
        beautifiedLine = beautify("");
    }
    else
    {
        TRACE( INFO, "delegation point 3" );
        isLineReady = false;
        beautifiedLine = beautify(readyFormattedLine);
    }

    prependEmptyLine = false;
    previousReadyFormattedLineLength = readyFormattedLineLength;

    return beautifiedLine;

}

/**
* check if there are any indented lines ready to be read by nextLine()
*
* @return    are there any indented lines ready?
*/
bool ASFormatter::hasMoreLines() const
{
    if (!isFormattingEnabled())
        return ASBeautifier::hasMoreLines();
    else
        return !endOfCodeReached;
}

/**
 * check if formatting options are enabled, in addition to indentation.
 *
 * @return     are formatting options enabled?
 */
bool ASFormatter::isFormattingEnabled() const
{
    return (bracketFormatMode != NONE_MODE
            || padOperators
            || convertTabs2Space);
}

/**
 * check if a specific sequence exists in the current placement of the current line
 *
 * @return             whether sequence has been reached.
 * @param sequence     the sequence to be checked
 */
bool ASFormatter::isSequenceReached(const string &sequence) const
{
    return CONTAINS_AT(currentLine, sequence, sequence.size(), charNum);
}

/**
 * jump over several characters.
 *
 * @param i       the number of characters to jump over.
 */
void ASFormatter::goForward(int i)
{
    while (--i >= 0)
        getNextChar();
}

/**
* peek at the next unread character.
*
* @return     the next unread character.
*/
char ASFormatter::peekNextChar() const
{
    int peekNum = charNum + 1;
    int len = currentLine.size();
    char ch = ' ';

    while (peekNum < len)
    {
        ch = currentLine[peekNum++];
        if (!isWhiteSpace(ch))
            return ch;
    }

    if (convertTabs2Space && ch == '\t')
        ch = ' ';

    return ch;
}

/**
* check if current placement is before a comment or line-comment
*
* @return     is before a comment or line-comment.
*/
bool ASFormatter::isBeforeComment() const
{
    int peekNum = charNum + 1;
    int len = currentLine.size();
    // char ch = ' ';
    bool foundComment = false;

    for (peekNum = charNum + 1;
            peekNum < len && isWhiteSpace(currentLine[peekNum]);
            ++peekNum)
        ;

    if (peekNum < len)
        foundComment = ( CONTAINS_AT(currentLine, AS_OPEN_COMMENT, 2, peekNum)
                         || CONTAINS_AT(currentLine, AS_OPEN_LINE_COMMENT, 2, peekNum) );

    return foundComment;
}

/**
* get the next character, increasing the current placement in the process.
* the new character is inserted into the variable currentChar.
*
* @return   whether succeded to recieve the new character.
*/
bool ASFormatter::getNextChar()
{
    isInLineBreak = false;
    bool isAfterFormattedWhiteSpace = false;

    if (padOperators && !isInComment && !isInLineComment
            && !isInQuote && !doesLineStartComment && !isInPreprocessor
            && !isBeforeComment())
    {
        int len = formattedLine.size();
        if (len > 0 && isWhiteSpace(formattedLine[len-1]))
            isAfterFormattedWhiteSpace = true;
    }

    previousChar = currentChar;
    if (!isWhiteSpace(currentChar))
    {
        previousNonWSChar = currentChar;
        if (!isInComment && !isInLineComment && !isInQuote
                && !isSequenceReached(AS_OPEN_COMMENT)
                && !isSequenceReached(AS_OPEN_LINE_COMMENT) )
            previousCommandChar = previousNonWSChar;
    }

    unsigned currentLineLength = currentLine.size();

    if (charNum+1 < currentLineLength
            && (!isWhiteSpace(peekNextChar()) || isInComment || isInLineComment))
    {
        currentChar = currentLine[++charNum];
        if (isAfterFormattedWhiteSpace)
            while (isWhiteSpace(currentChar) && charNum+1 < currentLineLength)
                currentChar = currentLine[++charNum];

        if (convertTabs2Space && currentChar == '\t')
            currentChar = ' ';

        return true;
    }
    else
    {
        if (*sourceIterator)
        {
            getline(*sourceIterator, currentLine);
            if ( !currentLine.empty() && currentLine[currentLine.size() - 1] == '\r' )
            {
                currentLine = currentLine.substr(0, currentLine.size() - 1);
            }
            if (currentLine.empty())
            {
                currentLine = string(" "); // think
            }
            // unless reading in the first line of the file,
            // break a new line.
            if (!isVirgin)
                isInLineBreak = true;
            else
                isVirgin = false;

            if (isInLineComment)
                isImmediatelyPostLineComment = true;
            isInLineComment = false;

            trimNewLine();
            currentChar = currentLine[charNum];

            // check if is in preprocessor right after the line break and line trimming
            if (previousNonWSChar != '\\')
                isInPreprocessor = false;
            else
                TRACE( INFO, "previousNonWSChar == '\\'" );

            if (convertTabs2Space && currentChar == '\t')
                currentChar = ' ';

            return true;
        }
        else
        {
            endOfCodeReached = true;
            return false;
        }
    }
}

/**
* jump over the leading white space in the current line,
* IF the line does not begin a comment or is in a preprocessor definition.
*/
void ASFormatter::trimNewLine()
{
    unsigned len = currentLine.size();
    charNum = 0;

    if (isInComment || isInPreprocessor)
        return;

    while (isWhiteSpace(currentLine[charNum]) && charNum+1 < len)
        ++charNum;

    doesLineStartComment = false;
    if (isSequenceReached(string("/*")))
    {
        charNum = 0;
        doesLineStartComment = true;
    }
}

/**
 * append the CURRENT character (curentChar)to the current
 * formatted line. Unless disabled (via canBreakLine == false),
 * first check if a line-break has been registered, and if so
 * break the formatted line, and only then append the character
 * into the next formatted line.
 *
 * @param canBreakLine     if true, a registered line-break
 */
void ASFormatter::appendCurrentChar(bool canBreakLine)
{
    // TODO: This is probably where win / mac / linux line breaks can be enforced
    if (canBreakLine && isInLineBreak)
        breakLine();
    formattedLine.append(1, currentChar);
}

/**
 * append a string sequence to the current formatted line.
 * Unless disabled (via canBreakLine == false), first check if a
 * line-break has been registered, and if so break the
 * formatted line, and only then append the sequence into
 * the next formatted line.
 *
 * @param sequence         the sequence to append.
 * @param canBreakLine     if true, a registered line-break
 */
void ASFormatter::appendSequence(const string &sequence, bool canBreakLine)
{
    if (canBreakLine && isInLineBreak)
        breakLine();
    formattedLine.append(sequence);
}

/**
 * append a space to the current formattedline, UNLESS the
 * last character is already a white-space character.
 */
void ASFormatter::appendSpacePad()
{
    int len = formattedLine.size();
    if (len == 0 || !isWhiteSpace(formattedLine[len-1]))
        formattedLine.append(1, ' ');
}

/**
 * register a line break for the formatted line.
 */
void ASFormatter::breakLine()
{
    isLineReady = true;
    isInLineBreak = false;

    // queue an empty line prepend request if one exists
    prependEmptyLine = isPrependPostBlockEmptyLineRequested;

    readyFormattedLine =  formattedLine;
    if (isAppendPostBlockEmptyLineRequested)
    {
        isAppendPostBlockEmptyLineRequested = false;
        isPrependPostBlockEmptyLineRequested = true;
    }
    else
    {
        isPrependPostBlockEmptyLineRequested = false;
    }

    formattedLine = "";
}

/**
 * check if the currently reached open-bracket (i.e. '{')
 * opens a:
 * - a definition type block (such as a class or namespace),
 * - a command block (such as a method block)
 * - a static array
 * this method takes for granted that the current character
 * is an opening bracket.
 *
 * @return    the type of the opened block.
 */
BracketType ASFormatter::getBracketType() const
{
    BracketType returnVal;

    if (foundPreDefinitionHeader)
        returnVal = DEFINITION_TYPE;
    else
    {
        bool isCommandType;
        isCommandType = ( foundPreCommandHeader
                          || ( currentHeader != NULL && isNonParenHeader )
                          || ( previousCommandChar == ')' )
                          || ( previousCommandChar == ':' && !foundQuestionMark )
                          || ( previousCommandChar == ';' )
                          || ( ( previousCommandChar == '{' ||  previousCommandChar == '}')
                               && isPreviousBracketBlockRelated ) );

        returnVal = (isCommandType ? COMMAND_TYPE : ARRAY_TYPE);
    }

    if (isOneLineBlockReached())
        returnVal = (BracketType) (returnVal | SINGLE_LINE_TYPE);

    return returnVal;
}

/**
 * check if the currently reached  '*' or '&' character is
 * a pointer-or-reference symbol, or another operator.
 * this method takes for granted that the current character
 * is either a '*' or '&'.
 *
 * @return        whether current character is a reference-or-pointer
 */
bool ASFormatter::isPointerOrReference() const
{
    bool isPR;
    isPR = ( !isInPotentialCalculation
             || (bracketTypeStack->back() == DEFINITION_TYPE)
             || (!isLegalNameChar(previousNonWSChar)
                 && previousNonWSChar != ')'
                 && previousNonWSChar != ']')
           );

    if (!isPR)
    {
        char nextChar = peekNextChar();
        isPR |= (!isWhiteSpace(nextChar)
                 && nextChar != '-'
                 && nextChar != '('
                 && nextChar != '['
                 && !isLegalNameChar(nextChar));
    }

    return isPR;
}


/**
 * check if the currently reached '-' character is
 * a unary minus
 * this method takes for granted that the current character
 * is a '-'.
 *
 * @return        whether the current '-' is a unary minus.
 */
bool ASFormatter::isUnaryMinus() const
{
    return ( (previousOperator == &AS_RETURN || !isalnum(previousCommandChar))
             && previousCommandChar != '.'
             && previousCommandChar != ')'
             && previousCommandChar != ']' );
}


/**
 * check if the currently reached '-' or '+' character is
 * part of an exponent, i.e. 0.2E-5.
 * this method takes for granted that the current character
 * is a '-' or '+'.
 *
 * @return        whether the current '-' is in an exponent.
 */
bool ASFormatter::isInExponent() const
{
    int formattedLineLength = formattedLine.size();
    if (formattedLineLength >= 2)
    {
        char prevPrevFormattedChar = formattedLine[formattedLineLength - 2];
        char prevFormattedChar = formattedLine[formattedLineLength - 1];

        return ( (prevFormattedChar == 'e' || prevFormattedChar == 'E')
                 && (prevPrevFormattedChar == '.' || isdigit(prevPrevFormattedChar)) );
    }
    else
        return false;
}

/**
 * check if a one-line bracket has been reached,
 * i.e. if the currently reached '{' character is closed
 * with a complimentry '}' elsewhere on the current line,
 *.
 * @return        has a one-line bracket been reached?
 */
bool ASFormatter::isOneLineBlockReached() const
{
    bool isInComment = false; // hides astyle::ASFormatter::isInComment
    bool isInQuote = false;   // hides astyle::ASFormatter::isInQuote
    int bracketCount = 1;
    unsigned currentLineLength = currentLine.size();
    unsigned i = 0;
    char ch = ' ';
    char quoteChar = ' ';     // hides astyle::ASFormatter::quoteChar

    for (i = charNum + 1; i < currentLineLength; ++i)
    {
        ch = currentLine[i];

        if (isInComment)
        {
            if (CONTAINS_AT(currentLine, AS_CLOSE_COMMENT, 2, i))
            {
                isInComment = false;
                ++i;
            }
            continue;
        }

        if (ch == '\\')
        {
            TRACE( INFO, "ch == '\\'" );
            ++i;
            continue;
        }

        if (isInQuote)
        {
            if (ch == quoteChar)
                isInQuote = false;
            continue;
        }

        if (ch == '"' || ch == '\'')
        {
            isInQuote = true;
            quoteChar = ch;
            continue;
        }

        if (CONTAINS_AT(currentLine, AS_OPEN_LINE_COMMENT, 2, i))
            break;

        if (CONTAINS_AT(currentLine, AS_OPEN_LINE_COMMENT, 2, i))
        {
            isInComment = true;
            ++i;
            continue;
        }

        if (ch == '{')
            ++bracketCount;
        else if (ch == '}')
            --bracketCount;

        if(bracketCount == 0)
            return true;
    }

    return false;
}


/**
 * check if one of a set of headers has been reached in the
 * current position of the current line.
 *
 * @return             a pointer to the found header. Or a NULL if no header has been reached.
 * @param headers      a vector of headers
 * @param checkBoundry
 */
const string *ASFormatter::findHeader(const vector<const string*> &headers, bool checkBoundry)
{
    return ASBeautifier::findHeader(currentLine, charNum, headers, checkBoundry);
}

} // namespace astyle
