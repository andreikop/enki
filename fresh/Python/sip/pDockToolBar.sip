class pDockToolBar : QToolBar
{
%TypeHeaderCode
#include <../widgets/pDockToolBar.h>
%End

public:
	pDockToolBar( pDockToolBarManager* manager, Qt::Orientation orientation = Qt::Horizontal, QMainWindow* window = 0 );

	virtual bool eventFilter( QObject* object, QEvent* event );

	QAction* addAction( QAction* action = 0, bool insert = true );
	void addActions( QList<QAction*> actions, bool insert = true );

	int addDock( QDockWidget* dock, const QString& title = QString(), const QIcon& icon = QIcon() );

	bool isDockVisible( int id ) const;
	bool isDockVisible( QDockWidget* dock ) const;

	bool exclusive() const;
	bool textAlwaysVisible() const;

	int id( QDockWidget* dock ) const;
	int id( QAbstractButton* button ) const;

	QDockWidget* dock( int id ) const;
	QDockWidget* dock( QAbstractButton* button ) const;

	QAbstractButton* button( int id ) const;
	QAbstractButton* button( QDockWidget* dock ) const;
	
	QList<QDockWidget*> docks() const;
	QList<QAbstractButton*> buttons() const;

	int count() const;
	
	QAction* toggleExclusiveAction() const;

public slots:
	void removeDock( int id );
	void removeDock( QDockWidget* dock );
	void setDockVisible( QDockWidget* dock, bool visible );
	void setExclusive( bool exclusive );
	void setTextAlwaysVisible( bool visible );

private slots:
	void internal_checkVisibility();
	void internal_checkButtonText( QAbstractButton* button );
	void internal_orientationChanged( Qt::Orientation orientation );
	void internal_dockChanged();
	void internal_dockDestroyed( QObject* object );
	void internal_buttonClicked( bool checked );

signals:
	void buttonClicked( int id );
	void dockWidgetAreaChanged( QDockWidget* dock, pDockToolBar* toolBar );
};
