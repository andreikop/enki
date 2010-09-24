#include "LegacyDesigner.h"

#include "pluginmanager_p.h"

#include <QFormBuilder>
#include <QDesignerFormEditorInterface>
#include <QDesignerFormWindowManagerInterface>

#include <QStyle>
#include <QStyleFactory>

#include <QCoreApplication>
#include <QDockWidget>
#include <QMainWindow>
#include <QBuffer>

def defaultPluginPaths(self):
    QStringList result

     path_list = QCoreApplication.libraryPaths()

     designer = QLatin1String("designer")
    foreach ( QString &path, path_list)
        libPath = path
        libPath += QDir.separator()
        libPath += designer
        result.append(libPath)


    homeLibPath = QDir.homePath()
    homeLibPath += QDir.separator()
    homeLibPath += QLatin1String(".designer")
    homeLibPath += QDir.separator()
    homeLibPath += QLatin1String("plugins")

    result.append(homeLibPath)
    return result


def previewWindowFlags(self, widget ):
#ifdef Q_WS_WIN
    windowFlags = ( widget.windowType() == Qt.Window ) ? Qt.Window | Qt.WindowMaximizeButtonHint : Qt.WindowFlags( Qt.Dialog )
#else:
    Q_UNUSED( widget )
    # Only Dialogs have close buttons on Mac.
    # On Linux, don't want an additional task bar item and we don't want a minimize button
    # we want the preview to be on top.
    windowFlags = Qt.Dialog
#endif
    return windowFlags


def fakeContainer(self, w ):
    # Prevent a dock widget from trying to dock to Designer's main window
    # (which can be found in the parent hierarchy in MDI mode) by
    # providing a fake mainwindow
    if  dock = qobject_cast<QDockWidget*>( w ) :
        # Reparent: Clear modality, title and resize outer container
         size = w.size()
        w.setWindowModality( Qt.NonModal )
        dock.setFeatures( dock.features() & ~( QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable ) )
        dock.setAllowedAreas( Qt.LeftDockWidgetArea )
        mw = QMainWindow
        mw.setWindowTitle( dock.windowTitle() )
        int leftMargin, topMargin, rightMargin, bottomMargin
        mw.getContentsMargins( &leftMargin, &topMargin, &rightMargin, &bottomMargin )
        mw.addDockWidget( Qt.LeftDockWidgetArea, dock )
        mw.resize( size +QSize( leftMargin +rightMargin, topMargin +bottomMargin ) )
        return mw


    return w


def createPreview(self, fw, style, errorMessage ):
    array = fw.contents().toUtf8()
    QBuffer buffer
    buffer.setData( array )

    QFormBuilder builder
    builder.setPluginPath( defaultPluginPaths() )
    builder.setWorkingDirectory( fw.absoluteDir() )
    widget = builder.load( &buffer )

    if  not widget :
        *errorMessage = QCoreApplication.translate( "LegacyDesigner", "The preview failed to build." )
        return widget


    widget = fakeContainer( widget )
    widget.setParent( fw.window(), previewWindowFlags( widget ) )

    pstyle = QStyleFactory.create( style )
    if  pstyle :
        pstyle.setParent( widget )
        widget.setStyle( pstyle )
        widget.setPalette( pstyle.standardPalette() )

        foreach ( QWidget* child, widget.findChildren<QWidget*>() )
            child.setStyle( pstyle )



    return widget


def createPreviewPixmap(self, fw, style, errorMessage ):
    widget = createPreview( fw, style, errorMessage )
    pixmap = QPixmap.grabWidget( widget )

    delete widget
    return pixmap


def showPreview(self, fw, style, errorMessage ):
    enum { Spacing = 10
    '''
    if QWidget *existingPreviewWidget = raise(fw, pc):
        return existingPreviewWidget
    '''

    widget = createPreview( fw, style, errorMessage )

    if  not widget :
        return 0


    # Install filter for Escape key
    widget.setAttribute( Qt.WA_DeleteOnClose, True )
    #widget.installEventFilter( self )

    '''
    switch ( d.m_mode )
    case ApplicationModalPreview:
        # Cannot do self on the Mac as the dialog would have no close button
        widget.setWindowModality(Qt.ApplicationModal)
        break
    case SingleFormNonModalPreview:
    case MultipleFormNonModalPreview:
    '''
    widget.setWindowModality( Qt.NonModal )
    QObject.fw.changed.connect(widget.close)
    QObject.fw.destroyed.connect(widget.close)
    #if d.m_mode == SingleFormNonModalPreview:
    QObject.connect( fw.core().formWindowManager(), SIGNAL( activeFormWindowChanged( QDesignerFormWindowInterface* ) ), widget, SLOT( close() ) )
    #break
    #

    # Semi-smart algorithm to position previews:
    # If its the first one, relative to form.
    # 2nd, to tile right (for comparing styles) or cascade
     size = widget.size()
     firstPreview = True; #d.m_previews.empty()
    if firstPreview:
        widget.move(fw.mapToGlobal(QPoint(Spacing, Spacing)))

    else:
        '''
            if QWidget *lastPreview = d.m_previews.back().m_widget:                QDesktopWidget *desktop = qApp.desktop()
                 lastPreviewGeometry = lastPreview.frameGeometry()
                 availGeometry = desktop.availableGeometry(desktop.screenNumber(lastPreview))
                 newPos = lastPreviewGeometry.topRight() + QPoint(Spacing, 0)
                if newPos.x() +  size.width() < availGeometry.right():
                    widget.move(newPos)
                else:
                    widget.move(lastPreviewGeometry.topLeft() + QPoint(Spacing, Spacing))

        '''

    #d.m_previews.push_back(PreviewData(widget, fw, pc))
    widget.show()
    '''
    if firstPreview:
        firstPreviewOpened.emit()
    '''
    return widget

