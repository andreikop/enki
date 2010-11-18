#ifndef COMMANDLINEMANAGER_H
#define COMMANDLINEMANAGER_H

#include <QMap>
#include <QStringList>

class CommandLineManager
{
public:
	CommandLineManager();
	~CommandLineManager();
	
	void parse();
	void process();
	const QMap<QString, QStringList>& arguments() const;
	
	void showVersion();
	void showHelp();
	void openProjects( const QStringList& fileNames );
	void openFiles( const QStringList& fileNames );

protected:
	QMap<QString, QStringList> mArguments;
	bool mVersionShown;
};

#endif // COMMANDLINEMANAGER_H
