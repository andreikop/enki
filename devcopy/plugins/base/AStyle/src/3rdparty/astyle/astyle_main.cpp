# $Id: astyle_main.cpp, 1.2 2005/07/01 18:58:17 mandrav Exp $
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
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with self program; if not, to the Free Software
# Foundation, Inc., Temple Place, 330, Boston, 02111-1307  USA
#
# --------------------------------------------------------------------------

#include "astyle.h"

#include <iostream>
#include <fstream>
#include <string>
#include <iterator>
#include <sstream>
#include <stdio.h>

using namespace std
using namespace astyle

# default options:
ostream *_err = &cerr
_suffix = ".orig"
shouldBackupFile = True
ostringstream msg

 _version = "1.17.0-dev"

# --------------------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------------------

def parseOption(self, &formatter, &arg, &errorInfo):
    TRACE( INFO, "Parsing option '" << arg << "'." )
    if  ( arg == "n" ) or ( arg == "suffix=none" ) :
        TRACE( INFO, "suffix=none" )
        shouldBackupFile = False

    elif  BEGINS_WITH(arg, "suffix=", 7) :
        suffixParam = arg.substr(strlen("suffix="))
        TRACE( INFO, "suffix=" << suffixParam )
        if suffixParam.size() > 0:
            _suffix = suffixParam

    elif  arg == "style=ansi" :
        TRACE( INFO, "style=ansi" )
        formatter.bracketIndent = False
        formatter.indentLength = 4
        formatter.indentString = "    "
        if  formatter.minConditionalIndent == INT_MIN :
            formatter.minConditionalIndent = formatter.indentLength * 2

        formatter.bracketFormatMode = BREAK_MODE
        formatter.classIndent = False
        formatter.switchIndent = False
        formatter.namespaceIndent = False

    elif  arg == "style=gnu" :
        TRACE( INFO, "style=gnu" )
        formatter.blockIndent = True
        formatter.bracketIndent = False
        formatter.indentLength = 2
        formatter.indentString = "  "
        if  formatter.minConditionalIndent == INT_MIN :
            formatter.minConditionalIndent = formatter.indentLength * 2

        formatter.bracketFormatMode = BREAK_MODE
        formatter.classIndent = False
        formatter.switchIndent = False
        formatter.namespaceIndent = False

    elif  arg == "style=java" :
        TRACE( INFO, "style=java" )
        formatter.sourceStyle = STYLE_JAVA
        formatter.modeSetManually = True
        formatter.bracketIndent = False
        formatter.indentLength = 4
        formatter.indentString = "    "
        if  formatter.minConditionalIndent == INT_MIN :
            formatter.minConditionalIndent = formatter.indentLength * 2

        formatter.bracketFormatMode = ATTACH_MODE
        formatter.switchIndent = False

    elif  arg == "style=kr" :
        #formatter.sourceStyle = STYLE_C
        #formatter.modeSetManually = True
        TRACE( INFO, "style=kr" )
        formatter.bracketIndent = False
        formatter.indentLength = 4
        formatter.indentString = "    "
        if  formatter.minConditionalIndent == INT_MIN :
            formatter.minConditionalIndent = formatter.indentLength * 2

        formatter.bracketFormatMode = ATTACH_MODE
        formatter.classIndent = False
        formatter.switchIndent = False
        formatter.namespaceIndent = False

    elif  arg == "style=linux" :
        TRACE( INFO, "style=linux" )
        formatter.bracketIndent = False
        formatter.indentLength = 8
        formatter.indentString = "        "
        if  formatter.minConditionalIndent == INT_MIN :
            formatter.minConditionalIndent = formatter.indentLength * 2

        formatter.bracketFormatMode = BDAC_MODE
        formatter.classIndent = False
        formatter.switchIndent = False
        formatter.namespaceIndent = False

    elif  (arg == "c") or (arg == "mode=c") :
        TRACE( INFO, "mode=c" )
        formatter.sourceStyle = STYLE_C
        formatter.modeSetManually = True

    elif  (arg == "j") or (arg == "mode=java") :
        TRACE( INFO, "mode=java" )
        formatter.sourceStyle = STYLE_JAVA
        formatter.modeSetManually = True

    elif  arg == "mode=csharp" :
        TRACE( INFO, "mode=csharp" )
        formatter.sourceStyle = STYLE_CSHARP
        formatter.modeSetManually = True

    elif  ( arg == "w" ) or ( arg == "eol=win" ) :
        TRACE( INFO, "eol=win" )
        formatter.eolString = "\r\n"; # not yet implementednot 

    elif  ( arg == "x" ) or ( arg == "eol=unix" ) :
        TRACE( INFO, "eol=unix" )
        formatter.eolString = "\n"; # not yet implementednot 

    elif  arg == "eol=mac" :
        TRACE( INFO, "eol=mac" )
        formatter.eolString = "\r"; # not yet implementednot 

    elif  arg == "indent=tab" :
        TRACE( INFO, "indent=tab" )
        formatter.indentString = "\t"
        formatter.indentLength = 4
        formatter.forceTabIndent = False
        if  formatter.minConditionalIndent == INT_MAX :
            formatter.minConditionalIndent = formatter.indentLength * 2


    elif  arg == "indent=spaces" :
        TRACE( INFO, "indent=spaces" )
        formatter.indentLength = 4
        formatter.indentString = "    "
        if  formatter.minConditionalIndent == INT_MIN :
            formatter.minConditionalIndent = formatter.indentLength * 2


    elif  (arg == "B") or (arg == "indent-brackets") :
        TRACE( INFO, "indent-brackets" )
        formatter.bracketIndent = True

    elif  (arg == "G") or (arg == "indent-blocks") :
        TRACE( INFO, "indent-blocks" )
        formatter.blockIndent = True
        formatter.bracketIndent = False

    elif  (arg == "N") or (arg == "indent-namespaces") :
        TRACE( INFO, "indent-namespaces" )
        formatter.namespaceIndent = True

    elif  (arg == "C") or (arg == "indent-classes") :
        TRACE( INFO, "indent-classes" )
        formatter.classIndent = True

    elif  (arg == "S") or (arg == "indent-switches") :
        TRACE( INFO, "indent-switches" )
        formatter.switchIndent = True

    elif  (arg == "K") or (arg == "indent-cases") :
        TRACE( INFO, "indent-cases" )
        formatter.caseIndent = True

    elif  (arg == "L") or (arg == "indent-labels") :
        TRACE( INFO, "indent-labels" )
        formatter.labelIndent = True

    elif arg == "indent-preprocessor":
        TRACE( INFO, "indent-preprocessor" )
        formatter.preprocessorIndent = True

    elif  arg == "brackets=break-closing-headers" :
        TRACE( INFO, "brackets=break-closing-headers" )
        formatter.breakClosingHeaderBrackets = True

    elif  (arg == "b") or (arg == "brackets=break") :
        TRACE( INFO, "brackets=break" )
        formatter.bracketFormatMode = BREAK_MODE

    elif  (arg == "a") or (arg == "brackets=attach") :
        TRACE( INFO, "brackets=attach" )
        formatter.bracketFormatMode = ATTACH_MODE

    elif  (arg == "l") or (arg == "brackets=linux") :
        TRACE( INFO, "brackets=linux" )
        formatter.bracketFormatMode = BDAC_MODE

    elif  (arg == "O") or (arg == "one-line=keep-blocks") :
        TRACE( INFO, "one-line=keep-blocks" )
        formatter.breakOneLineBlocks = False

    elif  (arg == "o") or (arg == "one-line=keep-statements") :
        TRACE( INFO, "one-line=keep-statements" )
        formatter.breakOneLineStatements = False

    elif  arg == "pad=paren" :
        TRACE( INFO, "pad=paren" )
        formatter.padParen = True

    elif  (arg == "P") or (arg == "pad=all") :
        TRACE( INFO, "pad=all" )
        formatter.padOperators = True
        formatter.padParen = True

    elif  (arg == "p") or (arg == "pad=oper") :
        TRACE( INFO, "pad=oper" )
        formatter.padOperators = True

    elif  (arg == "E") or (arg == "fill-empty-lines") :
        TRACE( INFO, "fill-empty-lines" )
        formatter.emptyLineIndent = True

    elif arg == "convert-tabs":
        TRACE( INFO, "convert-tabs" )
        formatter.convertTabs2Space = True

    elif arg == "break-blocks=all":
        TRACE( INFO, "break-blocks=all" )
        formatter.breakBlocks = True
        formatter.breakClosingHeaderBlocks = True

    elif arg == "break-blocks":
        TRACE( INFO, "break-blocks" )
        formatter.breakBlocks = True

    elif arg == "break-elseifs":
        TRACE( INFO, "break-elseifs" )
        formatter.breakElseIfs = True

    elif  (arg == "X") or (arg == "errors-to-standard-output") :
        TRACE( INFO, "errors-to-standard-output" )
        _err = &cout

    elif  (arg == "v") or (arg == "version") :
        TRACE( INFO, "version" )
        cout << "Artistic Style " << _version << endl
        exit(0)

    # parameterized short options at the end of the else-if cascade, or
    # they might be confused with long options starting with the same char
    elif  BEGINS_WITH( arg, "t", 1 ) or BEGINS_WITH( arg, "indent=tab=", 11 ) :
        TRACE( ENTRY, "indent=tab=" )
        spaceNum = 4
        spaceNumParam = (arg[0] == 't') ? arg.substr(1) : arg.substr(strlen("indent=tab="))
        if spaceNumParam.size() > 0:
            spaceNum = atoi(spaceNumParam.c_str())
        TRACE( EXIT, "indent=tab=" << spaceNum )
        formatter.indentString = "\t"
        formatter.indentLength = spaceNum
        formatter.forceTabIndent = False
        if  formatter.minConditionalIndent == INT_MAX :
            formatter.minConditionalIndent = formatter.indentLength * 2


    elif  BEGINS_WITH( arg, "T", 1 ) or BEGINS_WITH( arg, "force-indent=tab=", 17 ) :
        TRACE( ENTRY, "force-indent=tab=" )
        spaceNum = 4
        spaceNumParam = (arg[0] == 'T') ? arg.substr(1) : arg.substr(strlen("force-indent=tab="))
        if spaceNumParam.size() > 0:
            spaceNum = atoi(spaceNumParam.c_str())
        TRACE( EXIT, "force-indent=tab=" << spaceNum )
        formatter.indentString = "\t"
        formatter.indentLength = spaceNum
        formatter.forceTabIndent = True
        if  formatter.minConditionalIndent == INT_MIN :
            formatter.minConditionalIndent = formatter.indentLength * 2


    elif  BEGINS_WITH( arg, "s", 1 ) or BEGINS_WITH( arg, "indent=spaces=", 14 ) :
        TRACE( ENTRY, "indent=spaces=" )
        spaceNum = 4
        spaceNumParam = (arg[0] == 's') ? arg.substr(1) : arg.substr(strlen("indent=spaces="))
        if spaceNumParam.size() > 0:
            spaceNum = atoi(spaceNumParam.c_str())
        TRACE( EXIT, "indent=spaces=" << spaceNum )
        formatter.indentLength = spaceNum
        formatter.indentString = string(spaceNum, ' ')
        if  formatter.minConditionalIndent == INT_MIN :
            formatter.minConditionalIndent = formatter.indentLength * 2


    elif  BEGINS_WITH( arg, "M", 1 ) or BEGINS_WITH( arg, "max-instatement-indent=", 23 ) :
        TRACE( ENTRY, "max-instatement-indent=" )
        maxIndent = 40
        maxIndentParam = (arg[0] == 'M') ? arg.substr(1) : arg.substr(strlen("max-instatement-indent="))
        if maxIndentParam.size() > 0:
            maxIndent = atoi(maxIndentParam.c_str())
        TRACE( EXIT, "max-instatement-indent=" << maxIndent )
        formatter.maxInStatementIndent = maxIndent

    elif  BEGINS_WITH( arg, "m", 1 ) or BEGINS_WITH( arg, "min-conditional-indent=", 23 ) :
        TRACE( ENTRY, "min-conditional-indent=" )
        minIndent = 0
        minIndentParam = (arg[0] == 'm') ? arg.substr(1) : arg.substr(strlen("min-conditional-indent="))
        if minIndentParam.size() > 0:
            minIndent = atoi(minIndentParam.c_str())
        TRACE( EXIT, "min-conditional-indent=" << minIndent )
        formatter.minConditionalIndent = minIndent

    else:
        (*_err) << errorInfo << arg << endl
        return False; # unknown option

    return True; #o.k.




