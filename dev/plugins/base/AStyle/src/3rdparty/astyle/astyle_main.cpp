// $Id: astyle_main.cpp,v 1.2 2005/07/01 18:58:17 mandrav Exp $
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
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
// --------------------------------------------------------------------------

#include "astyle.h"

#include <iostream>
#include <fstream>
#include <string>
#include <iterator>
#include <sstream>
#include <stdio.h>

using namespace std;
using namespace astyle;

// default options:
ostream *_err = &cerr;
string _suffix = ".orig";
bool shouldBackupFile = true;
ostringstream msg;

const string _version = "1.17.0-dev";

// --------------------------------------------------------------------------
// Helper Functions
// --------------------------------------------------------------------------

bool parseOption(ASFormatter &formatter, const string &arg, const string &errorInfo)
{
    TRACE( INFO, "Parsing option '" << arg << "'." );
    if ( ( arg == "n" ) || ( arg == "suffix=none" ) )
    {
        TRACE( INFO, "suffix=none" );
        shouldBackupFile = false;
    }
    else if ( BEGINS_WITH(arg, "suffix=", 7) )
    {
        string suffixParam = arg.substr(strlen("suffix="));
        TRACE( INFO, "suffix=" << suffixParam );
        if (suffixParam.size() > 0)
            _suffix = suffixParam;
    }
    else if ( arg == "style=ansi" )
    {
        TRACE( INFO, "style=ansi" );
        formatter.bracketIndent = false;
        formatter.indentLength = 4;
        formatter.indentString = "    ";
        if ( formatter.minConditionalIndent == INT_MIN )
        {
            formatter.minConditionalIndent = formatter.indentLength * 2;
        }
        formatter.bracketFormatMode = BREAK_MODE;
        formatter.classIndent = false;
        formatter.switchIndent = false;
        formatter.namespaceIndent = false;
    }
    else if ( arg == "style=gnu" )
    {
        TRACE( INFO, "style=gnu" );
        formatter.blockIndent = true;
        formatter.bracketIndent = false;
        formatter.indentLength = 2;
        formatter.indentString = "  ";
        if ( formatter.minConditionalIndent == INT_MIN )
        {
            formatter.minConditionalIndent = formatter.indentLength * 2;
        }
        formatter.bracketFormatMode = BREAK_MODE;
        formatter.classIndent = false;
        formatter.switchIndent = false;
        formatter.namespaceIndent = false;
    }
    else if ( arg == "style=java" )
    {
        TRACE( INFO, "style=java" );
        formatter.sourceStyle = STYLE_JAVA;
        formatter.modeSetManually = true;
        formatter.bracketIndent = false;
        formatter.indentLength = 4;
        formatter.indentString = "    ";
        if ( formatter.minConditionalIndent == INT_MIN )
        {
            formatter.minConditionalIndent = formatter.indentLength * 2;
        }
        formatter.bracketFormatMode = ATTACH_MODE;
        formatter.switchIndent = false;
    }
    else if ( arg == "style=kr" )
    {
        //formatter.sourceStyle = STYLE_C;
        //formatter.modeSetManually = true;
        TRACE( INFO, "style=kr" );
        formatter.bracketIndent = false;
        formatter.indentLength = 4;
        formatter.indentString = "    ";
        if ( formatter.minConditionalIndent == INT_MIN )
        {
            formatter.minConditionalIndent = formatter.indentLength * 2;
        }
        formatter.bracketFormatMode = ATTACH_MODE;
        formatter.classIndent = false;
        formatter.switchIndent = false;
        formatter.namespaceIndent = false;
    }
    else if ( arg == "style=linux" )
    {
        TRACE( INFO, "style=linux" );
        formatter.bracketIndent = false;
        formatter.indentLength = 8;
        formatter.indentString = "        ";
        if ( formatter.minConditionalIndent == INT_MIN )
        {
            formatter.minConditionalIndent = formatter.indentLength * 2;
        }
        formatter.bracketFormatMode = BDAC_MODE;
        formatter.classIndent = false;
        formatter.switchIndent = false;
        formatter.namespaceIndent = false;
    }
    else if ( (arg == "c") || (arg == "mode=c") )
    {
        TRACE( INFO, "mode=c" );
        formatter.sourceStyle = STYLE_C;
        formatter.modeSetManually = true;
    }
    else if ( (arg == "j") || (arg == "mode=java") )
    {
        TRACE( INFO, "mode=java" );
        formatter.sourceStyle = STYLE_JAVA;
        formatter.modeSetManually = true;
    }
    else if ( arg == "mode=csharp" )
    {
        TRACE( INFO, "mode=csharp" );
        formatter.sourceStyle = STYLE_CSHARP;
        formatter.modeSetManually = true;
    }
    else if ( ( arg == "w" ) || ( arg == "eol=win" ) )
    {
        TRACE( INFO, "eol=win" );
        formatter.eolString = "\r\n"; // not yet implemented!
    }
    else if ( ( arg == "x" ) || ( arg == "eol=unix" ) )
    {
        TRACE( INFO, "eol=unix" );
        formatter.eolString = "\n"; // not yet implemented!
    }
    else if ( arg == "eol=mac" )
    {
        TRACE( INFO, "eol=mac" );
        formatter.eolString = "\r"; // not yet implemented!
    }
    else if ( arg == "indent=tab" )
    {
        TRACE( INFO, "indent=tab" );
        formatter.indentString = "\t";
        formatter.indentLength = 4;
        formatter.forceTabIndent = false;
        if ( formatter.minConditionalIndent == INT_MAX )
        {
            formatter.minConditionalIndent = formatter.indentLength * 2;
        }
    }
    else if ( arg == "indent=spaces" )
    {
        TRACE( INFO, "indent=spaces" );
        formatter.indentLength = 4;
        formatter.indentString = "    ";
        if ( formatter.minConditionalIndent == INT_MIN )
        {
            formatter.minConditionalIndent = formatter.indentLength * 2;
        }
    }
    else if ( (arg == "B") || (arg == "indent-brackets") )
    {
        TRACE( INFO, "indent-brackets" );
        formatter.bracketIndent = true;
    }
    else if ( (arg == "G") || (arg == "indent-blocks") )
    {
        TRACE( INFO, "indent-blocks" );
        formatter.blockIndent = true;
        formatter.bracketIndent = false;
    }
    else if ( (arg == "N") || (arg == "indent-namespaces") )
    {
        TRACE( INFO, "indent-namespaces" );
        formatter.namespaceIndent = true;
    }
    else if ( (arg == "C") || (arg == "indent-classes") )
    {
        TRACE( INFO, "indent-classes" );
        formatter.classIndent = true;
    }
    else if ( (arg == "S") || (arg == "indent-switches") )
    {
        TRACE( INFO, "indent-switches" );
        formatter.switchIndent = true;
    }
    else if ( (arg == "K") || (arg == "indent-cases") )
    {
        TRACE( INFO, "indent-cases" );
        formatter.caseIndent = true;
    }
    else if ( (arg == "L") || (arg == "indent-labels") )
    {
        TRACE( INFO, "indent-labels" );
        formatter.labelIndent = true;
    }
    else if (arg == "indent-preprocessor")
    {
        TRACE( INFO, "indent-preprocessor" );
        formatter.preprocessorIndent = true;
    }
    else if ( arg == "brackets=break-closing-headers" )
    {
        TRACE( INFO, "brackets=break-closing-headers" );
        formatter.breakClosingHeaderBrackets = true;
    }
    else if ( (arg == "b") || (arg == "brackets=break") )
    {
        TRACE( INFO, "brackets=break" );
        formatter.bracketFormatMode = BREAK_MODE;
    }
    else if ( (arg == "a") || (arg == "brackets=attach") )
    {
        TRACE( INFO, "brackets=attach" );
        formatter.bracketFormatMode = ATTACH_MODE;
    }
    else if ( (arg == "l") || (arg == "brackets=linux") )
    {
        TRACE( INFO, "brackets=linux" );
        formatter.bracketFormatMode = BDAC_MODE;
    }
    else if ( (arg == "O") || (arg == "one-line=keep-blocks") )
    {
        TRACE( INFO, "one-line=keep-blocks" );
        formatter.breakOneLineBlocks = false;
    }
    else if ( (arg == "o") || (arg == "one-line=keep-statements") )
    {
        TRACE( INFO, "one-line=keep-statements" );
        formatter.breakOneLineStatements = false;
    }
    else if ( arg == "pad=paren" )
    {
        TRACE( INFO, "pad=paren" );
        formatter.padParen = true;
    }
    else if ( (arg == "P") || (arg == "pad=all") )
    {
        TRACE( INFO, "pad=all" );
        formatter.padOperators = true;
        formatter.padParen = true;
    }
    else if ( (arg == "p") || (arg == "pad=oper") )
    {
        TRACE( INFO, "pad=oper" );
        formatter.padOperators = true;
    }
    else if ( (arg == "E") || (arg == "fill-empty-lines") )
    {
        TRACE( INFO, "fill-empty-lines" );
        formatter.emptyLineIndent = true;
    }
    else if (arg == "convert-tabs")
    {
        TRACE( INFO, "convert-tabs" );
        formatter.convertTabs2Space = true;
    }
    else if (arg == "break-blocks=all")
    {
        TRACE( INFO, "break-blocks=all" );
        formatter.breakBlocks = true;
        formatter.breakClosingHeaderBlocks = true;
    }
    else if (arg == "break-blocks")
    {
        TRACE( INFO, "break-blocks" );
        formatter.breakBlocks = true;
    }
    else if (arg == "break-elseifs")
    {
        TRACE( INFO, "break-elseifs" );
        formatter.breakElseIfs = true;
    }
    else if ( (arg == "X") || (arg == "errors-to-standard-output") )
    {
        TRACE( INFO, "errors-to-standard-output" );
        _err = &cout;
    }
    else if ( (arg == "v") || (arg == "version") )
    {
        TRACE( INFO, "version" );
        cout << "Artistic Style " << _version << endl;
        exit(0);
    }
    // parameterized short options at the end of the else-if cascade, or
    // they might be confused with long options starting with the same char
    else if ( BEGINS_WITH( arg, "t", 1 ) || BEGINS_WITH( arg, "indent=tab=", 11 ) )
    {
        TRACE( ENTRY, "indent=tab=" );
        int spaceNum = 4;
        string spaceNumParam = (arg[0] == 't') ? arg.substr(1) : arg.substr(strlen("indent=tab="));
        if (spaceNumParam.size() > 0)
            spaceNum = atoi(spaceNumParam.c_str());
        TRACE( EXIT, "indent=tab=" << spaceNum );
        formatter.indentString = "\t";
        formatter.indentLength = spaceNum;
        formatter.forceTabIndent = false;
        if ( formatter.minConditionalIndent == INT_MAX )
        {
            formatter.minConditionalIndent = formatter.indentLength * 2;
        }
    }
    else if ( BEGINS_WITH( arg, "T", 1 ) || BEGINS_WITH( arg, "force-indent=tab=", 17 ) )
    {
        TRACE( ENTRY, "force-indent=tab=" );
        int spaceNum = 4;
        string spaceNumParam = (arg[0] == 'T') ? arg.substr(1) : arg.substr(strlen("force-indent=tab="));
        if (spaceNumParam.size() > 0)
            spaceNum = atoi(spaceNumParam.c_str());
        TRACE( EXIT, "force-indent=tab=" << spaceNum );
        formatter.indentString = "\t";
        formatter.indentLength = spaceNum;
        formatter.forceTabIndent = true;
        if ( formatter.minConditionalIndent == INT_MIN )
        {
            formatter.minConditionalIndent = formatter.indentLength * 2;
        }
    }
    else if ( BEGINS_WITH( arg, "s", 1 ) || BEGINS_WITH( arg, "indent=spaces=", 14 ) )
    {
        TRACE( ENTRY, "indent=spaces=" );
        int spaceNum = 4;
        string spaceNumParam = (arg[0] == 's') ? arg.substr(1) : arg.substr(strlen("indent=spaces="));
        if (spaceNumParam.size() > 0)
            spaceNum = atoi(spaceNumParam.c_str());
        TRACE( EXIT, "indent=spaces=" << spaceNum );
        formatter.indentLength = spaceNum;
        formatter.indentString = string(spaceNum, ' ');
        if ( formatter.minConditionalIndent == INT_MIN )
        {
            formatter.minConditionalIndent = formatter.indentLength * 2;
        }
    }
    else if ( BEGINS_WITH( arg, "M", 1 ) || BEGINS_WITH( arg, "max-instatement-indent=", 23 ) )
    {
        TRACE( ENTRY, "max-instatement-indent=" );
        int maxIndent = 40;
        string maxIndentParam = (arg[0] == 'M') ? arg.substr(1) : arg.substr(strlen("max-instatement-indent="));
        if (maxIndentParam.size() > 0)
            maxIndent = atoi(maxIndentParam.c_str());
        TRACE( EXIT, "max-instatement-indent=" << maxIndent );
        formatter.maxInStatementIndent = maxIndent;
    }
    else if ( BEGINS_WITH( arg, "m", 1 ) || BEGINS_WITH( arg, "min-conditional-indent=", 23 ) )
    {
        TRACE( ENTRY, "min-conditional-indent=" );
        int minIndent = 0;
        string minIndentParam = (arg[0] == 'm') ? arg.substr(1) : arg.substr(strlen("min-conditional-indent="));
        if (minIndentParam.size() > 0)
            minIndent = atoi(minIndentParam.c_str());
        TRACE( EXIT, "min-conditional-indent=" << minIndent );
        formatter.minConditionalIndent = minIndent;
    }
    else
    {
        (*_err) << errorInfo << arg << endl;
        return false; // unknown option
    }
    return true; //o.k.
}



