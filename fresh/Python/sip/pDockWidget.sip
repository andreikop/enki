class pDockWidget : QDockWidget
{
%TypeHeaderCode
#include <../widgets/pDockWidget.h>
%End

public:
	pDockWidget( const QString& title, QWidget* parent = 0, Qt::WindowFlags flags = 0 );
	pDockWidget( QWidget* parent = 0, Qt::WindowFlags flags = 0 );
	~pDockWidget();

	virtual QSize sizeHint() const;
	
	pDockWidgetTitleBar* titleBar() const;
	
	void setActionsManager( pActionsManager* manager );
	pActionsManager* actionsManager() const;
	
public slots:
	virtual void setVisible( bool visible );

protected:
	
	void init();
	QSize contentsSize() const;
	virtual void paintEvent( QPaintEvent* event );

protected slots:
	void toggleViewAction_toggled( bool toggled );
	void handleWindowActivation();
	void handleFocusProxy();
};