bool parseOptions(ASFormatter & formatter,
                  vector<string>.iterator optionsBegin,
                  vector<string>.iterator optionsEnd,
                   string & errorInfo)
    vector<string>.iterator option
    ok = True
    string arg, subArg
    for (option = optionsBegin; option != optionsEnd; ++option)
        arg = *option
        TRACE( INFO, "Parsing '" << arg << "'." )

        if BEGINS_WITH(arg, "--", 2):
            ok &= parseOption(formatter, arg.substr(2), errorInfo)
        elif arg[0] == '-':
            for (unsigned i=1; i < arg.size(); ++i)
                if isalpha(arg[i]) and i > 1:
                    ok &= parseOption(formatter, subArg, errorInfo)
                    subArg = ""

                subArg.append(1, arg[i])

            ok &= parseOption(formatter, subArg, errorInfo)
            subArg = ""

        else:
            ok &= parseOption(formatter, arg, errorInfo)
            subArg = ""



    return ok



def stringEndsWith(self, &str, &suffix):
    strIndex = str.size() - 1
    suffixIndex = suffix.size() - 1

    while (strIndex >= 0 and suffixIndex >= 0)
        if tolower(str[strIndex]) != tolower(suffix[suffixIndex]):
            return False

        --strIndex
        --suffixIndex


    return True



