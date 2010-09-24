#include "UISettingsQMake.h"
#include "QMake.h"
#include "QtVersionManager.h"

#include <pMonkeyStudio.h>

#include <QPushButton>
#include <QDir>
#include <QWhatsThis>
#include <QFileSystemModel>
#include <QDirModel>
#include <QCompleter>
#include <QMessageBox>
#include <QDebug>

UISettingsQMake.UISettingsQMake( QWidget* parent )
        : QWidget( parent )
    # set up dialog
    setupUi( self )

    mQtManager = QMake.versionManager()

    # completer of paths
#ifdef Q_CC_GNU
#warning *** USING QDirModel is deprecated but QCompleter does not handle QFileSystemModel... please fix me when possible.
#endif
    completer = QCompleter( leQtVersionPath )
    model = QDirModel( completer )

    model.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Hidden | QDir.Readable )
    completer.setModel( model )
    leQtVersionPath.setCompleter( completer )

    lwPages.setCurrentRow( 0 )
    dbbButtons.button( QDialogButtonBox.Help ).setIcon( QIcon( ":/help/icons/help/keyword.png" ) )
    dbbButtons.button( QDialogButtonBox.Save ).setIcon( QIcon( ":/file/icons/file/save.png" ) )

    # load settings
    loadSettings()

    # connections
    lwQtVersions.currentItemChanged.connect(self.lw_currentItemChanged)
    lwQtModules.currentItemChanged.connect(self.lw_currentItemChanged)
    lwQtConfigurations.currentItemChanged.connect(self.lw_currentItemChanged)
    foreach ( QToolButton* tb, findChildren<QToolButton*>( QRegExp( "tbAdd*" ) ) )
    tb.clicked.connect(self.tbAdd_clicked)
    foreach ( QToolButton* tb, findChildren<QToolButton*>( QRegExp( "tbRemove*" ) ) )
    tb.clicked.connect(self.tbRemove_clicked)
    foreach ( QToolButton* tb, findChildren<QToolButton*>( QRegExp( "tbClear*" ) ) )
    tb.clicked.connect(self.tbClear_clicked)
    foreach ( QToolButton* tb, findChildren<QToolButton*>( QRegExp( "tbUp*" ) ) )
    tb.clicked.connect(self.tbUp_clicked)
    foreach ( QToolButton* tb, findChildren<QToolButton*>( QRegExp( "tbDown*" ) ) )
    tb.clicked.connect(self.tbDown_clicked)
    leQtVersionVersion.editingFinished.connect(self.qtVersionChanged)
    leQtVersionVersion.textChanged.connect(self.qtVersionChanged)
    leQtVersionPath.editingFinished.connect(self.qtVersionChanged)
    connect( cbQtVersionQMakeSpec.lineEdit(), SIGNAL( editingFinished() ), self, SLOT( qtVersionChanged() ) )
    leQtVersionQMakeParameters.editingFinished.connect(self.qtVersionChanged)
    cbQtVersionHasSuffix.toggled.connect(self.qtVersionChanged)


def tbAdd_clicked(self):
    lw = 0
    if  sender() == tbAddQtVersion :
        lw = lwQtVersions
    elif  sender() == tbAddQtModule :
        lw = lwQtModules
    elif  sender() == tbAddQtConfiguration :
        lw = lwQtConfigurations
    if  lw :
        lw.addItem( tr( "New value" ) )
        lw.setCurrentItem( lw.item( lw.count() -1 ) )
        lw.scrollToItem( lw.item( lw.count() -1 ) )
        lw.currentItem().setFlags( lw.currentItem().flags() | Qt.ItemIsEditable )



def tbRemove_clicked(self):
    if  sender() == tbRemoveQtVersion :
        delete lwQtVersions.selectedItems().value( 0 )
    elif  sender() == tbRemoveQtModule :
        delete lwQtModules.selectedItems().value( 0 )
    elif  sender() == tbRemoveQtConfiguration :
        delete lwQtConfigurations.selectedItems().value( 0 )


def tbClear_clicked(self):
    if  sender() == tbClearQtVersions :
        lwQtVersions.clear()
    elif  sender() == tbClearQtModules :
        lwQtModules.clear()
    elif  sender() == tbClearQtConfiguration :
        lwQtConfigurations.clear()


def tbUp_clicked(self):
    tb = qobject_cast<QToolButton*>( sender() )
    if  not tb :
        return
    lw = 0
    if  tb == tbUpQtVersion :
        lw = lwQtVersions
    elif  tb == tbUpQtModule :
        lw = lwQtModules
    elif  tb == tbUpQtConfiguration :
        lw = lwQtConfigurations
    if  not lw :
        return
    if  it = lw.selectedItems().value( 0 ) :
        i = lw.row( it )
        if  i != 0 :
            lw.insertItem( i -1, lw.takeItem( i ) )
        lw.setCurrentItem( it )



