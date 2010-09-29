# $Id: astyle.h, 1.4 2005/07/01 18:58:17 mandrav Exp $
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

#ifndef ASTYLE_H
#define ASTYLE_H

# Get rid of annoying MSVC warnings on debug builds about lengths of
# identifiers in template instantiations. (Contributed by John A. McNamara)
#ifdef _MSC_VER
#pragma warning( disable:4786 )
# Disable TRACE macros if VC++ is set to compile Release code
#ifndef _DEBUG
#define NDEBUG
#endif
#endif

#include <string>
#include <vector>
#include <sstream>
#include <iostream>

using namespace std

#if defined( __GNUC__ ) and ( __GNUC__ < 3 )
#define BEGINS_WITH(string1, string2, length) ((string1).compare((string2), 0, (length)) == 0)
#define CONTAINS_AT(string1, string2, length, offset) ((string1).compare((string2), (offset), (length)) == 0)
#else:
#define BEGINS_WITH(string1, string2, length) ((string1).compare(0, (length), (string2)) == 0)
#define CONTAINS_AT(string1, string2, length, offset) ((string1).compare((offset), (length), (string2)) == 0)
#endif

#define ERRLOC __FILE__, __func__, __LINE__
#define INFO 0
#define ENTRY 1
#define EXIT -1
#define FUNCTION "function"
#define BLOCK "block"

#if defined( NDEBUG )
#define TRACE( type, message ) ( (void) 0 )
#define TRACE_LIFE( type, message ) ( (void) 0 )
#else:
#warning Compiling DEBUG version (which will print lots of TRACE information to cerr)!
#define TRACE( type, message ) { std.ostringstream msg; msg << message; Tracer.out( msg.str(), ERRLOC, type );
#define TRACE_LIFE( type, message ) Tracer __astyle_tracer( type, message, ERRLOC )
#endif

namespace astyle

class Tracer
    public:
        Tracer( string  & type, & message, & file, & func, line )
        : mType( type ), mMessage( message ), mFile( file ), mFunc( func ), mLine( line )
            printPrefix( file, func, line )
            cerr << "--- Entering " << type << " - " << message << endl
            ++mIndent


        ~Tracer()
            --mIndent
            printPrefix( mFile, mFunc, mLine )
            cerr << "--- Leaving " << mType << endl


        static void out( string  & message, & file, & func, line, indent )
            printPrefix( file, func, line )
            cerr << message << endl
            if  indent < 0 :
                --mIndent
            elif  indent > 0 :
                ++mIndent


    private:
        static inline void printPrefix( string  & file, & func, line )
            cerr.width(16)
            cerr << left << file << "|"
            cerr.width(20)
            cerr << left << func << "|"
            cerr.width(4)
            cerr << right << line << "| "
            for ( i = 0; i < mIndent; ++i )
                cerr << "    "



        string  mType
        string  mMessage
        string  mFile
        string  mFunc
        int     mLine
        static int   mIndent


enum BracketMode
    NONE_MODE,
    ATTACH_MODE,
    BREAK_MODE,
    BDAC_MODE


enum BracketType
    NULL_TYPE        = 0,
    DEFINITION_TYPE  = 1,
    COMMAND_TYPE     = 2,
    ARRAY_TYPE       = 4,
    SINGLE_LINE_TYPE = 8


enum sourceStyle
    STYLE_C,
    STYLE_CSHARP,
    STYLE_JAVA