def isWriteable(self, *  filename ):
    std.ifstream in(filename)
    if not in:
        (*_err) << "File '" << filename << "' does not exist." << endl
        return False

    in.close()
    std.ofstream out(filename, std.ios_base.app)
    if not out:
        (*_err) << "File '" << filename << "' is not writeable." << endl
        return False

    out.close()
    return True



def printHelp(self):
    cout << endl
         << "Artistic Style " << _version << "   (http:#www.bigfoot.com/~davidsont/astyle)" << endl
         << "                       (created by Tal Davidson, davidsont@bigfoot.com)" << endl
         << "                       (maintained by Martin Baute, solar@rootdirectory.de)" << endl
    cout << endl
         << "Usage  :  astyle [options] < Original > Beautified" << endl
         << "          astyle [options] Foo.cpp Bar.cpp  [...]" << endl
    cout << endl
         << "When indenting a specific file, resulting indented file RETAINS the" << endl
         << "original file-name. The original pre-indented file is renamed, a" << endl
         << "suffix of \".orig\" added to the original filename." << endl
    cout << endl
         << "By default, is set up to indent C/C++/C# files, 4 spaces per" << endl
         << "indent, maximal indentation of 40 spaces inside continuous statements," << endl
         << "and NO formatting." << endl
    cout << endl
         << "Option's Format:" << endl
         << "----------------" << endl
    cout << endl
         << "    Long options (starting with '--') must be written one at a time." << endl
         << "    Short options (starting with '-') may be appended together." << endl
         << "    Thus, -bps4 is the same as -b -p -s4." << endl
    cout << endl
         << "Predefined Styling options:" << endl
         << "--------------------" << endl
    cout << endl
         << "    --style=ansi" << endl
         << "    ANSI style formatting/indenting." << endl
    cout << endl
         << "    --style=kr" << endl
         << "    Kernighan&Ritchie style formatting/indenting." << endl
    cout << endl
         << "    --style=gnu" << endl
         << "    GNU style formatting/indenting." << endl
    cout << endl
         << "    --style=java" << endl
         << "    Java mode, standard java style formatting/indenting." << endl
    cout << endl
         << "    --style=linux" << endl
         << "    Linux mode (i.e. 8 spaces per indent, definition-block" << endl
         << "    brackets but attach command-block brackets." << endl
    cout << endl
         << "Indentation options:" << endl
         << "--------------------" << endl
    cout << endl
         << "    -c\tOR\t--mode=c" << endl
         << "    Indent a C, C++ or C# source file (default)" << endl
    cout << endl
         << "    -j\tOR\t--mode=java" << endl
         << "    Indent a Java(TM) source file" << endl
    cout << endl
         << "    --mode=csharp" << endl
         << "    Indent a C# source file" << endl
    cout << endl
         << "    -s\tOR\t-s#\tOR\t--indent=spaces=#" << endl
         << "    Indent using # spaces per indent. Not specifying #" << endl
         << "    will result in a default of 4 spaces per indent." << endl
    cout << endl
         << "    -t\tOR\t-t#\tOR\t--indent=tab=#" << endl
         << "    Indent using tab characters, that each" << endl
         << "    tab is # spaces long. Not specifying # will result" << endl
         << "    in a default assumption of 4 spaces per tab." << endl
    cout << endl
         << "    -T#\tOR\t--force-indent=tab=#" << endl
         << "    Indent using tab characters, that each" << endl
         << "    tab is # spaces long. Force tabs to be used in areas" << endl
         << "    Astyle would prefer to use spaces." << endl
    cout << endl
         << "    -C\tOR\t--indent-classes" << endl
         << "    Indent 'class' blocks, that the inner 'public:'," << endl
         << "    'protected:' and 'private: headers are indented in" << endl
         << "    relation to the class block." << endl
    cout << endl
         << "    -S\tOR\t--indent-switches" << endl
         << "    Indent 'switch' blocks, that the inner 'case XXX:'" << endl
         << "    headers are indented in relation to the switch block." << endl
    cout << endl
         << "    -K\tOR\t--indent-cases" << endl
         << "    Indent 'case XXX:' lines, that they are flush with" << endl
         << "    their bodies.." << endl
    cout << endl
         << "    -N\tOR\t--indent-namespaces" << endl
         << "    Indent the contents of namespace blocks." << endl
    cout << endl
         << "    -B\tOR\t--indent-brackets" << endl
         << "    Add extra indentation to '{' and '}' block brackets." << endl
    cout << endl
         << "    -G\tOR\t--indent-blocks" << endl
         << "    Add extra indentation entire blocks (including brackets)." << endl
    cout << endl
         << "    -L\tOR\t--indent-labels" << endl
         << "    Indent labels so that they appear one indent less than" << endl
         << "    the current indentation level, than being" << endl
         << "    flushed completely to the left (which is the default)." << endl
    cout << endl
         << "    -m#\tOR\t--min-conditional-indent=#" << endl
         << "    Indent a minimal # spaces in a continuous conditional" << endl
         << "    belonging to a conditional header." << endl
    cout << endl
         << "    -M#\tOR\t--max-instatement-indent=#" << endl
         << "    Indent a maximal # spaces in a continuous statement," << endl
         << "    relatively to the previous line." << endl
    cout << endl
         << "    -E\tOR\t--fill-empty-lines" << endl
         << "    Fill empty lines with the white space of their" << endl
         << "    previous lines." << endl
    cout << endl
         << "    --indent-preprocessor" << endl
         << "    Indent multi-line #define statements" << endl
    cout << endl
         << "Formatting options:" << endl
         << "-------------------" << endl
    cout << endl
         << "    -b\tOR\t--brackets=break" << endl
         << "    Break brackets from pre-block code (i.e. ANSI C/C++ style)." << endl
    cout << endl
         << "    -a\tOR\t--brackets=attach" << endl
         << "    Attach brackets to pre-block code (i.e. Java/K&R style)." << endl
    cout << endl
         << "    -l\tOR\t--brackets=linux" << endl
         << "    Break definition-block brackets and attach command-block" << endl
         << "    brackets." << endl
    cout << endl
         << "    --brackets=break-closing-headers" << endl
         << "    Break brackets before closing headers (e.g. 'else', 'catch', ..)." << endl
         << "    Should be appended to --brackets=attach or --brackets=linux." << endl
    cout << endl
         << "    -o\tOR\t--one-line=keep-statements" << endl
         << "    Don't break lines containing multiple statements into" << endl
         << "    multiple single-statement lines." << endl
    cout << endl
         << "    -O\tOR\t--one-line=keep-blocks" << endl
         << "    Don't break blocks residing completely on one line" << endl
    cout << endl
         << "    -p\tOR\t--pad=oper" << endl
         << "    Insert space paddings around operators only." << endl
    cout << endl
         << "    --pad=paren" << endl
         << "    Insert space paddings around parenthesies only." << endl
    cout << endl
         << "    -P\tOR\t--pad=all" << endl
         << "    Insert space paddings around operators AND parenthesies." << endl
    cout << endl
         << "    --convert-tabs" << endl
         << "    Convert tabs to spaces." << endl
    cout << endl
         << "    --break-blocks" << endl
         << "    Insert empty lines around unrelated blocks, labels, classes, ..." << endl
    cout << endl
         << "    --break-blocks=all" << endl
         << "    Like --break-blocks, also insert empty lines " << endl
         << "    around closing headers (e.g. 'else', 'catch', ...)." << endl
    cout << endl
         << "    --break-elseifs" << endl
         << "    Break 'elif()' statements into two different lines." << endl
    cout << endl
         << "Other options:" << endl
         << "-------------" << endl
    cout << endl
         << "    --suffix=####" << endl
         << "    Append the suffix #### instead of '.orig' to original filename." << endl
    cout << endl
         << "    -n\tOR\t--suffix=none" << endl
         << "    Tells Astyle not to keep backups of the original source files." << endl
         << "    WARNING: Use self option with care, Astyle comes with NO WARRANTY..." << endl
    cout << endl
         << "    -X\tOR\t--errors-to-standard-output" << endl
         << "    Print errors to standard-output rather than standard-error." << endl
    cout << endl
         << "    -v\tOR\t--version" << endl
         << "    Print version number" << endl
    cout << endl
         << "    -h\tOR\t-?\tOR\t--help" << endl
         << "    Print self help message" << endl
    cout << endl
         << "Default options file:" << endl
         << "---------------------" << endl
    cout << endl
         << "    Artistic Style looks for a default options file in the" << endl
         << "    following order:" << endl
         << "    1. The contents of the ARTISTIC_STYLE_OPTIONS environment" << endl
         << "       variable if it exists." << endl
         << "    2. The file called .astylerc in the directory pointed to by the" << endl
         << "       HOME environment variable ( i.e. $HOME/.astylerc )." << endl
         << "    3. The file called .astylerc in the directory pointed to by the" << endl
         << "       HOMEDRIVE and HOMEPATH environment variables ( i.e.," << endl
         << "       %HOMEDRIVE%%HOMEPATH%\\.astylerc )." << endl
         << "    If a default options file is found, options in self file" << endl
         << "    will be parsed BEFORE the command-line options." << endl
         << "    Options within the default option file may be written without" << endl
         << "    the preliminary '-' or '--'." << endl
         << endl