bool parseOptions(ASFormatter & formatter,
                  vector<string>::iterator optionsBegin,
                  vector<string>::iterator optionsEnd,
                  const string & errorInfo)
{
    vector<string>::iterator option;
    bool ok = true;
    string arg, subArg;
    for (option = optionsBegin; option != optionsEnd; ++option)
    {
        arg = *option;
        TRACE( INFO, "Parsing '" << arg << "'." );

        if (BEGINS_WITH(arg, "--", 2))
            ok &= parseOption(formatter, arg.substr(2), errorInfo);
        else if (arg[0] == '-')
        {
            for (unsigned i=1; i < arg.size(); ++i)
            {
                if (isalpha(arg[i]) && i > 1)
                {
                    ok &= parseOption(formatter, subArg, errorInfo);
                    subArg = "";
                }
                subArg.append(1, arg[i]);
            }
            ok &= parseOption(formatter, subArg, errorInfo);
            subArg = "";
        }
        else
        {
            ok &= parseOption(formatter, arg, errorInfo);
            subArg = "";
        }
    }

    return ok;
}


bool stringEndsWith(const string &str, const string &suffix)
{
    int strIndex = str.size() - 1;
    int suffixIndex = suffix.size() - 1;

    while (strIndex >= 0 && suffixIndex >= 0)
    {
        if (tolower(str[strIndex]) != tolower(suffix[suffixIndex]))
            return false;

        --strIndex;
        --suffixIndex;
    }

    return true;
}


