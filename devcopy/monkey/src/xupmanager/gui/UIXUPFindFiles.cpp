#include "UIXUPFindFiles.h"

#include <QDir>

UIXUPFindFiles.UIXUPFindFiles(  QString& findFile, parent )
    : QDialog( parent )
    setupUi( self )
    lFindFile.setText( findFile )


UIXUPFindFiles.~UIXUPFindFiles()


def setFiles(self, files, rootPath ):
    QDir dir( rootPath )
    for fi in files:
        text = rootPath.isEmpty() ? fi.fileName() : dir.relativeFilePath( fi.absoluteFilePath() )
        item = QListWidgetItem( lwFiles )
        item.setText( text )
        item.setToolTip( fi.absoluteFilePath() )
        lwFiles.addItem( item )

    
    lwFiles.setCurrentRow( 0 )


def on_lwFiles_itemSelectionChanged(self):
    item = lwFiles.selectedItems().value( 0 )
    if  item :
        lAbsoluteFilePath.setText( item.toolTip() )



def on_lwFiles_itemActivated(self, item ):
    Q_UNUSED( item )
    accept()


def selectedFile(self):
    item = lwFiles.selectedItems().value( 0 )
    if  item :
        return item.toolTip()

    
    return QString.null


def accept(self):
    if  lwFiles.selectedItems().count() == 1 :
        QDialog.accept()


