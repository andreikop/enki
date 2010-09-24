
class pDockToolBarManager : QObject
{
%TypeHeaderCode
#include <../widgets/pDockToolBarManager.h>
%End

public:
	QMainWindow* mainWindow() const;
	pDockToolBar* bar( Qt::ToolBarArea area );

	void setSettings( pSettings* settings );
	pSettings* settings();

	static Qt::ToolBarArea dockWidgetAreaToToolBarArea( Qt::DockWidgetArea area );
	static Qt::DockWidgetArea toolBarAreaToDockWidgetArea( Qt::ToolBarArea area );
	static QBoxLayout::Direction toolBarAreaToBoxLayoutDirection( Qt::ToolBarArea area );

protected:
	pDockToolBarManager( QMainWindow* window );

public slots:
	void dockWidgetAreaChanged( QDockWidget* dock, pDockToolBar* bar );
	virtual void restoreState( pDockToolBar* bar = 0 );
	virtual void saveState( pDockToolBar* bar = 0 );
};
