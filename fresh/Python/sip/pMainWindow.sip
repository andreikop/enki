
class pMainWindow : QMainWindow
{
%TypeHeaderCode
#include <../widgets/pMainWindow.h>
%End

public:
	pMainWindow( QWidget* parent = 0, Qt::WindowFlags windowFlags = 0 );

	pMenuBar* menuBar();
	pDockToolBarManager* dockToolBarManager();
	pDockToolBar* dockToolBar( Qt::ToolBarArea area );

	void setSettings( pSettings* settings );
	pSettings* settings();
	
protected:
	void hideEvent( QHideEvent* event );

public slots:
	virtual void saveState();
	virtual void restoreState();
};
