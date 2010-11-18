#include "QMake2XUP.h"
#include "QMakeProjectItem.h"

/**************************
WARNING :
si "operator" n'existe pas, il vaut "="
si "multiline" n'existe pas, il vaut "false"
si "nested" n'existe pas, il vaut "false"
**************************/

#include <QApplication>
#include <QtCore>
#include <QtGui>
#include <QtXml>
#include <QTextCodec>

#include <pMonkeyStudio.h>

#include <exception>

class MksException : public std::exception
{
public:
	MksException( QString p_s ) throw()
	{
		s = p_s;
	};
	virtual ~MksException() throw() {};
	virtual const char* what() const throw()
	{
		return s.toLocal8Bit().constData();
	};
private:
	QString s;
};

const QString mQMakeEditor = "QMake";

QString tabsString( int i )
{ return QString().fill( '\t', i ); }

QString MyEscape( QString b )
{ return Qt::escape( b ).replace( "\"" , "&quot;" ); }

QString QMake2XUP::convertFromPro( const QString& s, const QString& codec )
{
	// check if file exists
	if ( !QFile::exists( s ) )
		return QString();
	
	QFile f( s );
	if( !f.open( QIODevice::ReadOnly | QIODevice::Text ) )
		return QString();
	QString data = QTextCodec::codecForName( codec.toUtf8() )->toUnicode( f.readAll() );
	
	QVector<QString> temp_v = data.split( '\n' ).toVector();
	QVector<QString> v;
	foreach(QString b,temp_v)
	{// used to trim the vector's data
		v.append(b.trimmed());
	}
	QStack<bool> isNested;
	QStack<QString> pile;
	QString file;
	QString inVarComment;
	int nbEmptyLine = 0;
	
	QRegExp Variable("^(?:((?:[-\\.a-zA-Z0-9*!_|+]+(?:\\((?:.*)\\))?[ \\t]*[:|][ \\t]*)+)?([\\.a-zA-Z0-9*!_]+))[ \\t]*([*+-]?=)[ \\t]*((?:\\\\'|\\\\\\$|\\\\\\\\\\\\\\\"|\\\\\\\"|[^#])+)?[ \\t]*(#.*)?");
	QRegExp RegexVar("^(?:((?:[-\\.a-zA-Z0-9*!_|+]+(?:\\((?:.*)\\))?[ \\t]*[:|][ \\t]*)+)?([\\.a-zA-Z0-9*!_]+))[ \\t]*~=([^#]+)(#.*)?");
	//QRegExp bloc("^(\\})?[ \\t]*((?:(?:[-\\.a-zA-Z0-9*|_!+]+(?:\\((?:[^\\)]*)\\))?[ \\t]*[:|][ \\t]*)+)?([-a-zA-Z0-9*|_!+]+(?:\\((?:[^\\)]*)\\))?))[ \\t]*(\\{)[ \\t]*(#.*)?");
	QRegExp bloc("^(\\})?[ \\t]*((?:(?:[-\\.a-zA-Z0-9*|_!+]+(?:\\((?:.*)\\))?[ \\t]*[:|][ \\t]*)+)?([-\\.a-zA-Z0-9*|_!+]+(?:\\((?:.*)\\))?))[:]*[ \\t]*(\\{)[ \\t]*(#.*)?");
	QRegExp function_call("^((?:!?[-\\.a-zA-Z0-9*!_|+]+(?:[ \\t]*\\((?:.*)\\))?[ \\t]*[|:][ \\t]*)+)?([a-zA-Z]+[ \\t]*\\((.*)\\))[ \\t]*(#.*)?");
	QRegExp end_bloc("^(\\})[ \t]*(#.*)?");
	QRegExp end_bloc_continuing("^(\\})[ \\t]*(?:((?:[-\\.a-zA-Z0-9*!_|+]+(?:\\((?:.*)\\))?[ \\t]*[:|][ \\t]*)+)?([\\.a-zA-Z0-9*!_]+))[ \\t]*([~*+-]?=)[ \\t]*((?:\\\\'|\\\\\\$|\\\\\\\\\\\\\\\"|\\\\\\\"|[^\\\\#])+)?[ \\t]*(\\\\)?[ \t]*(#.*)?");
	QRegExp comments("^#(.*)");
	QRegExp varLine("^(.*)[ \\t]*\\\\[ \\t]*(#.*)?");
	
	const QStringList fileVariables = QMakeProjectItem::projectInfos()->fileVariables( QMakeProjectItem::QMakeProject );
	const QStringList pathVariables = QMakeProjectItem::projectInfos()->pathVariables( QMakeProjectItem::QMakeProject );
	
	file.append( QString( "<!DOCTYPE XUPProject>\n<project codec=\"%1\" name=\"%2\" editor=\"%3\" expanded=\"false\">\n" ).arg( codec ).arg( QFileInfo( s ).fileName() ).arg( mQMakeEditor ) );
	try
	{
		for(int i = 0;i < v.size();i++)
		{
			if(bloc.exactMatch(v[i]))
			{
				QString tmp_end;
				QStringList liste = bloc.capturedTexts();
				if(liste[1] == "}")
				{
					while(!isNested.isEmpty() && isNested.top())
					{
						file.append(pile.pop());
						isNested.pop();
					}
					// pop the last scope of the bloc
					file.append(pile.pop());
					isNested.pop();
					// pop the nested scope of the bloc
					while(!isNested.isEmpty() && isNested.top())
					{
						file.append(pile.pop());
						isNested.pop();
					}
				}
				if(liste[0].trimmed()[0] == '}')
					liste[0] = liste[0].trimmed().right(liste[0].trimmed().length()-2);
				liste[0] = liste[0].left(liste[0].indexOf(QChar('{'))+1);
				QStringList liste2 = liste[0].split(QChar(':'),QString::SkipEmptyParts);
				
				foreach(QString s,liste2)
				{
					if(s[s.length()-1] == '{')
					{
						file.append("<scope name=\""+MyEscape(s.left(s.length()-1).trimmed())+"\""+(liste[5].trimmed() != "" ? " comment=\""+MyEscape(liste[5].trimmed())+"\"" : "")+">\n");
					}
					else
					{
						file.append("<scope name=\""+MyEscape(s.trimmed())+"\" nested=\"true\">\n");
						tmp_end += "</scope>\n";
					}
				}
				if(tmp_end != "")
				{
					pile += tmp_end;
					isNested.push(true);
				}
				pile += "</scope>\n";
				isNested.push(false);
			}
			else if(RegexVar.exactMatch(v[i]))
			{
				QStringList liste = RegexVar.capturedTexts();
				// liste[1] = scopes
				// liste[2] = la variable
				// liste[3] = la ligne (ne pas oublier trimmed())
				// liste[4] = le commentaire
				file.append("<comment value=\"#"+MyEscape(liste[2])+"\" />\n");
			}
			else if(Variable.exactMatch(v[i]))
			{
				QString tmp_end;
				QStringList liste = Variable.capturedTexts();
				QStringList liste2 = liste[1].trimmed().split(QChar(':'), QString::SkipEmptyParts);
				if(liste[1] == "else" || (liste2.size() > 0 && liste2[0] == "else"))
				{
					if(isNested.size())
					{
						// pop the last scope of the bloc
						file.append(pile.pop());
						isNested.pop();
						// pop the nested scope of the bloc
						while(!isNested.isEmpty() && isNested.top())
						{
							file.append(pile.pop());
							isNested.pop();
						}
					}
				}
				else
				{
					while(!isNested.isEmpty() && isNested.top())
					{
						file.append(pile.pop());
						isNested.pop();
					}
				}
				if(liste2.size() > 0)
				{
					foreach(QString s,liste2)
					{
						file.append("<scope name=\""+MyEscape(s.trimmed())+"\" nested=\"true\">\n");
						pile += "</scope>\n";
						isNested.push(true);
					}
				}
				
				QString isMulti;
				if(liste[4].trimmed().endsWith("\\") || liste[4].trimmed() == "\\")
				{
					isMulti = " multiline=\"true\"";
					QString tmppp = liste[4].trimmed();
					tmppp.chop(1);
					liste[4] = tmppp;
				}
				QString theOp = (liste[3].trimmed() == "=" ? "" : " operator=\""+liste[3].trimmed()+"\"");
				file.append("<variable name=\""+MyEscape(liste[2].trimmed())+"\""+theOp+isMulti+">\n");
				bool isFile = fileVariables.contains(liste[2].trimmed());
				bool isPath = pathVariables.contains(liste[2].trimmed());
				if ( isFile || isPath )
				{
					QStringList tmpValues = liste[4].trimmed().split(" ");
					bool inStr = false;
					QStringList multivalues;
					QString ajout;
					for(int ku = 0;ku < tmpValues.size();ku++)
					{
						if(tmpValues.value(ku).startsWith('"') )
							inStr = true;
						if(inStr)
						{
							if(ajout != "")
								ajout += " ";
							ajout += tmpValues.value(ku);
							if(tmpValues.value(ku).endsWith('"') )
							{
								multivalues += ajout;
								ajout = "";
								inStr = false;
							}
						}
						else
						{
							multivalues += tmpValues.value(ku);
						}
					}
					for(int ku = 0;ku < multivalues.size();ku++)
					{
						inVarComment = multivalues.value(ku).trimmed();
						if ( inVarComment.startsWith( "#" ) )
						{
							if ( inVarComment == "#" && ku < multivalues.size() )
							{
								ku++;
								inVarComment = "# " +multivalues.value(ku).trimmed();
							}
							file.append( QString( "<comment value=\"%1\" />\n" ).arg( QString( inVarComment ) ) );
						}
						else
						{
							if ( isFile )
							{
								file.append("<file"+(liste[5].trimmed() != "" && ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste[5].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n");
							}
							else if ( isPath )
							{
								file.append("<path"+(liste[5].trimmed() != "" && ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste[5].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n");
							}
						}
					}
				}
				else
					file.append("<value"+(liste[5].trimmed() != "" ? " comment=\""+MyEscape(liste[5].trimmed())+"\"" : "")+" content=\""+MyEscape(liste[4].trimmed())+"\" />\n");
				if(isMulti == " multiline=\"true\"")
				{
					i++;
					while(varLine.exactMatch(v[i]))
					{
						QStringList liste3 = varLine.capturedTexts();
						bool isFile = fileVariables.contains(liste[2].trimmed());
						bool isPath = pathVariables.contains(liste[2].trimmed());
						if ( isFile || isPath )
						{
							QStringList tmpValues = liste3[1].trimmed().split(" ");
							QStringList multivalues = QStringList();
							QString ajout = "";
							bool inStr = false;
							for(int ku = 0;ku < tmpValues.size();ku++)
							{
								if(tmpValues.value(ku).startsWith('"') )
									inStr = true;
								if(inStr)
								{
									if(ajout != "")
										ajout += " ";
									ajout += tmpValues.value(ku);
									if(tmpValues.value(ku).endsWith('"') )
									{
										multivalues += ajout;
										ajout = "";
										inStr = false;
									}
								}
								else
								{
									multivalues += tmpValues.value(ku);
								}
							}
							for(int ku = 0;ku < multivalues.size();ku++)
							{
								inVarComment = multivalues.value(ku).trimmed();
								if ( inVarComment.startsWith( "#" ) )
								{
									if ( inVarComment == "#" && ku < multivalues.size() )
									{
										ku++;
										inVarComment = "# " +multivalues.value(ku).trimmed();
									}
									file.append( QString( "<comment value=\"%1\" />\n" ).arg( QString( inVarComment ) ) );
								}
								else
								{
									if ( isFile )
									{
										file.append("<file"+(liste3[2].trimmed() != "" && ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n");
									}
									else if ( isPath )
									{
										file.append("<path"+(liste3[2].trimmed() != "" && ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n");
									}
								}
							}
						}
						else
							file.append("<value"+(liste3[2].trimmed() != "" ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(liste3[1].trimmed())+"\" />\n");
						i++;
					}
					QStringList liste3 = v[i].split( "#" );
					QString comment;
					if(liste3.size() == 2)
						comment = "#"+liste3[1];
					bool isFile = fileVariables.contains(liste[2].trimmed());
					bool isPath = pathVariables.contains(liste[2].trimmed());
					if ( isFile || isPath )
					{
						QStringList tmpValues = liste3[0].trimmed().split(" ");
						QStringList multivalues = QStringList();
						QString ajout = "";
						bool inStr = false;
						for(int ku = 0;ku < tmpValues.size();ku++)
						{
							if(tmpValues.value(ku).startsWith('"') )
								inStr = true;
							if(inStr)
							{
								if(ajout != "")
									ajout += " ";
								ajout += tmpValues.value(ku);
								if(tmpValues.value(ku).endsWith('"') )
								{
									multivalues += ajout;
									ajout = "";
									inStr = false;
								}
							}
							else
							{
								multivalues += tmpValues.value(ku);
							}
						}
						for(int ku = 0;ku < multivalues.size();ku++)
						{
							inVarComment = multivalues.value(ku).trimmed();
							if ( inVarComment.startsWith( "#" ) )
							{
								if ( inVarComment == "#" && ku < multivalues.size() )
								{
									ku++;
									inVarComment = "# " +MyEscape(multivalues.value(ku).trimmed());
								}
								file.append( QString( "<comment content=\"%1\" />\n" ).arg( QString( inVarComment ) ) );
							}
							else
							{
								if ( isFile )
								{
									file.append("<file"+(comment.trimmed() != "" && ku+1 == multivalues.size() ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n");
								}
								else if ( isPath )
								{
									file.append("<path"+(comment.trimmed() != "" && ku+1 == multivalues.size() ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n");
								}
							}
						}
					}
					else
						file.append("<value"+(comment.trimmed() != "" ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(liste3[0].trimmed())+"\" />\n");
				}
				file.append("</variable>\n");
			}
			else if(function_call.exactMatch(v[i]))
			{
				QString tmp_end;
				QStringList liste = function_call.capturedTexts();
				QStringList liste2 = liste[1].split(QChar(':'),QString::SkipEmptyParts);
				foreach(QString s,liste2)
				{
					file.append("<scope name=\""+MyEscape(s.trimmed())+"\" nested=\"true\">\n");
					tmp_end += "</scope>\n";
				}
				QStringList explode_params = liste[2].split("(");
				QString func_name = explode_params[0].trimmed();
				QString params;
				if(explode_params.size() > 2)
					params = explode_params.join("(");
				else
					params = explode_params[1];
				params = params.trimmed(); // to be sure that the last char is the last ")"
				params.chop(1); // pop the last ")"
				params = params.trimmed(); // to pop off the ending spaces
				file.append("<function"+(liste[4].trimmed() != "" ? " comment=\""+MyEscape(liste[4].trimmed())+"\"" : "")+" name=\""+MyEscape(func_name)+"\" parameters=\""+MyEscape(params)+"\" />\n");
				file.append(tmp_end);
			}
			else if(end_bloc_continuing.exactMatch(v[i]))
			{
				QStringList liste = end_bloc_continuing.capturedTexts();
				while(!isNested.isEmpty() && isNested.top())
				{
					file.append(pile.pop());
					isNested.pop();
				}
				// pop the last scope of the bloc
				file.append(pile.pop());
				isNested.pop();
				// pop the nested scope of the bloc
				while(!isNested.isEmpty() && isNested.top())
				{
					file.append(pile.pop());
					isNested.pop();
				}
				
				QStringList liste2 = liste[2].split(QChar(':'),QString::SkipEmptyParts);
				foreach(QString s,liste2)
				{
					file.append("<scope name=\""+MyEscape(s.trimmed())+"\" nested=\"true\">\n");
					pile += "</scope>\n";
					isNested.push(true);
				}
				QString isMulti = (liste[6].trimmed() == "\\" ? " multiline=\"true\"" : "");
				QString theOp = (liste[4].trimmed() == "=" ? "" : " operator=\""+liste[4].trimmed()+"\"");
				file.append("<variable name=\""+MyEscape(liste[3].trimmed())+"\""+theOp+">\n");
				if ( liste[7].trimmed().startsWith( "#" ) )
					file.append( QString( "<comment value=\"%1\" />\n" ).arg( QString( liste[7].trimmed() ) ) );
				else
					file.append("<value"+(liste[7].trimmed() != "" ? " comment=\""+MyEscape(liste[7].trimmed())+"\"" : "")+" content=\""+MyEscape(liste[5].trimmed())+"\" />\n");
				if(isMulti == " multiline=\"true\"")
				{
					i++;
					while(varLine.exactMatch(v[i]))
					{
						QStringList liste3 = varLine.capturedTexts();
						bool isFile = fileVariables.contains(liste[2].trimmed());
						bool isPath = pathVariables.contains(liste[2].trimmed());
						if ( isFile || isPath )
						{
							QStringList tmpValues = liste3[1].trimmed().split(" ");
							QStringList multivalues = QStringList();
							QString ajout = "";
							bool inStr = false;
							for(int ku = 0;ku < tmpValues.size();ku++)
							{
								if(tmpValues.value(ku).startsWith('"') )
									inStr = true;
								if(inStr)
								{
									if(ajout != "")
										ajout += " ";
									ajout += tmpValues.value(ku);
									if(tmpValues.value(ku).endsWith('"') )
									{
										multivalues += ajout;
										ajout = "";
										inStr = false;
									}
								}
								else
								{
									multivalues += tmpValues.value(ku);
								}
							}
							for(int ku = 0;ku < multivalues.size();ku++)
							{
								inVarComment = multivalues.value(ku).trimmed();
								if ( inVarComment.startsWith( "#" ) )
								{
									if ( inVarComment == "#" && ku < multivalues.size() )
									{
										ku++;
										inVarComment = "# " +multivalues.value(ku).trimmed();
									}
									file.append( QString( "<comment value=\"%1\" />\n" ).arg( QString( inVarComment ) ) );
								}
								else
								{
									if ( isFile )
									{
										file.append("<file"+(liste3[2].trimmed() != "" && ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n");
									}
									else if ( isPath )
									{
										file.append("<path"+(liste3[2].trimmed() != "" && ku+1 == multivalues.size() ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n");
									}
								}
							}
						}
						else
							file.append("<value"+(liste3[2].trimmed() != "" ? " comment=\""+MyEscape(liste3[2].trimmed())+"\"" : "")+" content=\""+MyEscape(liste3[1].trimmed())+"\" />\n");
						i++;
					}
					QStringList liste3 = v[i].split( "#" );
					QString comment;
					if(liste3.size() == 2)
						comment = "#"+liste3[1];
					bool isFile = fileVariables.contains(liste[2].trimmed());
					bool isPath = pathVariables.contains(liste[2].trimmed());
					if ( isFile || isPath )
					{
						QStringList tmpValues = liste3[0].trimmed().split(" ");
						QStringList multivalues = QStringList();
						QString ajout = "";
						bool inStr = false;
						for(int ku = 0;ku < tmpValues.size();ku++)
						{
							if(tmpValues.value(ku).startsWith('"') )
								inStr = true;
							if(inStr)
							{
								if(ajout != "")
									ajout += " ";
								ajout += tmpValues.value(ku);
								if(tmpValues.value(ku).endsWith('"') )
								{
									multivalues += ajout;
									ajout = "";
									inStr = false;
								}
							}
							else
							{
								multivalues += tmpValues.value(ku);
							}
						}
						for(int ku = 0;ku < multivalues.size();ku++)
						{
							inVarComment = multivalues.value(ku).trimmed();
							if ( inVarComment.startsWith( "#" ) )
							{
								if ( inVarComment == "#" && ku < multivalues.size() )
								{
									ku++;
									inVarComment = "# " +MyEscape(multivalues.value(ku).trimmed());
								}
								file.append( QString( "<comment content=\"%1\" />\n" ).arg( QString( inVarComment ) ) );
							}
							else
							{
								if ( isFile )
								{
									file.append("<file"+(comment.trimmed() != "" && ku+1 == multivalues.size() ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n");
								}
								else if ( isPath )
								{
									file.append("<path"+(comment.trimmed() != "" && ku+1 == multivalues.size() ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(multivalues.value(ku)).remove( '"' )+"\" />\n");
								}
							}
						}
					}
					else
						file.append("<value"+(comment.trimmed() != "" ? " comment=\""+MyEscape(comment.trimmed())+"\"" : "")+" content=\""+MyEscape(liste3[0].trimmed())+"\" />\n");
				}
				file.append("</variable>\n");
			}
			else if(end_bloc.exactMatch(v[i]))
			{
				while(!isNested.isEmpty() && isNested.top())
				{
					isNested.top();
					file.append(pile.pop());
					isNested.pop();
				}
				isNested.top();
				file.append(pile.pop());
				isNested.pop();
				if(!isNested.isEmpty() && isNested.top())
				{
					isNested.top();
					file.append(pile.pop());
					isNested.pop();
				}
			}
			else if(comments.exactMatch(v[i]))
			{
				QStringList liste = comments.capturedTexts();
				file.append("<comment value=\"#"+MyEscape(liste[1])+"\" />\n");
			}
			else if(v[i] == "")
			{
				nbEmptyLine++;
				while(!isNested.isEmpty() && isNested.top())
				{
					file.append(pile.pop());
					isNested.pop();
				}
				if(i+1 < v.size())
				{
					if(v[i+1] != "")
					{
						file.append("<emptyline count=\""+QString::number(nbEmptyLine)+"\" />\n");
						nbEmptyLine = 0;
					}
				}
				else
					file.append("<emptyline count=\""+QString::number(nbEmptyLine)+"\" />\n");
			}
			else
			{
				qWarning( "%s didn't match", v[i].toLocal8Bit().constData());
				throw MksException( QString("Erreur parsing project file: %1").arg( s ) );
			}
		}
		while(!isNested.isEmpty() && isNested.top())
		{
			file.append(pile.pop());
			isNested.pop();
		}
	}
	catch(const std::exception & e)
	{
		// re-init the XML output
		file.append( QString( "<!DOCTYPE XUPProject>\n<project codec=\"%1\" name=\"%2\" editor=\"%3\" expanded=\"false\">\n" ).arg( codec ).arg( QFileInfo( s ).fileName() ).arg( mQMakeEditor ) );
		// empty both stacks
		isNested.clear();
		pile.clear();
		qWarning("%s", e.what() );
	}
	
	file.append( "</project>\n" );
	// to output the xml in a file
	/*QFile apt(s+".xml");
	if( apt.open( QIODevice::WriteOnly | QIODevice::Text ) )
	{
		apt.write(file.toAscii());
		apt.close();
	}*/
	
	return file;
}

QString convertNodeToPro( const QDomElement& element, const QString& EOL = pMonkeyStudio::getEol() )
{
	static int tabs = 0; // tabs indentation
	static bool isMultiline = false; // tell if last variable is multiline or not
	bool isNested = false; // tell if scope is nested or not
	QString comment; // comment of item if available
	QString data; // the data to return
	const QString tag = element.tagName(); // current node tag name

	if ( tag != "project" )
	{
		if ( tag == "function" )
		{
			QString function = QString( "%1( %2 )" ).arg( element.attribute( "name" ) ).arg( element.attribute( "parameters" ) );
			comment = element.attribute( "comment" );
			
			data.append( tabsString( tabs ) +function );
			
			if ( !comment.isEmpty() )
			{
				data.append( ' ' +comment );
			}
			
			data.append( EOL );
		}
		else if ( tag == "emptyline" )
		{
			int count = element.attribute( "count" ).toInt();
			
			for ( int i = 0; i < count; i++ )
			{
				data.append( EOL );
			}
		}
		else if ( tag == "variable" )
		{
			int vtabs = tabs;
			QDomElement parentElement = element.parentNode().toElement();
			QString variable = QString( "%1\t%2 " ).arg( element.attribute( "name" ) ).arg( element.attribute( "operator", "=" ) );
			isMultiline = QVariant( element.attribute( "multiline", "false" ) ).toBool();
			
			if ( parentElement.tagName() == "scope" && QVariant( parentElement.attribute( "nested", "false" ) ).toBool() )
			{
				vtabs--;
			}
			
			data.append( tabsString( vtabs ) +variable );
		}
		else if ( tag == "value" || tag == "file" || tag == "path" )
		{
			int vtabs = tabs;
			QString value = element.attribute( "content" );
			comment = element.attribute( "comment" );
			
			if ( !element.previousSibling().isNull() && isMultiline )
			{
				vtabs++;
			}
			else if ( element.previousSibling().isNull() || !isMultiline )
			{
				vtabs = 0;
			}
			
			data.append( tabsString( vtabs ) +value );
			
			if ( isMultiline )
			{
				if ( !element.nextSibling().isNull() )
				{
					data.append( " \\" );
				}
				
				if ( !comment.isEmpty() )
				{
					data.append( ' ' +comment );
				}
				
				data.append( EOL );
			}
			else if ( element.nextSibling().isNull() )
			{
				if ( !comment.isEmpty() )
				{
					data.append( ' ' +comment );
				}
				
				data.append( EOL );
			}
			else
			{
				data.append( ' ' );
			}
		}
		else if ( tag == "scope" )
		{
			int vtabs = tabs;
			QDomElement parentElement = element.parentNode().toElement();
			isNested = QVariant( element.attribute( "nested", "false" ) ).toBool();
			comment = element.attribute( "comment" );
			QString name = element.attribute( "name" );
			
			if ( ( element.attribute( "name" ) == "else" && !QVariant( element.previousSibling().toElement().attribute( "nested", "false" ) ).toBool() ) ||
				( parentElement.tagName() == "scope" && QVariant( parentElement.attribute( "nested", "false" ) ).toBool() ) )
			{
				vtabs = 0;
			}
			
			data.append( tabsString( vtabs ) +name );
			
			if ( !isNested )
			{
				data.append( " {" );
				
				if ( !comment.isEmpty() )
				{
					data.append( ' ' +comment );
				}
				
				data.append( EOL );
				tabs++;
			}
			else
			{
				data.append( ':' );
			}
		}
		else if ( tag == "comment" )
		{
			int vtabs = tabs;
			QString cmt = element.attribute( "value" );
			
			if ( element.parentNode().toElement().tagName() == "variable" && isMultiline )
			{
				vtabs++;
			}
			
			data.append( tabsString( vtabs ) +cmt +EOL );
		}
	}
	else
	{
		tabs = 0;
	}
	
	const QStringList containers = QStringList() << "function" << "emptyline" << "value" << "file" << "path" << "comment";
	
	if ( element.hasChildNodes() && !containers.contains( tag ) )
	{
		QDomNodeList nodes = element.childNodes();
		
		for ( int i = 0; i < nodes.count(); i++ )
		{
			data.append( convertNodeToPro( nodes.at( i ).toElement(), EOL ) );
		}
		
		if ( tag == "scope" && !isNested )
		{
			tabs--;
			QDomElement childElement = element.nextSibling().toElement();
			
			data.append( tabsString( tabs ) +"}" );
			
			if ( !( childElement.tagName() == "scope" && childElement.attribute( "name" ) == "else" ) )
			{
				data.append( EOL );
			}
			else
			{
				data.append( ' ' );
			}
		}
	}

	return data;
}

QString QMake2XUP::convertToPro( const QDomDocument& document )
{
	// get project node
	QDomElement element  = document.firstChildElement( "project" ).toElement();
	
	// check project available
	if ( element.isNull() )
	{
		return QString::null;
	}
	
	// parse project scope
	QString contents = convertNodeToPro( element );
	
	// remove last eol
	if ( contents.length() > 0 )
	{
		contents.chop( 1 );
	}
	
	// return buffer
	return contents;
}
