'''***************************************************************************
**
**         Created using Monkey Studio v1.8.0.0
** Author    : Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>
** Project   : UIProjectHeaders
** FileName  : UIProjectHeaders.cpp
** Date      : 2007-11-04T02:21:34
** License   : GPL
** Comment   : Your comment here
**
** This file is provided AS IS with NO WARRANTY OF ANY KIND, THE
** WARRANTY OF DESIGN, AND FITNESS FOR A PARTICULAR PURPOSE.
**
***************************************************************************'''
#include "UIProjectHeaders.h"
#include "ProjectHeaders.h"

#include <QDir>
#include <QFileInfoList>
#include <QTextCodec>
#include <QHash>
#include <QStringList>
#include <QPushButton>
#include <QDateTime>
#include <QMessageBox>
#include <QDebug>

#include <pMonkeyStudio.h>
#include <variablesmanager/VariablesManager.h>

UIProjectHeaders.UIProjectHeaders( QWidget* parent, plugin )
        : QDialog( parent ), mPlugin( plugin )
    # setup dialog
    setupUi( self )
    # restore settings
    restoreSettings()
    # set buttons icons
    dbbButtons.button( QDialogButtonBox.Apply ).setIcon( QPixmap( ":/icons/icons/ok.png" ) )
    dbbButtons.button( QDialogButtonBox.Close ).setIcon( QPixmap( ":/icons/icons/cancel.png" ) )
    # connections
    connect( dbbButtons.button( QDialogButtonBox.Apply ), SIGNAL( clicked() ), self, SLOT( accept() ) )


def restoreSettings(self):
    # add languages to combo
    cbLanguages.addItems( pMonkeyStudio.availableLanguages() )
    # save inputs
    leDirectory.setText( mPlugin.settingsValue( "Directory" ).toString() )
    leAuthors.setText( mPlugin.settingsValue( "Authors" ).toString() )
    leProjectName.setText( mPlugin.settingsValue( "ProjectName" ).toString() )
    leHomePage.setText( mPlugin.settingsValue( "HomePage" ).toString() )
     license = mPlugin.settingsValue( "License", "GPL" ).toString()
    if  cbLicenses.findText( license ) == -1 :
        cbLicenses.addItem( license )
    cbLicenses.setCurrentIndex( cbLicenses.findText( license ) )
    teComment.setPlainText( mPlugin.settingsValue( "Comment" ).toString() )
    # set regexp and licensing
    for ( i = 0; i < cbLanguages.count(); i++ )
        cbLanguages.setItemData( i, templatesHeaderRegExp( cbLanguages.itemText( i ) ), Qt.UserRole +1 )
        cbLanguages.setItemData( i, templatesHeader( cbLanguages.itemText( i ) ), Qt.UserRole +2 )

    # show current language information
    if  cbLanguages.count() :
        cbLanguages.setCurrentIndex( 0 )
        leRegExp.setText( cbLanguages.itemData( 0, Qt.UserRole +1 ).toString() )
        teLicensing.setPlainText( cbLanguages.itemData( 0, Qt.UserRole +2 ).toString() )

    # encodings
    encodings = pMonkeyStudio.availableTextCodecs()
    lwSourceEncoding.addItems( encodings )
    lwTargetEncoding.addItems( encodings )
    QList<QListWidgetItem*> items
    items = lwSourceEncoding.findItems( mPlugin.settingsValue( "SourceEncoding", "UTF-8" ).toString(), Qt.MatchFixedString )
    lwSourceEncoding.setCurrentItem( items.value( 0 ) )
    items = lwTargetEncoding.findItems( mPlugin.settingsValue( "TargetEncoding", "UTF-8" ).toString(), Qt.MatchFixedString )
    lwTargetEncoding.setCurrentItem( items.value( 0 ) )


def saveSettings(self):
    # save inputs
    mPlugin.setSettingsValue( "Directory", leDirectory.text() )
    mPlugin.setSettingsValue( "Authors", leAuthors.text() )
    mPlugin.setSettingsValue( "ProjectName", leProjectName.text() )
    mPlugin.setSettingsValue( "HomePage", leHomePage.text() )
    mPlugin.setSettingsValue( "License", cbLicenses.currentText() )
    mPlugin.setSettingsValue( "Comment", teComment.toPlainText() )
    # save regexp and licensing
    on_cbLanguages_highlighted( -1 )
    for ( i = 0; i < cbLanguages.count(); i++ )
        setTemplatesHeaderRegExp( cbLanguages.itemText( i ), cbLanguages.itemData( i, Qt.UserRole +1 ).toString() )
        setTemplatesHeader( cbLanguages.itemText( i ), cbLanguages.itemData( i, Qt.UserRole +2 ).toString() )

    # encodings
    if  item = lwSourceEncoding.selectedItems().value( 0 ) :
        mPlugin.setSettingsValue( "SourceEncoding", item.text() )
    if  item = lwTargetEncoding.selectedItems().value( 0 ) :
        mPlugin.setSettingsValue( "TargetEncoding", item.text() )


def setTemplatesHeaderRegExp(self, language, regexp ):
    mPlugin.setSettingsValue( QString( "RegExp/" ).append( language ), regexp )


def templatesHeaderRegExp(self, language ):
    regexp = mPlugin.settingsValue( QString( "RegExp/" ).append( language ), QString() ).toString()
    return regexp.isEmpty() ? defaultTemplatesHeaderRegExp( language ) : regexp


def defaultTemplatesHeaderRegExp(self, language ):
    QString regexp

    if  language == "C++" :
        regexp = "^(/\\*.*\\''')"
    elif  language == "HTML" :
        regexp = "^(<not --+.*--+>)"

    # default
    return regexp


