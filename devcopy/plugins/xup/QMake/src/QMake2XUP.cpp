#include "QMake2XUP.h"
#include "QMakeProjectItem.h"

'''*************************
WARNING :
si "operator" n'existe pas, vaut "="
si "multiline" n'existe pas, vaut "False"
si "nested" n'existe pas, vaut "False"
*************************'''

#include <QApplication>
#include <QtCore>
#include <QtGui>
#include <QtXml>
#include <QTextCodec>

#include <pMonkeyStudio.h>

#include <exception>

class MksException : public std.exception
public:
    MksException( QString p_s ) throw()
        s = p_s

    virtual ~MksException() throw()    virtual  char* what()  throw()
        return s.toLocal8Bit().constData()

private:
    QString s


 mQMakeEditor = "QMake"

def tabsString(self, i ):
    return QString().fill( '\t', i )


def MyEscape(self, b ):
    return Qt.escape( b ).replace( "\"" , "&quot;" )


def convertFromPro(self, s, codec ):
    # check if file exists
    if  not QFile.exists( s ) :
        return QString()

    QFile f( s )
    if  not f.open( QIODevice.ReadOnly | QIODevice.Text ) :
        return QString()
    data = QTextCodec.codecForName( codec.toUtf8() ).toUnicode( f.readAll() )

    QVector<QString> temp_v = data.split( '\n' ).toVector()
    QVector<QString> v
    for b in temp_v:
    {# used to trim the vector's data
        v.append(b.trimmed())

    QStack<bool> isNested
    QStack<QString> pile
    QString file
    QString inVarComment
    nbEmptyLine = 0

    QRegExp Variable("^(?:((?:[-\\.a-zA-Z0-9*not _|+]+(?:\\((?:.*)\\))?[ \\t]*[:|][ \\t]*)+)?([\\.a-zA-Z0-9*not _]+))[ \\t]*([*+-]?=)[ \\t]*((?:\\\\'|\\\\\\$|\\\\\\\\\\\\\\\"|\\\\\\\"|[^#])+)?[ \\t]*(#.*)?")
    QRegExp RegexVar("^(?:((?:[-\\.a-zA-Z0-9*not _|+]+(?:\\((?:.*)\\))?[ \\t]*[:|][ \\t]*)+)?([\\.a-zA-Z0-9*not _]+))[ \\t]*~=([^#]+)(#.*)?")
    #QRegExp bloc("^(\\})?[ \\t]*((?:(?:[-\\.a-zA-Z0-9*|_not +]+(?:\\((?:[^\\)]*)\\))?[ \\t]*[:|][ \\t]*)+)?([-a-zA-Z0-9*|_not +]+(?:\\((?:[^\\)]*)\\))?))[ \\t]*(\\{)[ \\t]*(#.*)?")
    QRegExp bloc("^(\\})?[ \\t]*((?:(?:[-\\.a-zA-Z0-9*|_not +]+(?:\\((?:.*)\\))?[ \\t]*[:|][ \\t]*)+)?([-\\.a-zA-Z0-9*|_not +]+(?:\\((?:.*)\\))?))[:]*[ \\t]*(\\{)[ \\t]*(#.*)?")
    QRegExp function_call("^((?:not ?[-\\.a-zA-Z0-9*not _|+]+(?:[ \\t]*\\((?:.*)\\))?[ \\t]*[|:][ \\t]*)+)?([a-zA-Z]+[ \\t]*\\((.*)\\))[ \\t]*(#.*)?")
    QRegExp end_bloc("^(\\})[ \t]*(#.*)?")
    QRegExp end_bloc_continuing("^(\\})[ \\t]*(?:((?:[-\\.a-zA-Z0-9*not _|+]+(?:\\((?:.*)\\))?[ \\t]*[:|][ \\t]*)+)?([\\.a-zA-Z0-9*not _]+))[ \\t]*([~*+-]?=)[ \\t]*((?:\\\\'|\\\\\\$|\\\\\\\\\\\\\\\"|\\\\\\\"|[^\\\\#])+)?[ \\t]*(\\\\)?[ \t]*(#.*)?")
    QRegExp comments("^#(.*)")
    QRegExp varLine("^(.*)[ \\t]*\\\\[ \\t]*(#.*)?")

     fileVariables = QMakeProjectItem.projectInfos().fileVariables( QMakeProjectItem.QMakeProject )
     pathVariables = QMakeProjectItem.projectInfos().pathVariables( QMakeProjectItem.QMakeProject )

    file.append( QString( "<not DOCTYPE XUPProject>\n<project codec=\"%1\" name=\"%2\" editor=\"%3\" expanded=\"False\">\n" ).arg( codec ).arg( QFileInfo( s ).fileName() ).arg( mQMakeEditor ) )
    try
        for (i = 0; i < v.size(); i++)
            if bloc.exactMatch(v[i]):
                QString tmp_end
                liste = bloc.capturedTexts()
                if liste[1] == "}":
                    while (not isNested.isEmpty() and isNested.top())
                        file.append(pile.pop())
                        isNested.pop()

                    # pop the last scope of the bloc
                    file.append(pile.pop())
                    isNested.pop()
                    # pop the nested scope of the bloc
                    while (not isNested.isEmpty() and isNested.top())
                        file.append(pile.pop())
                        isNested.pop()


                if liste[0].trimmed()[0] == '}':
                    liste[0] = liste[0].trimmed().right(liste[0].trimmed().length()-2)
                liste[0] = liste[0].left(liste[0].indexOf(QChar('{'))+1)
                liste2 = liste[0].split(QChar(':'),QString.SkipEmptyParts)

                for s in liste2:
                    if s[s.length()-1] == '{':
                        file.append("<scope name=\""+MyEscape(s.left(s.length()-1).trimmed())+"\""+(liste[5].trimmed() != "" ? " comment=\""+MyEscape(liste[5].trimmed())+"\"" : "")+">\n")

                    else:
                        file.append("<scope name=\""+MyEscape(s.trimmed())+"\" nested=\"True\">\n")
                        tmp_end += "</scope>\n"


                if tmp_end != "":
                    pile += tmp_end
                    isNested.push(True)

                pile += "</scope>\n"
                isNested.push(False)

            elif RegexVar.exactMatch(v[i]):
                liste = RegexVar.capturedTexts()
                # liste[1] = scopes
                # liste[2] = la variable
                # liste[3] = la ligne (ne pas oublier trimmed())
                # liste[4] = le commentaire
                file.append("<comment value=\"#"+MyEscape(liste[2])+"\" />\n")

            elif Variable.exactMatch(v[i]):
                QString tmp_end
                liste = Variable.capturedTexts()
                liste2 = liste[1].trimmed().split(QChar(':'), QString.SkipEmptyParts)
                if liste[1] == "else" or (liste2.size() > 0 and liste2[0] == "else"):
                    if isNested.size():
                        # pop the last scope of the bloc
                        file.append(pile.pop())
                        isNested.pop()
                        # pop the nested scope of the bloc
                        while (not isNested.isEmpty() and isNested.top())
                            file.append(pile.pop())
                            isNested.pop()



                else:
                    while (not isNested.isEmpty() and isNested.top())
                        file.append(pile.pop())
                        isNested.pop()


                if liste2.size() > 0:
                    for s in liste2:
                        file.append("<scope name=\""+MyEscape(s.trimmed())+"\" nested=\"True\">\n")
                        pile += "</scope>\n"
                        isNested.push(True)



                QString isMulti
                if liste[4].trimmed().endsWith("\\") or liste[4].trimmed() == "\\":
                    isMulti = " multiline=\"True\""
                    tmppp = liste[4].trimmed()
                    tmppp.chop(1)
                    liste[4] = tmppp

                theOp = (liste[3].trimmed() == "=" ? "" : " operator=\""+liste[3].trimmed()+"\"")
                file.append("<variable name=\""+MyEscape(liste[2].trimmed())+"\""+theOp+isMulti+">\n")
                isFile = fileVariables.contains(liste[2].trimmed())
                isPath = pathVariables.contains(liste[2].trimmed())
                if  isFile or isPath :
                    tmpValues = liste[4].trimmed().split(" ")
                    inStr = False
                    QStringList multivalues
                    QString ajout
                    for (ku = 0; ku < tmpValues.size(); ku++)
                        if tmpValues.value(ku).startsWith('"') :
                            inStr = True
                        if inStr:
                            if ajout != "":
                                ajout += " "
                            ajout += tmpValues.value(ku)
                            if tmpValues.value(ku).endsWith('"') :
                                multivalues += ajout
                                ajout = ""
                                inStr = False


                        else:
                            multivalues += tmpValues.value(ku)


                    for (ku = 0; ku < multivalues.size(); ku++)
                        inVarComment = multivalues.value(ku).trimmed()
                        if  inVarComment.startsWith( "#" ) :
                            if  inVarComment == "#" and ku < multivalues.size() :
                                ku++
                                inVarComment = "# " +multivalues.value(ku).trimmed()

                            file.append( QString( "<comment value=\"%1\" />\n" ).arg( QString( inVarComment ) ) )

                        else:
                            if  isFile :
                                file.append("<file"+(liste[5].trimmed() != "" and ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste[5].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n")

                            elif  isPath :
                                file.append("<path"+(liste[5].trimmed() != "" and ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste[5].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n")




                else:
                    file.append("<value"+(liste[5].trimmed() != "" ? " comment=\""+MyEscape(liste[5].trimmed())+"\"" : "")+" content=\""+MyEscape(liste[4].trimmed())+"\" />\n")
                if isMulti == " multiline=\"True\"":
                    i++
                    while (varLine.exactMatch(v[i]))
                        liste3 = varLine.capturedTexts()
                        isFile = fileVariables.contains(liste[2].trimmed())
                        isPath = pathVariables.contains(liste[2].trimmed())
                        if  isFile or isPath :
                            tmpValues = liste3[1].trimmed().split(" ")
                            multivalues = QStringList()
                            ajout = ""
                            inStr = False
                            for (ku = 0; ku < tmpValues.size(); ku++)
                                if tmpValues.value(ku).startsWith('"') :
                                    inStr = True
                                if inStr:
                                    if ajout != "":
                                        ajout += " "
                                    ajout += tmpValues.value(ku)
                                    if tmpValues.value(ku).endsWith('"') :
                                        multivalues += ajout
                                        ajout = ""
                                        inStr = False


                                else:
                                    multivalues += tmpValues.value(ku)


                            for (ku = 0; ku < multivalues.size(); ku++)
                                inVarComment = multivalues.value(ku).trimmed()
                                if  inVarComment.startsWith( "#" ) :
                                    if  inVarComment == "#" and ku < multivalues.size() :
                                        ku++
                                        inVarComment = "# " +multivalues.value(ku).trimmed()

                                    file.append( QString( "<comment value=\"%1\" />\n" ).arg( QString( inVarComment ) ) )

                                else:
                                    if  isFile :
                                        file.append("<file"+(liste3[2].trimmed() != "" and ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n")

                                    elif  isPath :
                                        file.append("<path"+(liste3[2].trimmed() != "" and ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n")




                        else:
                            file.append("<value"+(liste3[2].trimmed() != "" ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(liste3[1].trimmed())+"\" />\n")
                        i++

                    liste3 = v[i].split( "#" )
                    QString comment
                    if liste3.size() == 2:
                        comment = "#"+liste3[1]
                    isFile = fileVariables.contains(liste[2].trimmed())
                    isPath = pathVariables.contains(liste[2].trimmed())
                    if  isFile or isPath :
                        tmpValues = liste3[0].trimmed().split(" ")
                        multivalues = QStringList()
                        ajout = ""
                        inStr = False
                        for (ku = 0; ku < tmpValues.size(); ku++)
                            if tmpValues.value(ku).startsWith('"') :
                                inStr = True
                            if inStr:
                                if ajout != "":
                                    ajout += " "
                                ajout += tmpValues.value(ku)
                                if tmpValues.value(ku).endsWith('"') :
                                    multivalues += ajout
                                    ajout = ""
                                    inStr = False


                            else:
                                multivalues += tmpValues.value(ku)


                        for (ku = 0; ku < multivalues.size(); ku++)
                            inVarComment = multivalues.value(ku).trimmed()
                            if  inVarComment.startsWith( "#" ) :
                                if  inVarComment == "#" and ku < multivalues.size() :
                                    ku++
                                    inVarComment = "# " +MyEscape(multivalues.value(ku).trimmed())

                                file.append( QString( "<comment content=\"%1\" />\n" ).arg( QString( inVarComment ) ) )

                            else:
                                if  isFile :
                                    file.append("<file"+(comment.trimmed() != "" and ku+1 == multivalues.size() ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n")

                                elif  isPath :
                                    file.append("<path"+(comment.trimmed() != "" and ku+1 == multivalues.size() ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n")




                    else:
                        file.append("<value"+(comment.trimmed() != "" ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(liste3[0].trimmed())+"\" />\n")

                file.append("</variable>\n")

            elif function_call.exactMatch(v[i]):
                QString tmp_end
                liste = function_call.capturedTexts()
                liste2 = liste[1].split(QChar(':'),QString.SkipEmptyParts)
                for s in liste2:
                    file.append("<scope name=\""+MyEscape(s.trimmed())+"\" nested=\"True\">\n")
                    tmp_end += "</scope>\n"

                explode_params = liste[2].split("(")
                func_name = explode_params[0].trimmed()
                QString params
                if explode_params.size() > 2:
                    params = explode_params.join("(")
                else:
                    params = explode_params[1]
                params = params.trimmed(); # to be sure that the last char is the last ")"
                params.chop(1); # pop the last ")"
                params = params.trimmed(); # to pop off the ending spaces
                file.append("<function"+(liste[4].trimmed() != "" ? " comment=\""+MyEscape(liste[4].trimmed())+"\"" : "")+" name=\""+MyEscape(func_name)+"\" parameters=\""+MyEscape(params)+"\" />\n")
                file.append(tmp_end)

            elif end_bloc_continuing.exactMatch(v[i]):
                liste = end_bloc_continuing.capturedTexts()
                while (not isNested.isEmpty() and isNested.top())
                    file.append(pile.pop())
                    isNested.pop()

                # pop the last scope of the bloc
                file.append(pile.pop())
                isNested.pop()
                # pop the nested scope of the bloc
                while (not isNested.isEmpty() and isNested.top())
                    file.append(pile.pop())
                    isNested.pop()


                liste2 = liste[2].split(QChar(':'),QString.SkipEmptyParts)
                for s in liste2:
                    file.append("<scope name=\""+MyEscape(s.trimmed())+"\" nested=\"True\">\n")
                    pile += "</scope>\n"
                    isNested.push(True)

                isMulti = (liste[6].trimmed() == "\\" ? " multiline=\"True\"" : "")
                theOp = (liste[4].trimmed() == "=" ? "" : " operator=\""+liste[4].trimmed()+"\"")
                file.append("<variable name=\""+MyEscape(liste[3].trimmed())+"\""+theOp+">\n")
                if  liste[7].trimmed().startsWith( "#" ) :
                    file.append( QString( "<comment value=\"%1\" />\n" ).arg( QString( liste[7].trimmed() ) ) )
                else:
                    file.append("<value"+(liste[7].trimmed() != "" ? " comment=\""+MyEscape(liste[7].trimmed())+"\"" : "")+" content=\""+MyEscape(liste[5].trimmed())+"\" />\n")
                if isMulti == " multiline=\"True\"":
                    i++
                    while (varLine.exactMatch(v[i]))
                        liste3 = varLine.capturedTexts()
                        isFile = fileVariables.contains(liste[2].trimmed())
                        isPath = pathVariables.contains(liste[2].trimmed())
                        if  isFile or isPath :
                            tmpValues = liste3[1].trimmed().split(" ")
                            multivalues = QStringList()
                            ajout = ""
                            inStr = False
                            for (ku = 0; ku < tmpValues.size(); ku++)
                                if tmpValues.value(ku).startsWith('"') :
                                    inStr = True
                                if inStr:
                                    if ajout != "":
                                        ajout += " "
                                    ajout += tmpValues.value(ku)
                                    if tmpValues.value(ku).endsWith('"') :
                                        multivalues += ajout
                                        ajout = ""
                                        inStr = False


                                else:
                                    multivalues += tmpValues.value(ku)


                            for (ku = 0; ku < multivalues.size(); ku++)
                                inVarComment = multivalues.value(ku).trimmed()
                                if  inVarComment.startsWith( "#" ) :
                                    if  inVarComment == "#" and ku < multivalues.size() :
                                        ku++
                                        inVarComment = "# " +multivalues.value(ku).trimmed()

                                    file.append( QString( "<comment value=\"%1\" />\n" ).arg( QString( inVarComment ) ) )

                                else:
                                    if  isFile :
                                        file.append("<file"+(liste3[2].trimmed() != "" and ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n")

                                    elif  isPath :
                                        file.append("<path"+(liste3[2].trimmed() != "" and ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n")




                        else:
                            file.append("<value"+(liste3[2].trimmed() != "" ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(liste3[1].trimmed())+"\" />\n")
                        i++

                    liste3 = v[i].split( "#" )
                    QString comment
                    if liste3.size() == 2:
                        comment = "#"+liste3[1]
                    isFile = fileVariables.contains(liste[2].trimmed())
                    isPath = pathVariables.contains(liste[2].trimmed())
                    if  isFile or isPath :
                        tmpValues = liste3[0].trimmed().split(" ")
                        multivalues = QStringList()
                        ajout = ""
                        inStr = False
                        for (ku = 0; ku < tmpValues.size(); ku++)
                            if tmpValues.value(ku).startsWith('"') :
                                inStr = True
                            if inStr:
                                if ajout != "":
                                    ajout += " "
                                ajout += tmpValues.value(ku)
                                if tmpValues.value(ku).endsWith('"') :
                                    multivalues += ajout
                                    ajout = ""
                                    inStr = False


                            else:
                                multivalues += tmpValues.value(ku)


                        for (ku = 0; ku < multivalues.size(); ku++)
                            inVarComment = multivalues.value(ku).trimmed()
                            if  inVarComment.startsWith( "#" ) :
                                if  inVarComment == "#" and ku < multivalues.size() :
                                    ku++
                                    inVarComment = "# " +MyEscape(multivalues.value(ku).trimmed())

                                file.append( QString( "<comment content=\"%1\" />\n" ).arg( QString( inVarComment ) ) )

                            else:
                                if  isFile :
                                    file.append("<file"+(comment.trimmed() != "" and ku+1 == multivalues.size() ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n")

                                elif  isPath :
                                    file.append("<path"+(comment.trimmed() != "" and ku+1 == multivalues.size() ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n")




                    else:
                        file.append("<value"+(comment.trimmed() != "" ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(liste3[0].trimmed())+"\" />\n")

                file.append("</variable>\n")

            elif end_bloc.exactMatch(v[i]):
                while (not isNested.isEmpty() and isNested.top())
                    isNested.top()
                    file.append(pile.pop())
                    isNested.pop()

                isNested.top()
                file.append(pile.pop())
                isNested.pop()
                if not isNested.isEmpty() and isNested.top():
                    isNested.top()
                    file.append(pile.pop())
                    isNested.pop()


            elif comments.exactMatch(v[i]):
                liste = comments.capturedTexts()
                file.append("<comment value=\"#"+MyEscape(liste[1])+"\" />\n")

            elif v[i] == "":
                nbEmptyLine++
                while (not isNested.isEmpty() and isNested.top())
                    file.append(pile.pop())
                    isNested.pop()

                if i+1 < v.size():
                    if v[i+1] != "":
                        file.append("<emptyline count=\""+QString.number(nbEmptyLine)+"\" />\n")
                        nbEmptyLine = 0


                else:
                    file.append("<emptyline count=\""+QString.number(nbEmptyLine)+"\" />\n")

            else:
                qWarning( "%s didn't match", v[i].toLocal8Bit().constData())
                throw MksException( QString("Erreur parsing project file: %1").arg( s ) )


        while (not isNested.isEmpty() and isNested.top())
            file.append(pile.pop())
            isNested.pop()


    catch ( std.exception & e)
        # re-init the XML output
        file.append( QString( "<not DOCTYPE XUPProject>\n<project codec=\"%1\" name=\"%2\" editor=\"%3\" expanded=\"False\">\n" ).arg( codec ).arg( QFileInfo( s ).fileName() ).arg( mQMakeEditor ) )
        # empty both stacks
        isNested.clear()
        pile.clear()
        qWarning("%s", e.what() )


    file.append( "</project>\n" )
    # to output the xml in a file
    '''QFile apt(s+".xml")
    if  apt.open( QIODevice.WriteOnly | QIODevice.Text ) :
        apt.write(file.toAscii())
        apt.close()
    }'''

    return file


QString convertNodeToPro(  QDomElement& element, EOL = pMonkeyStudio.getEol() )
    static tabs = 0; # tabs indentation
    static isMultiline = False; # tell if last variable is multiline or not
    isNested = False; # tell if scope is nested or not
    QString comment; # comment of item if available
    QString data; # the data to return
     tag = element.tagName(); # current node tag name

    if  tag != "project" :
        if  tag == "function" :
            function = QString( "%1( %2 )" ).arg( element.attribute( "name" ) ).arg( element.attribute( "parameters" ) )
            comment = element.attribute( "comment" )

            data.append( tabsString( tabs ) +function )

            if  not comment.isEmpty() :
                data.append( ' ' +comment )


            data.append( EOL )

        elif  tag == "emptyline" :
            count = element.attribute( "count" ).toInt()

            for ( i = 0; i < count; i++ )
                data.append( EOL )


        elif  tag == "variable" :
            vtabs = tabs
            parentElement = element.parentNode().toElement()
            variable = QString( "%1\t%2 " ).arg( element.attribute( "name" ) ).arg( element.attribute( "operator", "=" ) )
            isMultiline = QVariant( element.attribute( "multiline", "False" ) ).toBool()

            if  parentElement.tagName() == "scope" and QVariant( parentElement.attribute( "nested", "False" ) ).toBool() :
                vtabs--


            data.append( tabsString( vtabs ) +variable )

        elif  tag == "value" or tag == "file" or tag == "path" :
            vtabs = tabs
            value = element.attribute( "content" )
            comment = element.attribute( "comment" )

            if  not element.previousSibling().isNull() and isMultiline :
                vtabs++

            elif  element.previousSibling().isNull() or not isMultiline :
                vtabs = 0


            data.append( tabsString( vtabs ) +value )

            if  isMultiline :
                if  not element.nextSibling().isNull() :
                    data.append( " \\" )


                if  not comment.isEmpty() :
                    data.append( ' ' +comment )


                data.append( EOL )

            elif  element.nextSibling().isNull() :
                if  not comment.isEmpty() :
                    data.append( ' ' +comment )


                data.append( EOL )

            else:
                data.append( ' ' )


        elif  tag == "scope" :
            vtabs = tabs
            parentElement = element.parentNode().toElement()
            isNested = QVariant( element.attribute( "nested", "False" ) ).toBool()
            comment = element.attribute( "comment" )
            name = element.attribute( "name" )

            if ( ( element.attribute( "name" ) == "else" and not QVariant( element.previousSibling().toElement().attribute( "nested", "False" ) ).toBool() ) or
                    ( parentElement.tagName() == "scope" and QVariant( parentElement.attribute( "nested", "False" ) ).toBool() ) )
                vtabs = 0


            data.append( tabsString( vtabs ) +name )

            if  not isNested :
                data.append( " {" )

                if  not comment.isEmpty() :
                    data.append( ' ' +comment )


                data.append( EOL )
                tabs++

            else:
                data.append( ':' )


        elif  tag == "comment" :
            vtabs = tabs
            cmt = element.attribute( "value" )

            if  element.parentNode().toElement().tagName() == "variable" and isMultiline :
                vtabs++


            data.append( tabsString( vtabs ) +cmt +EOL )


    else:
        tabs = 0


     containers = QStringList() << "function" << "emptyline" << "value" << "file" << "path" << "comment"

    if  element.hasChildNodes() and not containers.contains( tag ) :
        nodes = element.childNodes()

        for ( i = 0; i < nodes.count(); i++ )
            data.append( convertNodeToPro( nodes.at( i ).toElement(), EOL ) )


        if  tag == "scope" and not isNested :
            tabs--
            childElement = element.nextSibling().toElement()

            data.append( tabsString( tabs ) +"}" )

            if  not ( childElement.tagName() == "scope" and childElement.attribute( "name" ) == "else" ) :
                data.append( EOL )

            else:
                data.append( ' ' )




    return data


def convertToPro(self, document ):
    # get project node
    element = document.firstChildElement( "project" ).toElement()

    # check project available
    if  element.isNull() :
        return QString.null


    # parse project scope
    contents = convertNodeToPro( element )

    # remove last eol
    if  contents.length() > 0 :
        contents.chop( 1 )


    # return buffer
    return contents