def main(self, argc, *argv[]):
    ASFormatter formatter
    vector<string> fileNameVector
    vector<string> optionsVector
    optionsFileName = ""
    string arg
    ok = True
    shouldPrintHelp = False
    shouldParseOptionsFile = True

    # manage flags
    for (int i=1; i<argc; i++)
        arg = string(argv[i])

        if  BEGINS_WITH(arg ,"--options=none", 14) :
            TRACE( INFO, "options=none" )
            shouldParseOptionsFile = False

        elif  BEGINS_WITH(arg ,"--options=", 10) :
            TRACE( ENTRY, "options=" )
            optionsFileName = arg.substr(strlen("--options="))
            TRACE( EXIT, "options=" << optionsFileName )

        elif  (arg == "-h") or (arg == "--help") or (arg == "-?") :
            TRACE( INFO, "help" )
            shouldPrintHelp = True

        elif arg[0] == '-':
            TRACE( INFO, "option: " << arg )
            optionsVector.push_back(arg)

        else # file-name
            TRACE( INFO, "source: " << arg )
            fileNameVector.push_back(arg)



    # parse options file
    if shouldParseOptionsFile:
        TRACE( INFO, "Options file should be read..." )
        if optionsFileName.empty():
            env = getenv("ARTISTIC_STYLE_OPTIONS")
            if env != NULL:
                optionsFileName = string(env)
            TRACE( INFO, "Taken filename '" << optionsFileName << "' from $ARTISTIC_STYLE_OPTIONS." )

        if optionsFileName.empty():
            env = getenv("HOME")
            if env != NULL:
                optionsFileName = string(env) + string("/.astylerc")
            TRACE( INFO, "Assembled filename '" << optionsFileName << "' from $HOME/.astylerc." )

        if optionsFileName.empty():
            drive = getenv("HOMEDRIVE")
            path = getenv("HOMEPATH")
            if path != NULL:
                optionsFileName = string(drive) + string(path) + string("/.astylerc")
            TRACE( INFO, "Assembled filename '" << optionsFileName << "' from %HOMEDRIVE%%HOMEPATH%/.astylerc." )


        if not optionsFileName.empty():
            ifstream optionsIn(optionsFileName.c_str())
            TRACE( INFO, "Reading options file " << optionsFileName )
            if optionsIn:
                vector<string> fileOptionsVector
                # reading (whitespace seperated) strings from file into string vector
                string buffer
                while (optionsIn)
                    getline(optionsIn, buffer)
                    TRACE( INFO, "Read line: '" << buffer << "'" )
                    if optionsIn.fail() or (buffer.size() == 0) or (buffer[0] == '#'):
                        TRACE( INFO, "Invalid line (EOF, line, comment line)" )
                        continue

                    istringstream buf(buffer)
                    copy(istream_iterator<string>(buf), istream_iterator<string>(), back_inserter(fileOptionsVector))

                TRACE( ENTRY, "Options read:" )
