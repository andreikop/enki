#ifndef MKSSHELLINTERPRETER_H
#define MKSSHELLINTERPRETER_H

#include <objects/MonkeyExport.h>
#include "widgets/pConsoleCommand.h"

#include <QPointer>
#include <QObject>
#include <QHash>

/*
Pointer to function
QString commandImplementation( const QString& command, const QStringList& arguments, int* result, MkSShellInterpreter* interpreter, void* data )
*/
typedef QString (*CommandImplementationPtr)(const QString&, const QStringList&, int*, class MkSShellInterpreter*, void* );

class Q_MONKEY_EXPORT MkSShellInterpreter : public QObject, public pConsoleCommand
{
	Q_OBJECT
	
public:
	enum Error
	{
		NoError = 0,
		InvalidCommand = -1,
		NoResultVariable = -2,
		UnknowError = -3
	};
	
	static MkSShellInterpreter* instance( QObject* parent = 0 );
	
	bool loadScript( const QString& fileName );
	void loadHomeScripts();
	QString usage( const QString& command ) const;
	QString interpret( const QString& command, int* result ) const;
	
	void addCommandImplementation( const QString& command, CommandImplementationPtr function, const QString& help = QString::null, void* data = 0 );
	void removeCommandImplementation( const QString& command );
	void setCommandHelp( const QString& command, const QString& help );
	
protected:
	static QPointer<MkSShellInterpreter> mInstance;
	QHash<QString, CommandImplementationPtr> mCommandImplementations;
	QHash<QString, void*> mCommandImplementationsData;
	QHash<QString, QString> mCommandHelps;
	
	MkSShellInterpreter( QObject* parent = 0 );
	static QString interpretHelp( const QString&, const QStringList& arguments, int* result, MkSShellInterpreter* interpreter, void* data );
	static QString interpretEcho( const QString&, const QStringList& arguments, int* result, MkSShellInterpreter* interpreter, void* data );
	
signals:
	void commandExecuted( const QString& command, const QString& output, int result );
};

#endif // MKSSHELLINTERPRETER_H