bool isWriteable( char const * const filename )
{
    std::ifstream in(filename);
    if (!in)
    {
        (*_err) << "File '" << filename << "' does not exist." << endl;
        return false;
    }
    in.close();
    std::ofstream out(filename, std::ios_base::app);
    if (!out)
    {
        (*_err) << "File '" << filename << "' is not writeable." << endl;
        return false;
    }
    out.close();
    return true;
}


void printHelp()
{
    cout << endl
    << "Artistic Style " << _version << "   (http://www.bigfoot.com/~davidsont/astyle)" << endl
    << "                       (created by Tal Davidson, davidsont@bigfoot.com)" << endl
    << "                       (maintained by Martin Baute, solar@rootdirectory.de)" << endl;
    cout << endl
    << "Usage  :  astyle [options] < Original > Beautified" << endl
    << "          astyle [options] Foo.cpp Bar.cpp  [...]" << endl;
    cout << endl
    << "When indenting a specific file, the resulting indented file RETAINS the" << endl
    << "original file-name. The original pre-indented file is renamed, with a" << endl
    << "suffix of \".orig\" added to the original filename." << endl;
    cout << endl
    << "By default, astyle is set up to indent C/C++/C# files, with 4 spaces per" << endl
    << "indent, a maximal indentation of 40 spaces inside continuous statements," << endl
    << "and NO formatting." << endl;
    cout << endl
    << "Option's Format:" << endl
    << "----------------" << endl;
    cout << endl
    << "    Long options (starting with '--') must be written one at a time." << endl
    << "    Short options (starting with '-') may be appended together." << endl
    << "    Thus, -bps4 is the same as -b -p -s4." << endl;
    cout << endl
    << "Predefined Styling options:" << endl
    << "--------------------" << endl;
    cout << endl
    << "    --style=ansi" << endl
    << "    ANSI style formatting/indenting." << endl;
    cout << endl
    << "    --style=kr" << endl
    << "    Kernighan&Ritchie style formatting/indenting." << endl;
    cout << endl
    << "    --style=gnu" << endl
    << "    GNU style formatting/indenting." << endl;
    cout << endl
    << "    --style=java" << endl
    << "    Java mode, with standard java style formatting/indenting." << endl;
    cout << endl
    << "    --style=linux" << endl
    << "    Linux mode (i.e. 8 spaces per indent, break definition-block" << endl
    << "    brackets but attach command-block brackets." << endl;
    cout << endl
    << "Indentation options:" << endl
    << "--------------------" << endl;
    cout << endl
    << "    -c\tOR\t--mode=c" << endl
    << "    Indent a C, C++ or C# source file (default)" << endl;
    cout << endl
    << "    -j\tOR\t--mode=java" << endl
    << "    Indent a Java(TM) source file" << endl;
    cout << endl
    << "    --mode=csharp" << endl
    << "    Indent a C# source file" << endl;
    cout << endl
    << "    -s\tOR\t-s#\tOR\t--indent=spaces=#" << endl
    << "    Indent using # spaces per indent. Not specifying #" << endl
    << "    will result in a default of 4 spaces per indent." << endl;
    cout << endl
    << "    -t\tOR\t-t#\tOR\t--indent=tab=#" << endl
    << "    Indent using tab characters, assuming that each" << endl
    << "    tab is # spaces long. Not specifying # will result" << endl
    << "    in a default assumption of 4 spaces per tab." << endl;
    cout << endl
    << "    -T#\tOR\t--force-indent=tab=#" << endl
    << "    Indent using tab characters, assuming that each" << endl
    << "    tab is # spaces long. Force tabs to be used in areas" << endl
    << "    Astyle would prefer to use spaces." << endl;
    cout << endl
    << "    -C\tOR\t--indent-classes" << endl
    << "    Indent 'class' blocks, so that the inner 'public:'," << endl
    << "    'protected:' and 'private: headers are indented in" << endl
    << "    relation to the class block." << endl;
    cout << endl
    << "    -S\tOR\t--indent-switches" << endl
    << "    Indent 'switch' blocks, so that the inner 'case XXX:'" << endl
    << "    headers are indented in relation to the switch block." << endl;
    cout << endl
    << "    -K\tOR\t--indent-cases" << endl
    << "    Indent 'case XXX:' lines, so that they are flush with" << endl
    << "    their bodies.." << endl;
    cout << endl
    << "    -N\tOR\t--indent-namespaces" << endl
    << "    Indent the contents of namespace blocks." << endl;
    cout << endl
    << "    -B\tOR\t--indent-brackets" << endl
    << "    Add extra indentation to '{' and '}' block brackets." << endl;
    cout << endl
    << "    -G\tOR\t--indent-blocks" << endl
    << "    Add extra indentation entire blocks (including brackets)." << endl;
    cout << endl
    << "    -L\tOR\t--indent-labels" << endl
    << "    Indent labels so that they appear one indent less than" << endl
    << "    the current indentation level, rather than being" << endl
    << "    flushed completely to the left (which is the default)." << endl;
    cout << endl
    << "    -m#\tOR\t--min-conditional-indent=#" << endl
    << "    Indent a minimal # spaces in a continuous conditional" << endl
    << "    belonging to a conditional header." << endl;
    cout << endl
    << "    -M#\tOR\t--max-instatement-indent=#" << endl
    << "    Indent a maximal # spaces in a continuous statement," << endl
    << "    relatively to the previous line." << endl;
    cout << endl
    << "    -E\tOR\t--fill-empty-lines" << endl
    << "    Fill empty lines with the white space of their" << endl
    << "    previous lines." << endl;
    cout << endl
    << "    --indent-preprocessor" << endl
    << "    Indent multi-line #define statements" << endl;
    cout << endl
    << "Formatting options:" << endl
    << "-------------------" << endl;
    cout << endl
    << "    -b\tOR\t--brackets=break" << endl
    << "    Break brackets from pre-block code (i.e. ANSI C/C++ style)." << endl;
    cout << endl
    << "    -a\tOR\t--brackets=attach" << endl
    << "    Attach brackets to pre-block code (i.e. Java/K&R style)." << endl;
    cout << endl
    << "    -l\tOR\t--brackets=linux" << endl
    << "    Break definition-block brackets and attach command-block" << endl
    << "    brackets." << endl;
    cout << endl
    << "    --brackets=break-closing-headers" << endl
    << "    Break brackets before closing headers (e.g. 'else', 'catch', ..)." << endl
    << "    Should be appended to --brackets=attach or --brackets=linux." << endl;
    cout << endl
    << "    -o\tOR\t--one-line=keep-statements" << endl
    << "    Don't break lines containing multiple statements into" << endl
    << "    multiple single-statement lines." << endl;
    cout << endl
    << "    -O\tOR\t--one-line=keep-blocks" << endl
    << "    Don't break blocks residing completely on one line" << endl;
    cout << endl
    << "    -p\tOR\t--pad=oper" << endl
    << "    Insert space paddings around operators only." << endl;
    cout << endl
    << "    --pad=paren" << endl
    << "    Insert space paddings around parenthesies only." << endl;
    cout << endl
    << "    -P\tOR\t--pad=all" << endl
    << "    Insert space paddings around operators AND parenthesies." << endl;
    cout << endl
    << "    --convert-tabs" << endl
    << "    Convert tabs to spaces." << endl;
    cout << endl
    << "    --break-blocks" << endl
    << "    Insert empty lines around unrelated blocks, labels, classes, ..." << endl;
    cout << endl
    << "    --break-blocks=all" << endl
    << "    Like --break-blocks, except also insert empty lines " << endl
    << "    around closing headers (e.g. 'else', 'catch', ...)." << endl;
    cout << endl
    << "    --break-elseifs" << endl
    << "    Break 'else if()' statements into two different lines." << endl;
    cout << endl
    << "Other options:" << endl
    << "-------------" << endl;
    cout << endl
    << "    --suffix=####" << endl
    << "    Append the suffix #### instead of '.orig' to original filename." << endl;
    cout << endl
    << "    -n\tOR\t--suffix=none" << endl
    << "    Tells Astyle not to keep backups of the original source files." << endl
    << "    WARNING: Use this option with care, as Astyle comes with NO WARRANTY..." << endl;
    cout << endl
    << "    -X\tOR\t--errors-to-standard-output" << endl
    << "    Print errors to standard-output rather than standard-error." << endl;
    cout << endl
    << "    -v\tOR\t--version" << endl
    << "    Print version number" << endl;
    cout << endl
    << "    -h\tOR\t-?\tOR\t--help" << endl
    << "    Print this help message" << endl;
    cout << endl
    << "Default options file:" << endl
    << "---------------------" << endl;
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
    << "    If a default options file is found, the options in this file" << endl
    << "    will be parsed BEFORE the command-line options." << endl
    << "    Options within the default option file may be written without" << endl
    << "    the preliminary '-' or '--'." << endl
    << endl;
}