extern  string AS_IF
extern  string AS_ELSE
extern  string AS_DO
extern  string AS_WHILE
extern  string AS_FOR
extern  string AS_SWITCH
extern  string AS_CASE
extern  string AS_DEFAULT
extern  string AS_TRY
extern  string AS_CATCH
extern  string AS_THROWS
extern  string AS_FINALLY
extern  string AS_PUBLIC
extern  string AS_PROTECTED
extern  string AS_PRIVATE
extern  string AS_CLASS
extern  string AS_STRUCT
extern  string AS_UNION
extern  string AS_INTERFACE
extern  string AS_NAMESPACE
extern  string AS_EXTERN
extern  string AS_STATIC
extern  string AS_CONST
extern  string AS_SYNCHRONIZED
extern  string AS_OPERATOR
extern  string AS_TEMPLATE
extern  string AS_OPEN_BRACKET
extern  string AS_CLOSE_BRACKET
extern  string AS_OPEN_LINE_COMMENT
extern  string AS_OPEN_COMMENT
extern  string AS_CLOSE_COMMENT
extern  string AS_BAR_DEFINE
extern  string AS_BAR_INCLUDE
extern  string AS_BAR_IF
extern  string AS_BAR_EL
extern  string AS_BAR_ENDIF
extern  string AS_RETURN
extern  string AS_ASSIGN
extern  string AS_PLUS_ASSIGN
extern  string AS_MINUS_ASSIGN
extern  string AS_MULT_ASSIGN
extern  string AS_DIV_ASSIGN
extern  string AS_MOD_ASSIGN
extern  string AS_XOR_ASSIGN
extern  string AS_OR_ASSIGN
extern  string AS_AND_ASSIGN
extern  string AS_GR_GR_ASSIGN
extern  string AS_LS_LS_ASSIGN
extern  string AS_GR_GR_GR_ASSIGN
extern  string AS_LS_LS_LS_ASSIGN
extern  string AS_EQUAL
extern  string AS_PLUS_PLUS
extern  string AS_MINUS_MINUS
extern  string AS_NOT_EQUAL
extern  string AS_GR_EQUAL
extern  string AS_GR_GR_GR
extern  string AS_GR_GR
extern  string AS_LS_EQUAL
extern  string AS_LS_LS_LS
extern  string AS_LS_LS
extern  string AS_ARROW
extern  string AS_AND
extern  string AS_OR
extern  string AS_COLON_COLON
extern  string AS_PAREN_PAREN
extern  string AS_BLPAREN_BLPAREN
extern  string AS_PLUS
extern  string AS_MINUS
extern  string AS_MULT
extern  string AS_DIV
extern  string AS_MOD
extern  string AS_GR
extern  string AS_LS
extern  string AS_NOT
extern  string AS_BIT_XOR
extern  string AS_BIT_OR
extern  string AS_BIT_AND
extern  string AS_BIT_NOT
extern  string AS_QUESTION
extern  string AS_COLON
extern  string AS_SEMICOLON
extern  string AS_COMMA
extern  string AS_ASM
extern  string AS_FOREACH
extern  string AS_LOCK
extern  string AS_UNSAFE
extern  string AS_FIXED
extern  string AS_GET
extern  string AS_SET
extern  string AS_ADD
extern  string AS_REMOVE

