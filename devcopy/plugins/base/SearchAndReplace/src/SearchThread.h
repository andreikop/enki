#ifndef SEARCHTHREAD_H
#define SEARCHTHREAD_H

#include <QThread>
#include <QMutex>
#include <QDir>

#include "SearchWidget.h"
#include "SearchResultsModel.h"

class SearchThread : public QThread
    Q_OBJECT

public:
    SearchThread( parent = 0 )
    virtual ~SearchThread()

    void search(  SearchAndReplace.Properties& properties )
    void stop()

    SearchAndReplace.Properties* properties()

protected:
    static int mMaxTime
    SearchAndReplace.Properties mProperties
    QMutex mMutex
    bool mReset
    bool mExit

    QStringList getFiles( QDir fromDir, filters, recursive )
    QStringList getFilesToScan()
    QString fileContent(  QString& fileName )
    void search(  QString& fileName, content )
    virtual void run()

public slots:
    void clear()

signals:
    void reset()
    void resultsAvailable(  QString& fileName, results )
    void progressChanged( int value, total )


#endif # SEARCHTHREAD_H