#ifndef NDEBUG
                for ( unsigned i = 0; i < fileOptionsVector.size(); ++i )
                    TRACE( INFO, fileOptionsVector[i] )
                TRACE( EXIT, "End of options." )
#endif
                ok = parseOptions(formatter,
                                  fileOptionsVector.begin(),
                                  fileOptionsVector.end(),
                                  "Unknown option in default options file: ")

            else:
                TRACE( INFO, "Could not open options file " << optionsFileName )


            optionsIn.close()
            if not ok:
                (*_err) << "For help on options, type 'astyle -h' " << endl



    else:
        TRACE( INFO, "Options file disabled." )


    # parse options from command line

    ok = parseOptions(formatter,
                      optionsVector.begin(),
                      optionsVector.end(),
                      "Unknown command line option: ")
    if not ok:
        (*_err) << "For help on options, type 'astyle -h' " << endl
        exit(1)


    if shouldPrintHelp:
        printHelp()
        return 1


    # if no files have been given, cin for input and cout for output
    if fileNameVector.empty():
        formatter.init( cin )

        while (formatter.hasMoreLines() )
            cout << formatter.nextLine()
            if formatter.hasMoreLines():
                cout << endl

        cout.flush()

    else:
        # indent the given files
        for (unsigned i=0; i<fileNameVector.size(); i++)
            originalFileName = fileNameVector[i]
            inFileName = originalFileName + _suffix

            if  not  isWriteable(originalFileName.c_str()) :
                (*_err) << "File '" << originalFileName << "' does not exist, is read-only." << endl
                continue


            remove(inFileName.c_str())

            if  rename(originalFileName.c_str(), inFileName.c_str()) < 0:
                (*_err) << "Could not rename " << originalFileName << " to " << inFileName << endl
                exit(1)


            TRACE( INFO, "Processing file " << originalFileName << "..." )
            ifstream in(inFileName.c_str())
            if not in:
                (*_err) << "Could not open input file" << inFileName << endl
                exit(1)


            ofstream out(originalFileName.c_str())
            if not out:
                (*_err) << "Could not open output file" << originalFileName << endl
                exit(1)


            # Unless a specific language mode has been set, the language mode
            # according to the file's suffix.
            if not formatter.modeSetManually:
                if stringEndsWith(originalFileName, ".java"):
                    TRACE( INFO, "Setting style=java according to filename extension on " << originalFileName )
                    formatter.sourceStyle = STYLE_JAVA

                elif stringEndsWith(originalFileName, ".sc") or stringEndsWith(originalFileName, ".cs"):
                    TRACE( INFO, "Setting style=csharp according to filename extension on " << originalFileName )
                    formatter.sourceStyle = STYLE_CSHARP

                else:
                    TRACE( INFO, "Setting style=c according to non-java/csharp filename extension on " << originalFileName )
                    formatter.sourceStyle = STYLE_C



            formatter.init( in )
            while (formatter.hasMoreLines() )
                out << formatter.nextLine()
                if formatter.hasMoreLines():
                    out << endl


            out.flush()
            out.close()

            in.close()
            if  not  shouldBackupFile :
                TRACE( INFO, "Removing backup file as requested..." )
                remove( inFileName.c_str() )



    return 0