int main(int argc, char *argv[])
{
    ASFormatter formatter;
    vector<string> fileNameVector;
    vector<string> optionsVector;
    string optionsFileName = "";
    string arg;
    bool ok = true;
    bool shouldPrintHelp = false;
    bool shouldParseOptionsFile = true;

    // manage flags
    for (int i=1; i<argc; i++)
    {
        arg = string(argv[i]);
        
        if ( BEGINS_WITH(arg ,"--options=none", 14) )
        {
            TRACE( INFO, "options=none" );
            shouldParseOptionsFile = false;
        }
        else if ( BEGINS_WITH(arg ,"--options=", 10) )
        {
            TRACE( ENTRY, "options=" );
            optionsFileName = arg.substr(strlen("--options="));
            TRACE( EXIT, "options=" << optionsFileName );
        }
        else if ( (arg == "-h") || (arg == "--help") || (arg == "-?") )
        {
            TRACE( INFO, "help" );
            shouldPrintHelp = true;
        }
        else if (arg[0] == '-')
        {
            TRACE( INFO, "option: " << arg );
            optionsVector.push_back(arg);
        }
        else // file-name
        {
            TRACE( INFO, "source: " << arg );
            fileNameVector.push_back(arg);
        }
    }

    // parse options file
    if (shouldParseOptionsFile)
    {
        TRACE( INFO, "Options file should be read..." );
        if (optionsFileName.empty())
        {
            char* env = getenv("ARTISTIC_STYLE_OPTIONS");
            if (env != NULL)
                optionsFileName = string(env);
            TRACE( INFO, "Taken filename '" << optionsFileName << "' from $ARTISTIC_STYLE_OPTIONS." );
        }
        if (optionsFileName.empty())
        {
            char* env = getenv("HOME");
            if (env != NULL)
                optionsFileName = string(env) + string("/.astylerc");
            TRACE( INFO, "Assembled filename '" << optionsFileName << "' from $HOME/.astylerc." );
        }
        if (optionsFileName.empty())
        {
            char* drive = getenv("HOMEDRIVE");
            char* path = getenv("HOMEPATH");
            if (path != NULL)
                optionsFileName = string(drive) + string(path) + string("/.astylerc");
            TRACE( INFO, "Assembled filename '" << optionsFileName << "' from %HOMEDRIVE%%HOMEPATH%/.astylerc." );
        }

        if (!optionsFileName.empty())
        {
            ifstream optionsIn(optionsFileName.c_str());
            TRACE( INFO, "Reading options file " << optionsFileName );
            if (optionsIn)
            {
                vector<string> fileOptionsVector;
                // reading (whitespace seperated) strings from file into string vector
                string buffer;
                while (optionsIn)
                {
                    getline(optionsIn, buffer);
                    TRACE( INFO, "Read line: '" << buffer << "'" );
                    if (optionsIn.fail() || (buffer.size() == 0) || (buffer[0] == '#'))
                    {
                        TRACE( INFO, "Invalid line (EOF, empty line, or comment line)" );
                        continue;
                    }
                    istringstream buf(buffer);
                    copy(istream_iterator<string>(buf), istream_iterator<string>(), back_inserter(fileOptionsVector));
                }
                TRACE( ENTRY, "Options read:" );
#ifndef NDEBUG
                for ( unsigned int i = 0; i < fileOptionsVector.size(); ++i )
                    TRACE( INFO, fileOptionsVector[i] );
                TRACE( EXIT, "End of options." );
#endif
                ok = parseOptions(formatter,
                                  fileOptionsVector.begin(),
                                  fileOptionsVector.end(),
                                  "Unknown option in default options file: ");
            }
            else
            {
                TRACE( INFO, "Could not open options file " << optionsFileName );
            }

            optionsIn.close();
            if (!ok)
            {
                (*_err) << "For help on options, type 'astyle -h' " << endl;
            }
        }
    }
    else
    {
        TRACE( INFO, "Options file disabled." );
    }

    // parse options from command line

    ok = parseOptions(formatter,
                      optionsVector.begin(),
                      optionsVector.end(),
                      "Unknown command line option: ");
    if (!ok)
    {
        (*_err) << "For help on options, type 'astyle -h' " << endl;
        exit(1);
    }

    if (shouldPrintHelp)
    {
        printHelp();
        return 1;
    }

    // if no files have been given, use cin for input and cout for output
    if (fileNameVector.empty())
    {
        formatter.init( cin );

        while (formatter.hasMoreLines() )
        {
            cout << formatter.nextLine();
            if (formatter.hasMoreLines())
                cout << endl;
        }
        cout.flush();
    }
    else
    {
        // indent the given files
        for (unsigned i=0; i<fileNameVector.size(); i++)
        {
            string originalFileName = fileNameVector[i];
            string inFileName = originalFileName + _suffix;

            if ( ! isWriteable(originalFileName.c_str()) )
            {
                (*_err) << "File '" << originalFileName << "' does not exist, or is read-only." << endl;
                continue;
            }

            remove(inFileName.c_str());

            if ( rename(originalFileName.c_str(), inFileName.c_str()) < 0)
            {
                (*_err) << "Could not rename " << originalFileName << " to " << inFileName << endl;
                exit(1);
            }

            TRACE( INFO, "Processing file " << originalFileName << "..." );
            ifstream in(inFileName.c_str());
            if (!in)
            {
                (*_err) << "Could not open input file" << inFileName << endl;
                exit(1);
            }

            ofstream out(originalFileName.c_str());
            if (!out)
            {
                (*_err) << "Could not open output file" << originalFileName << endl;
                exit(1);
            }

            // Unless a specific language mode has been set, set the language mode
            // according to the file's suffix.
            if (!formatter.modeSetManually)
            {
                if (stringEndsWith(originalFileName, ".java"))
                {
                    TRACE( INFO, "Setting style=java according to filename extension on " << originalFileName );
                    formatter.sourceStyle = STYLE_JAVA;
                }
                else if (stringEndsWith(originalFileName, ".sc") || stringEndsWith(originalFileName, ".cs"))
                {
                    TRACE( INFO, "Setting style=csharp according to filename extension on " << originalFileName );
                    formatter.sourceStyle = STYLE_CSHARP;
                }
                else
                {
                    TRACE( INFO, "Setting style=c according to non-java/csharp filename extension on " << originalFileName );
                    formatter.sourceStyle = STYLE_C;
                }
            }

            formatter.init( in );
            while (formatter.hasMoreLines() )
            {
                out << formatter.nextLine();
                if (formatter.hasMoreLines())
                    out << endl;
            }

            out.flush();
            out.close();

            in.close();
            if ( ! shouldBackupFile )
            {
                TRACE( INFO, "Removing backup file as requested..." );
                remove( inFileName.c_str() );
            }
        }
    }
    return 0;
}

