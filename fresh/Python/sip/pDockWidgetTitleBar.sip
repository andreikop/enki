class pDockWidgetTitleBar : QToolBar
{
%TypeHeaderCode
#include <../widgets/pDockWidgetTitleBar.h>
%End

public:
	pDockWidgetTitleBar( pDockWidget* parent = 0 );
	
	virtual bool event( QEvent* event );
	virtual QSize minimumSizeHint() const;
	virtual QSize sizeHint() const;
	
	QWidget* addAction( QAction* action, int index = -1 );
	void addSeparator( int index = -1 );

protected:
	
	virtual void paintEvent( QPaintEvent* event );
	void transposeSize( QRect& rect );
	void updateStandardIcons();

protected slots:
	void aOrientation_triggered();
	void aFloat_triggered();
	void dockWidget_featuresChanged( QDockWidget::DockWidgetFeatures features );
};
