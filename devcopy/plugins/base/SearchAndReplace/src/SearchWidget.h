#ifndef SEARCHWIDGET_H
#define SEARCHWIDGET_H

#include "ui_SearchWidget.h"
#include "SearchAndReplace.h"
#include "SearchResultsModel.h"

#include <QFile>

class SearchAndReplace
class SearchThread
class ReplaceThread
class SearchResultsDock
class QProgressBar
class QToolButton

class SearchWidget : public QFrame, Ui.SearchWidget
    Q_OBJECT

public:
    enum InputField
        Search,
        Replace


    enum State
        Normal,
        Good,
        Bad


    SearchWidget( SearchAndReplace* plugin, parent = 0 )
    virtual ~SearchWidget()

    SearchAndReplace.Mode mode()
    SearchThread* searchThread()

    void setResultsDock( SearchResultsDock* dock )

    static bool isBinary( QFile& file )

public slots:
    void setMode( SearchAndReplace.Mode mode )

protected:
    SearchAndReplace* mPlugin
    SearchAndReplace.Mode mMode
    QMap<SearchAndReplace.Option, mOptionActions
    SearchAndReplace.Properties mProperties
    SearchThread* mSearchThread
    ReplaceThread* mReplaceThread
    SearchResultsDock* mDock
    QToolButton* tbMode
    QToolButton* tbCdUp
    QProgressBar* mProgress

    virtual bool eventFilter( QObject* object, event )
    virtual void keyPressEvent( QKeyEvent* event )

    void updateLabels()
    void updateWidgets()
    void updateComboBoxes()
    void initializeProperties( bool currentDocumentOnly )
    void showMessage(  QString& status )
    void setState( SearchWidget.InputField field, state )
    bool searchFile( bool forward, incremental )
    bool replaceFile( bool all )

protected slots:
    void searchThread_stateChanged()
    void searchThread_progressChanged( int value, total )
    void replaceThread_stateChanged()
    void replaceThread_openedFileHandled(  QString& fileName, content, codec )
    void replaceThread_error(  QString& error )
    void search_textChanged()
    void cdUp_clicked()
    void on_pbPrevious_clicked()
    void on_pbNext_clicked()
    void on_pbSearch_clicked()
    void on_pbSearchStop_clicked()
    void on_pbReplace_clicked()
    void on_pbReplaceAll_clicked()
    void on_pbReplaceChecked_clicked()
    void on_pbReplaceCheckedStop_clicked()
    void on_pbBrowse_clicked()


#endif # SEARCHWIDGET_H
