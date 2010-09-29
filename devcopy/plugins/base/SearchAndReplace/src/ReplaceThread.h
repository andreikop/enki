#ifndef REPLACETHREAD_H
#define REPLACETHREAD_H

#include <QThread>
#include <QMutex>

#include "SearchAndReplace.h"
#include "SearchResultsModel.h"

class ReplaceThread : public QThread
    Q_OBJECT
    
public:
    ReplaceThread( parent = 0 )
    virtual ~ReplaceThread()
    
    void replace(  SearchAndReplace.Properties& properties,  QHash<QString, results )
    void stop()

protected:
    static int mMaxTime
    SearchAndReplace.Properties mProperties
    QHash<QString, mResults
    QMutex mMutex
    bool mReset
    bool mExit
    
    void saveContent(  QString& fileName, content, codec )
    QString fileContent(  QString& fileName )
    void replace(  QString& fileName, content )
    void run()

signals:
    void resultsHandled(  QString& fileName, results )
    void openedFileHandled(  QString& fileName, content, codec )
    void error(  QString& error )


#endif # REPLACETHREAD_H