def setTemplatesHeader(self, language, license ):
    mPlugin.setSettingsValue( QString( "Licensing/" ).append( language ), license )


def templatesHeader(self, language ):
    license = mPlugin.settingsValue( QString( "Licensing/" ).append( language ), QString() ).toString()
    return license.isEmpty() ? defaultTemplatesHeader( language ) : license


def defaultTemplatesHeader(self, language ):
    QString license

    if  language == "C++" :
        license = "'''***************************************************************************\n"
                  "**\n"
                  "**         Created using $editor_version_string$\n"
                  "** Authors   : $authors$\n"
                  "** Project   : $projectname$\n"
                  "** FileName  : $filename$\n"
                  "** Date      : $date$\n"
                  "** License   : $license$\n"
                  "** Comment   : $comment$\n"
                  "** Home Page : $homepage$\n"
                  "**\n"
                  "** This file is provided AS IS with NO WARRANTY OF ANY KIND, THE\n"
                  "** WARRANTY OF DESIGN, AND FITNESS FOR A PARTICULAR PURPOSE.\n"
                  "**\n"
                  "***************************************************************************'''\n"
    elif  language == "HTML" :
        license = "<not ---------------------------------------------------------------------\n"
                  "--\n"
                  "--        Created using $editor_version_string$\n"
                  "-- Authors   : $authors$\n"
                  "-- Project   : $projectname$\n"
                  "-- FileName  : $filename$\n"
                  "-- Date      : $date$\n"
                  "-- License   : $license$\n"
                  "-- Comment   : $comment$\n"
                  "-- Home Page : $homepage$\n"
                  "--\n"
                  "-- This file is provided AS IS with NO WARRANTY OF ANY KIND, THE\n"
                  "-- WARRANTY OF DESIGN, AND FITNESS FOR A PARTICULAR PURPOSE.\n"
                  "--\n"
                  "---------------------------------------------------------------------------.\n"

    # default
    return license


def on_cbLanguages_highlighted(self,  int ):
    cbLanguages.setItemData( cbLanguages.currentIndex(), leRegExp.text(), Qt.UserRole +1 )
    cbLanguages.setItemData( cbLanguages.currentIndex(), teLicensing.toPlainText(), Qt.UserRole +2 )


def on_cbLanguages_currentIndexChanged(self, i ):
    leRegExp.setText( cbLanguages.itemData( i, Qt.UserRole +1 ).toString() )
    teLicensing.setPlainText( cbLanguages.itemData( i, Qt.UserRole +2 ).toString() )


def on_tbDirectory_clicked(self):
     s = pMonkeyStudio.getExistingDirectory( tr( "Choose the directory to scan" ), QString(), window() )
    if  not s.isEmpty() :
        leDirectory.setText( s )


def reject(self):
    saveSettings()
    QDialog.reject()


def accept(self):
    # save settings
    saveSettings()
    # get languages filters
    QStringList filters
    QMap<QString, l = pMonkeyStudio.availableLanguagesSuffixes()
    for k in l.keys():
    foreach ( QString e, l.value( k ) )
    if  not filters.contains( e ) :
        filters << e
    # encodings
    sourceCodec = QTextCodec.codecForName( mPlugin.settingsValue( "SourceEncoding", "UTF-8" ).toString().toAscii() )
    targetCodec = QTextCodec.codecForName( mPlugin.settingsValue( "SourceEncoding", "UTF-8" ).toString().toAscii() )
    # set dictionnary
    VariablesManager.Dictionary v
    v[ "authors" ] = leAuthors.text()
    v[ "projectname" ] = leProjectName.text()
    v[ "license" ] = cbLicenses.currentText()
    v[ "homepage" ] = leHomePage.text()
    v[ "comment" ] = teComment.toPlainText().trimmed()
    # get variables manager
    vm = VariablesManager.instance()
    # get recursive files
    yesToAll = False
    foreach ( QFileInfo fi, pMonkeyStudio.getFiles( QDir( leDirectory.text() ), filters, True ) )
        QFile f( fi.absoluteFilePath() )
        f.open( QIODevice.ReadWrite | QIODevice.Text )
        b = sourceCodec.toUnicode( f.readAll() )
        l = pMonkeyStudio.languageForFileName( fi.fileName() )
        # regexp
        QRegExp rx( templatesHeaderRegExp( l ) )
        rx.setMinimal( True )
        if  rx.indexIn( b ) != -1 and rx.cap( 1 ).trimmed().length() > 0 :
            if  not yesToAll :
                QMessageBox msg( window() )
                msg.setWindowTitle( tr( "Replace Licensing..." ) )
                msg.setIcon( QMessageBox.Question )
                msg.setStandardButtons( QMessageBox.YesToAll | QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel )
                msg.setText( tr( "There already is a licensing, file :\n%1\n replace it ?" ).arg( fi.fileName() ) )
                msg.setDetailedText( rx.cap( 1 ) )
                switch ( msg.exec() )
                case QMessageBox.YesToAll:
                    yesToAll = True
                    break
                case QMessageBox.No:
                    continue
                    break
                case QMessageBox.Cancel:
                    return
                default:
                    break


            b.remove( 0, rx.cap( 1 ).length() )

        # set variables
        v[ "filename" ] = fi.fileName()
        v[ "date" ] = fi.created().toString( Qt.ISODate )
        # replaces variables
        b = b.trimmed().prepend( vm.replaceAllVariables( templatesHeader( l ), v ) ).append( pMonkeyStudio.getEol() )
        # write buffer
        f.resize( 0 )
        f.write( targetCodec.fromUnicode( b ) )
        f.close()