def tbDown_clicked(self):
    tb = qobject_cast<QToolButton*>( sender() )
    if  not tb :
        return
    lw = 0
    if  tb == tbDownQtVersion :
        lw = lwQtVersions
    elif  tb == tbDownQtModule :
        lw = lwQtModules
    elif  tb == tbDownQtConfiguration :
        lw = lwQtConfigurations
    if  not lw :
        return
    if  it = lw.selectedItems().value( 0 ) :
        i = lw.row( it )
        if  i != lw.count() -1 :
            lw.insertItem( i +1, lw.takeItem( i ) )
        lw.setCurrentItem( it )



def on_tbDefaultQtVersion_clicked(self):
    if  it = lwQtVersions.selectedItems().value( 0 ) :
        for ( i = 0; i < lwQtVersions.count(); i++ )
            cit = lwQtVersions.item( i )
            v = cit.data( Qt.UserRole ).value<QtVersion>()
            v.Default = it == cit
            cit.setData( Qt.UserRole, QVariant.fromValue( v ) )
            cit.setBackground( QBrush( v.Default ? Qt.green : Qt.transparent ) )




def qtVersionChanged(self):
    lw_currentItemChanged( lwQtVersions.currentItem(), lwQtVersions.currentItem() )


def on_tbQtVersionPath_clicked(self):
     s = pMonkeyStudio.getExistingDirectory( tr( "Locate your qt installation directory" ), leQtVersionPath.text(), window() )
    if  not s.isNull() :
        leQtVersionPath.setText( s )
        qtVersionChanged()



def on_tbQtVersionQMakeSpec_clicked(self):
     s = pMonkeyStudio.getExistingDirectory( tr( "Locate the mk spec folder to use" ), leQtVersionPath.text(), window() )
    if  not s.isNull() :
        if  cbQtVersionQMakeSpec.findText( s ) == -1 :
            cbQtVersionQMakeSpec.addItem( s )
        cbQtVersionQMakeSpec.setCurrentIndex( cbQtVersionQMakeSpec.findText( s ) )
        qtVersionChanged()



def lw_currentItemChanged(self, c, p ):
    if  c != p :
        foreach ( QWidget* widget, findChildren<QWidget*>() )
            widget.blockSignals( True )



    if  p :
        if  p.listWidget() == lwQtVersions :
            v = p.data( Qt.UserRole ).value<QtVersion>()
            v.Version = leQtVersionVersion.text()
            v.Path = leQtVersionPath.text()
            v.QMakeSpec = cbQtVersionQMakeSpec.currentText()
            v.QMakeParameters = leQtVersionQMakeParameters.text()
            v.HasQt4Suffix = cbQtVersionHasSuffix.isChecked()
            p.setData( Qt.UserRole, QVariant.fromValue( v ) )
            p.setText( v.Version )

        elif  p.listWidget() == lwQtModules :
            it = p.data( Qt.UserRole ).value<QtItem>()
            it.Text = leCaptionQtModule.text()
            it.Value = leValueQtModule.text()
            if  it.Variable.isEmpty() :
                it.Variable = "QT"
            it.Help = pteHelpQtModule.toPlainText()
            p.setData( Qt.UserRole, QVariant.fromValue( it ) )
            p.setText( it.Text )

        elif  p.listWidget() == lwQtConfigurations :
            it = p.data( Qt.UserRole ).value<QtItem>()
            it.Text = leCaptionQtConfiguration.text()
            it.Value = leValueQtConfiguration.text()
            if  it.Variable.isEmpty() :
                it.Variable = "CONFIG"
            it.Help = pteHelpQtConfiguration.toPlainText()
            p.setData( Qt.UserRole, QVariant.fromValue( it ) )
            p.setText( it.Text )


    if  c :
        if  c.listWidget() == lwQtVersions :
            v = c.data( Qt.UserRole ).value<QtVersion>()
            leQtVersionVersion.setText( v.Version )
            leQtVersionPath.setText( v.Path )
            # need to get all mkspecs for self qt versions
            cbQtVersionQMakeSpec.clear()
            QDir mkspecs( QString( v.Path ).append( "/mkspecs" ) )
            if  mkspecs.exists() :
                foreach (  QFileInfo& fi, mkspecs.entryInfoList( QDir.Dirs | QDir.NoDotAndDotDot, QDir.Name ) )
                    if  fi.fileName() != "common" and fi.fileName() != "features" :
                        cbQtVersionQMakeSpec.addItem( fi.fileName() )


            if  cbQtVersionQMakeSpec.findText( v.QMakeSpec ) == -1 :
                cbQtVersionQMakeSpec.addItem( v.QMakeSpec )
            cbQtVersionQMakeSpec.setCurrentIndex( cbQtVersionQMakeSpec.findText( v.QMakeSpec ) )
            leQtVersionQMakeParameters.setText( v.QMakeParameters )
            cbQtVersionHasSuffix.setChecked( v.HasQt4Suffix )
            wQtVersion.setEnabled( True )

        elif  c.listWidget() == lwQtModules :
            it = c.data( Qt.UserRole ).value<QtItem>()
            leCaptionQtModule.setText( it.Text )
            leValueQtModule.setText( it.Value )
            pteHelpQtModule.setPlainText( it.Help )
            wQtModule.setEnabled( True )

        elif  c.listWidget() == lwQtConfigurations :
            it = c.data( Qt.UserRole ).value<QtItem>()
            leCaptionQtConfiguration.setText( it.Text )
            leValueQtConfiguration.setText( it.Value )
            pteHelpQtConfiguration.setPlainText( it.Help )
            wQtConfiguration.setEnabled( True )


    elif  sender() == lwQtVersions :
        wQtVersion.setEnabled( False )
        leQtVersionVersion.clear()
        leQtVersionPath.clear()
        cbQtVersionQMakeSpec.clear()
        cbQtVersionHasSuffix.setChecked( False )

    elif  sender() == lwQtModules :
        wQtModule.setEnabled( False )
        leCaptionQtModule.clear()
        leValueQtModule.clear()
        pteHelpQtModule.clear()

    elif  sender() == lwQtConfigurations :
        wQtConfiguration.setEnabled( False )
        leCaptionQtConfiguration.clear()
        leValueQtConfiguration.clear()
        pteHelpQtConfiguration.clear()


    if  c != p :
        foreach ( QWidget* widget, findChildren<QWidget*>() )
            widget.blockSignals( False )




