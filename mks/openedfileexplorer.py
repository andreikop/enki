from PyQt4.QtCore import *
from PyQt4.QtGui import *

import PyQt4.fresh

import mks.monkeycore
import mks.iconmanager

class pOpenedFileAction(QWidgetAction):
    
    def __init__( self, parent, model ):
        QWidgetAction.__init__(self, parent )
        
        self.mOpenedFileExplorer = parent
        self.mModel = model
        mCombos = []

    def syncViewIndex( self, index ):
        for combo in mCombos:
            aSMLocked = combo.view().selectionModel().blockSignals( True )
            aLocked = combo.blockSignals( True )
            combo.setCurrentIndex( index.row() )
            combo.view().selectionModel().blockSignals( aSMLocked )
            combo.blockSignals( aLocked )

    def createWidget( self, parent ):
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

    def comboBox_activated( row ):
        index = mModel.index( row, 0 )
        currentIndexChanged.emit( index )
    
    def object_destroyed( object ):
        mCombos.remove( (object).parentWidget() )

    currentIndexChanged = pyqtSignal()

class pOpenedFileExplorer(PyQt4.fresh.pDockWidget):
    
    def __init__(self, workspace):
        PyQt4.fresh.pDockWidget.__init__(self, workspace)
        
        self.mWorkspace = workspace
        self.mModel = pOpenedFileModel( workspace )
        self.aComboBox = pOpenedFileAction( self, mModel )
        self.setupUi( self )
        self.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        self.tvFiles.setModel( mModel )
        self.tvFiles.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.tvFiles.setAttribute( Qt.WA_MacSmallSize )

        # sort menu
        self.mSortMenu = QMenu( self )
        group = QActionGroup( mSortMenu )

        group.addAction( self.tr( "Opening order" ) )
        group.addAction( self.tr( "File name" ) )
        group.addAction( self.tr( "URL" ) )
        group.addAction( self.tr( "Suffixes" ) )
        group.addAction( self.tr( "Custom" ) )
        mSortMenu.addActions( group.actions() )

        for  i in range(pOpenedFileModel.OpeningOrder, pOpenedFileModel.Custom +1):
            action = group.actions()[i]
            action.setData( i )
            action.setCheckable( True )

            if  i == pOpenedFileModel.OpeningOrder :
                action.setChecked( True )

        aSortMenu = QAction( tr( "Sorting" ), self )
        aSortMenu.setMenu( mSortMenu )
        aSortMenu.setIcon( mks.iconmanager.icon( "sort.png" ) )
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
        tvFiles.selectionModel().selectionChanged.connect(self.selectionModel_selectionChanged)
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
        mode = action.data().toInt()
        setSortMode( mode )

    def documentChanged(self, document ):
        pass

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
        index = selected.indexes().value( 0 )
        syncViewsIndex( index, False )

    def on_tvFiles_customContextMenuRequested(self, pos ):
        menu = QMenu()
        menu.addAction( mks.monkeycore.menuBar().action( "mFile/mClose/aCurrent" ) )
        menu.addAction( mks.monkeycore.menuBar().action( "mFile/mSave/aCurrent" ) )
        menu.addAction( mks.monkeycore.menuBar().action( "mFile/aReload" ) )
        menu.addSeparator()
        menu.addAction( mSortMenu.menuAction() )
        menu.exec_( tvFiles.mapToGlobal( pos ) )
