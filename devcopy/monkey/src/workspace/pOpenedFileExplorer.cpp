#include "pOpenedFileExplorer.h"
#include "pWorkspace.h"
#include "coremanager/MonkeyCore.h"
#include "maininterface/UIMain.h"

#include <objects/pIconManager.h>
#include <widgets/pDockWidgetTitleBar.h>
#include <widgets/pMenuBar.h>

#include <QWidgetAction>
#include <QComboBox>
#include <QMenu>
#include <QDebug>

class pOpenedFileAction : public QWidgetAction
    Q_OBJECT

public:
    pOpenedFileAction( pOpenedFileExplorer* parent, model )
            : QWidgetAction( parent )
        mOpenedFileExplorer = parent
        mModel = model


    ~pOpenedFileAction()
        qDeleteAll( mCombos )


    void syncViewIndex(  QModelIndex& index )
        for combo in mCombos:
             aSMLocked = combo.view().selectionModel().blockSignals( True )
             aLocked = combo.blockSignals( True )
            combo.setCurrentIndex( index.row() )
            combo.view().selectionModel().blockSignals( aSMLocked )
            combo.blockSignals( aLocked )



protected:
    pOpenedFileExplorer* mOpenedFileExplorer
    QAbstractItemModel* mModel
    QHash<QWidget*, mCombos

    virtual QWidget* createWidget( QWidget* parent )
        combo = mCombos.value( parent )

        if  combo :
            #Q_ASSERT( 0 )
            return combo


        combo = QComboBox( parent )
        combo.setMaxVisibleItems( 25 )
        combo.setSizeAdjustPolicy( QComboBox.AdjustToContents )
        combo.setAttribute( Qt.WA_MacSmallSize )
        combo.setModel( mModel )

        combo.activated.connect(self.comboBox_activated)
        combo.destroyed.connect(self.object_destroyed)

        mCombos[ parent ] = combo

        return combo


protected slots:
    void comboBox_activated( int row )
         index = mModel.index( row, 0 )
        currentIndexChanged.emit( index )


    void object_destroyed( QObject* object )
        mCombos.remove( ((QWidget*)object).parentWidget() )


signals:
    void currentIndexChanged(  QModelIndex& index )


pOpenedFileExplorer.pOpenedFileExplorer( pWorkspace* workspace )
        : pDockWidget( workspace )
    Q_ASSERT( workspace )
    mWorkspace = workspace
    mModel = pOpenedFileModel( workspace )
    aComboBox = pOpenedFileAction( self, mModel )
    setupUi( self )
    setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
    tvFiles.setModel( mModel )
    tvFiles.setAttribute( Qt.WA_MacShowFocusRect, False )
    tvFiles.setAttribute( Qt.WA_MacSmallSize )

    # sort menu
    mSortMenu = QMenu( self )
    group = QActionGroup( mSortMenu )

    group.addAction( tr( "Opening order" ) )
    group.addAction( tr( "File name" ) )
    group.addAction( tr( "URL" ) )
    group.addAction( tr( "Suffixes" ) )
    group.addAction( tr( "Custom" ) )
    mSortMenu.addActions( group.actions() )

    for ( i = pOpenedFileModel.OpeningOrder; i < pOpenedFileModel.Custom +1; i++ )
        action = group.actions().at( i )
        action.setData( (pOpenedFileModel.SortMode)i )
        action.setCheckable( True )

        if  i == pOpenedFileModel.OpeningOrder :
            action.setChecked( True )



    aSortMenu = QAction( tr( "Sorting" ), self )
    aSortMenu.setMenu( mSortMenu )
    aSortMenu.setIcon( pIconManager.icon( "sort.png" ) )
    aSortMenu.setToolTip( aSortMenu.text() )
    '''
    tb = qobject_cast<QToolButton*>( titleBar().addAction( aSortMenu, 0 ) )
    tb.setPopupMode( QToolButton.InstantPopup )
    titleBar().addSeparator( 1 )
    '''
    tvFiles.viewport().setAcceptDrops( True )

    group.triggered.connect(self.sortTriggered)
    workspace.documentChanged.connect(self.documentChanged)
    workspace.currentDocumentChanged.connect(self.currentDocumentChanged)
    mModel.sortModeChanged.connect(self.sortModeChanged)
    mModel.documentsSorted.connect(self.documentsSorted)
    tvFiles.selectionModel().selectionChanged.connect(self.selectionModel_selectionChanged(  QItemSelection&,  QItemSelection& ) ) )
    aComboBox.currentIndexChanged.connect(self.syncViewsIndex)


def model(self):
    return mModel


def comboBoxAction(self):
    return aComboBox


def sortMode(self):
    return mModel.sortMode()


def setSortMode(self, mode ):
    mModel.setSortMode( mode )


def syncViewsIndex(self, index, syncOnly ):
    # sync action combobox
    aComboBox.syncViewIndex( index )

    # sync listview
     vLocked = tvFiles.blockSignals( True )
    tvFiles.setCurrentIndex( index )
    tvFiles.blockSignals( vLocked )

    # scroll the view
    tvFiles.scrollTo( index )

    if  syncOnly :
        return


    # backup/restore current focused widget as setting active mdi window will steal it
    focusWidget = window().focusWidget()

    # set current document
    document = mModel.document( index )
    mWorkspace.setCurrentDocument( document )

    # restore focus widget
    if  focusWidget :
        focusWidget.setFocus()



def sortTriggered(self, action ):
    mode = (pOpenedFileModel.SortMode)action.data().toInt()
    setSortMode( mode )


def documentChanged(self, document ):
    Q_UNUSED( document )


def currentDocumentChanged(self, document ):
     index = mModel.index( document )
    syncViewsIndex( index, True )


def sortModeChanged(self, mode ):
    for action in mSortMenu.actions():
        if  action.data().toInt() == mode :
            if  not action.isChecked() :
                action.setChecked( True )


            return




def documentsSorted(self):
    # scroll the view
    tvFiles.scrollTo( tvFiles.selectionModel().selectedIndexes().value( 0 ) )


def selectionModel_selectionChanged(self, selected, deselected ):
    Q_UNUSED( deselected )
     index = selected.indexes().value( 0 )
    syncViewsIndex( index, False )


def on_tvFiles_customContextMenuRequested(self, pos ):
    QMenu menu
    menu.addAction( MonkeyCore.menuBar().action( "mFile/mClose/aCurrent" ) )
    menu.addAction( MonkeyCore.menuBar().action( "mFile/mSave/aCurrent" ) )
    menu.addAction( MonkeyCore.menuBar().action( "mFile/aReload" ) )
    menu.addSeparator()
    menu.addAction( mSortMenu.menuAction() )
    menu.exec( tvFiles.mapToGlobal( pos ) )


#include "pOpenedFileExplorer.moc"