def loadSettings(self):
    # general
    for v in mQtManager.versions():
        it = QListWidgetItem( v.Version, lwQtVersions )
        it.setData( Qt.UserRole, QVariant.fromValue( v ) )
        if  v.Default :
            it.setBackground( QBrush( Qt.green ) )


    # qt modules
    for i in mQtManager.modules():
        it = QListWidgetItem( i.Text, lwQtModules )
        it.setData( Qt.UserRole, QVariant.fromValue( i ) )


    # configuration
    for i in mQtManager.configurations():
        it = QListWidgetItem( i.Text, lwQtConfigurations )
        it.setData( Qt.UserRole, QVariant.fromValue( i ) )



def on_dbbButtons_helpRequested(self):
    QString help

    switch ( swPages.currentIndex() )
    case 0:
        help = tr( "You can register one or more Qt Version to use in your Qt projects, you can easily select the one to use in project settings.<br /><br />"
                   "The green item is the default Qt Version used. if there is no green item, default Qt Version used will be the first one available. You can explicitely set the default Qt Version selecting an item and clicking the set default button.<br /><br />"
                   "To add a Qt version, click the <b>Add a Qt Version</b> button at top and fill needed fields.<br /><br />"
                   "The minimum required fields are:<br />"
                   "- <b>Version</b>: it define a human label across a Qt version.<br />"
                   "- <b>Path</b>: it define the path where is located your Qt installation (the path from where you can see bin/qmake).<br /><br />"
                   "You can get more help about fields reading there tooltips." )
        break

    case 1:
        help = tr( "You can register one or more Qt Modules for your Qt projects, you can easily use them in the project settings dialog.<br />"
                   "Qt Modules are components available by your Qt installation, QtCore, GtGui...<br />"
                   "This editor allow you to edit the available modules in case of by example a Qt version is released and MkS did not yet support the modules in the project settings.<br />"
                   "A concrete example is the release of Qt 4.6.0 that has added QtMultimedia, had notified that self module was not available in the project settings, you can't use it.<br />"
                   "By adding a module by clicking <b>Add a module</b> button, can define the module caption and its associated value, will make it available in the project settings not <br />"
                   "The minimum required fields are <b>caption</b> and <b>value</b>, while <b>help</b> is an optional description of the module and will be shown as tooltip in the project settings.<br />"
                   "Typically, module value goes into the QT variable of your project file."    )
        break

    case 2:
        help = tr( "Qt Configuration works like <b>Qt Modules</b> except that the content is shown in the <b>Others Modules</b> list and that values goes into the CONFIG variable of your project.<br /><br />"
                   "Configurations having the word '<b>only</b>' as caption will be considerated as group separators and must have no value associated (they will be ignored).")
        break



    if  not help.isEmpty() :
        point = rect().center()
        point.setY( 35 )
        QWhatsThis.showText( mapToGlobal( point ), help )



def on_dbbButtons_clicked(self, b ):
    # only accept save button
    if  dbbButtons.standardButton( b )  != QDialogButtonBox.Save :
        return


    # save qt versions
    QtVersionList versions

    for ( i = 0; i < lwQtVersions.count(); i++ )
        item = lwQtVersions.item( i )

         version = item.data( Qt.UserRole ).value<QtVersion>()

        if  not version.isValid() :
            lwQtVersions.setCurrentItem( item )
            QMessageBox.warning( self, tr( "Error..." ), tr( "A Qt Version is not valid and has been selected, correct it and save again." ) )
            lwQtVersions.setFocus()
            return


        versions << version


    mQtManager.setVersions( versions )

    # save modules
    QtItemList modules

    for ( i = 0; i < lwQtModules.count(); i++ )
        modules << lwQtModules.item( i ).data( Qt.UserRole ).value<QtItem>()


    mQtManager.setModules( modules )

    # save configurations
    QtItemList configurations

    for ( i = 0; i < lwQtConfigurations.count(); i++ )
        configurations << lwQtConfigurations.item( i ).data( Qt.UserRole ).value<QtItem>()


    mQtManager.setConfigurations( configurations )

    # save content on disk
    mQtManager.sync()

