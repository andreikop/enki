typedef QList<QAction*> QActionList;

class pActionsManager : QObject
{
%TypeHeaderCode
#include <../widgets/pActionsManager.h>
%End
public:
	enum PropertyType { ActionsManager = 0, ActionPath, DefaultShortcut };
	
	pActionsManager( const QString& name, QObject* parent = 0 );
	virtual ~pActionsManager();
	
	void setSettings( QSettings* settings );
	QSettings* settings() const;
	
	QString name() const;
	void reloadSettings() const;
	QActionList actions( const QString& path = QString::null ) const;
	QAction* action( const QString& path, const QString& name ) const;
	QAction* newAction( const QString& path, const QKeySequence& defaultShortcut, const QString& name );
	QString lastError() const;
	
	static QString fixedPath( const QString& path );
	static bool setShortcut( QAction* action, const QKeySequence& shortcut );
	
	static pActionsManager* actionsManager( QAction* action );
	static void setActionsManager( QAction* action, pActionsManager* manager );
	
	static QString actionPath( QAction* action );
	static void setActionPath( QAction* action, const QString& path );
	
	static QKeySequence defaultShortcut( QAction* action );
	static void setDefaultShortcut( QAction* action, const QKeySequence& shortcut );
	
	static QString pathPartTranslation( const QString& part );
	static QString pathTranslation( const QString& path, const QString& separator = " > " );
	static QString pathTranslation( QAction* action, const QString& separator = " > " );
	static void setPathPartTranslation( const QString& part, const QString& translation );

protected:
	void updateShortcut( QAction* action ) const;

protected slots:
	void actionDestroyed( QObject* object );

public slots:
	void editActionsShortcuts();
};