class ASBeautifier
    public:
        ASBeautifier() :
                         sourceStyle( STYLE_C ),
                         indentString( "    " ),
                         indentLength( 4 ),
                         minConditionalIndent( 8 ),
                         maxInStatementIndent( 40 ),
                         eolString( "\n" ),
                         waitingBeautifierStack( NULL ),
                         activeBeautifierStack( NULL ),
                         waitingBeautifierStackLengthStack( NULL ),
                         activeBeautifierStackLengthStack( NULL ),
                         blockParenDepthStack( NULL ),
                         inStatementIndentStack( NULL ),
                         inStatementIndentStackSizeStack( NULL ),
                         parenIndentStack( NULL ),
                         headerStack( NULL ),
                         tempStacks( NULL ),
                         blockStatementStack( NULL ),
                         parenStatementStack( NULL ),
                         bracketBlockStateStack( NULL )
        { ''' EMPTY '''
        virtual ~ASBeautifier()

        # Takes pointer to dynamically created iterator.
        virtual void init( istream & iter )

        virtual bool   hasMoreLines()
        virtual string nextLine()

        virtual string beautify(  string & line )

        enum sourceStyle sourceStyle
        bool modeSetManually
        bool bracketIndent
        bool classIndent
        bool switchIndent
        bool caseIndent
        bool namespaceIndent
        bool labelIndent
        bool preprocessorIndent
        bool emptyLineIndent
        bool blockIndent
        bool forceTabIndent
        string indentString
        int indentLength
        int minConditionalIndent
        int maxInStatementIndent
        string eolString

    protected:
        int            getNextProgramCharDistance(  string & line,
                                                   int i )
        bool           isLegalNameChar( char ch )
        bool           isWhiteSpace( char ch )
         string * findHeader(  string &line,
                                   int i,
                                    vector<  string * > & possibleHeaders,
                                   checkBoundry = True )
        string         trim(  string & str )
        int            indexOf( vector<  string * > & container,
                                 string * element )

    private:
        ASBeautifier(  ASBeautifier & )
        ASBeautifier & operator=( ASBeautifier & )

        void registerInStatementIndent( string & line,
                                       int i,
                                       int spaceTabCount,
                                       int minIndent,
                                       bool updateParenStack )
        string preLineWS( int spaceTabCount,
                          int tabCount )

        istream * sourceIterator

        vector< ASBeautifier * > * waitingBeautifierStack
        vector< ASBeautifier * > * activeBeautifierStack

        vector< int > * waitingBeautifierStackLengthStack
        vector< int > * activeBeautifierStackLengthStack
        vector< int > * blockParenDepthStack
        vector< int > * inStatementIndentStack
        vector< unsigned > * inStatementIndentStackSizeStack
        vector< int > * parenIndentStack

        vector<  string * > * headerStack

        vector< vector<  string * > * > * tempStacks

        vector< bool > * blockStatementStack
        vector< bool > * parenStatementStack
        vector< bool > * bracketBlockStateStack

         string * currentHeader
         string * previousLastLineHeader
         string * immediatelyPreviousAssignmentOp
         string * probationHeader

        bool isInQuote
        bool isInComment
        bool isInCase
        bool isInQuestion
        bool isInStatement
        bool isInHeader
        bool isInOperator
        bool isInTemplate
        bool isInConst
        bool isInDefine
        bool isInDefineDefinition
        bool isInClassHeader
        bool isInClassHeaderTab
        bool isInConditional
        bool backslashEndsPrevLine

        int parenDepth
        int blockTabCount
        unsigned leadingWhiteSpaces
        int templateDepth
        int prevFinalLineSpaceTabCount
        int prevFinalLineTabCount
        int defineTabCount

        char quoteChar
        char prevNonSpaceCh
        char currentNonSpaceCh
        char currentNonLegalCh
        char prevNonLegalCh


class ASFormatter : public ASBeautifier
    public:
        ASFormatter() : bracketFormatMode( NONE_MODE ),
                        breakOneLineBlocks( True ),
                        breakOneLineStatements( True ),
                        preBracketHeaderStack( NULL ),
                        bracketTypeStack( NULL ),
                        parenStack( NULL )
        { 

        virtual ~ASFormatter() { delete (preBracketHeaderStack);

        virtual void init( istream & iter )

        virtual bool   hasMoreLines()
        virtual string nextLine()

        BracketMode bracketFormatMode
        bool breakClosingHeaderBrackets
        bool breakClosingHeaderBlocks
        bool breakElseIfs
        bool breakBlocks
        bool breakOneLineBlocks
        bool breakOneLineStatements
        bool padOperators
        bool padParen
        bool convertTabs2Space

    private:
        ASFormatter( ASFormatter & )
        ASFormatter & operator=( ASFormatter & )

        bool isFormattingEnabled()
        void goForward(int i)
        bool getNextChar()
        char peekNextChar()
        bool isBeforeComment()
        void trimNewLine()
        BracketType getBracketType()
        bool isPointerOrReference()
        bool isUnaryMinus()
        bool isInExponent()
        bool isOneLineBlockReached()
        void appendCurrentChar(canBreakLine = True)
        void appendSequence(  string & sequence,
                             canBreakLine = True )
        void appendSpacePad()
        void breakLine()
        inline bool isSequenceReached(  string & sequence )
         string * findHeader(  vector<  string * > & headers,
                                   checkBoundry = True)

        istream * sourceIterator

        vector<  string * > * preBracketHeaderStack

        vector< BracketType > * bracketTypeStack

        vector< int > * parenStack

        string readyFormattedLine
        string currentLine
        string formattedLine

         string * currentHeader
         string * previousOperator

        char currentChar
        char previousChar
        char previousNonWSChar
        char previousCommandChar
        char quoteChar

        unsigned charNum
        int previousReadyFormattedLineLength

        bool isVirgin
        bool isInLineComment
        bool isInComment
        bool isInPreprocessor
        # True both in definitions (template<class A>) and usage (F<int>)
        bool isInTemplate
        bool doesLineStartComment
        bool isInQuote
        bool isSpecialChar
        bool isNonParenHeader
        bool foundQuestionMark
        bool foundPreDefinitionHeader
        bool foundPreCommandHeader
        bool isInLineBreak
        bool isInClosingBracketLineBreak
        bool endOfCodeReached
        bool isLineReady
        bool isPreviousBracketBlockRelated
        bool isInPotentialCalculation
        # bool foundOneLineBlock
        bool shouldReparseCurrentChar
        bool shouldBreakLineAfterComments
        bool passedSemicolon
        bool passedColon
        bool isImmediatelyPostComment
        bool isImmediatelyPostLineComment
        bool isImmediatelyPostEmptyBlock
        bool isPrependPostBlockEmptyLineRequested
        bool isAppendPostBlockEmptyLineRequested
        bool prependEmptyLine
        bool foundClosingHeader
        bool isInHeader
        bool isImmediatelyPostHeader


} # namespace astyle

#endif # ASTYLE_H

