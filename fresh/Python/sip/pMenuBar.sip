
class pMenuBar : QMenuBar
{
%TypeHeaderCode
#include <../widgets/pMenuBar.h>
%End

public:
	pMenuBar( QWidget* parent = 0 );

	QString absoluteScope( const QString& path );
	QString relativeScope( const QString& path );
	static QString normalizedKey( const QString& key );
	void beginGroupOrArray( const pGroupPath& group );
	void beginGroup( const QString& group );
	QString group() const;
	void endGroup();
	
	Qt::ShortcutContext defaultShortcutContext() const;
	void setDefaultShortcutContext( Qt::ShortcutContext context );
	
	pActionsManager* actionsManager() const;
	
	QMenu* menu( const QString& path = QString::null, const QString& title = QString::null, const QIcon& icon = QIcon() );
	QAction* action( const QString& path, const QString& text = QString::null, const QIcon& icon = QIcon(), const QString& shortcut = QString::null, const QString& toolTip = QString::null );
	void addAction( const QString& path, QAction* action );
	
	void clearMenu( const QString& path );
	void deleteMenu( const QString& path );
	void setMenuEnabled( QMenu* menu, bool enabled );
};
