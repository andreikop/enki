#ifndef SEARCHRESULTSMODEL_H
#define SEARCHRESULTSMODEL_H

#include <QAbstractItemModel>
#include <QFileInfo>
#include <QPoint>
#include <QStringList>
#include <QDir>

class SearchThread

class SearchResultsModel : public QAbstractItemModel
    Q_OBJECT
    friend class SearchWidget

public:
    struct Result
        Result(  _fileName = QString.null, _capture = QString.null,
                 _position = QPoint(), _offset = -1, _length = 0, _checkable = False,
                _checkState = Qt.Unchecked, _enabled = True, _capturedTexts = QStringList() )
            fileName = _fileName
            capture = _capture
            position = _position
            offset = _offset
            length = _length
            checkable = _checkable
            checkState = _checkState
            enabled = _enabled
            capturedTexts = _capturedTexts


        bool operator==(  SearchResultsModel.Result& other )
            return fileName == other.fileName and
                   #capture == other.capture and
                   position == other.position and
                   offset == other.offset and
                   length == other.length and
                   '''checkable == other.checkable and
                   checkState == other.checkState and
                   enabled == other.enabled'''
                   capturedTexts == other.capturedTexts


        QString fileName
        QString capture
        QPoint position
        int offset
        int length
        bool checkable
        Qt.CheckState checkState
        bool enabled
        QStringList capturedTexts


    typedef QList<SearchResultsModel.Result*> ResultList

    enum CustomRoles
        EnabledRole = Qt.UserRole


    SearchResultsModel( SearchThread* searchThread, parent = 0 )

    virtual int columnCount(  parent = QModelIndex() )
    virtual QVariant data(  QModelIndex& index, role = Qt.DisplayRole )
    virtual QModelIndex index( int row, column, parent = QModelIndex() )
    virtual QModelIndex parent(  QModelIndex& index )
    virtual int rowCount(  parent = QModelIndex() )

    virtual Qt.ItemFlags flags(  QModelIndex& index )
    virtual bool hasChildren(  parent = QModelIndex() )
    virtual bool setData(  QModelIndex& index, value, role = Qt.EditRole )

    QModelIndex index( SearchResultsModel.Result* result )
    SearchResultsModel.Result* result(  QModelIndex& index )

     QList<SearchResultsModel.ResultList>& results()

protected:
    int mRowCount
    QDir mSearchDir
    mutable QHash<QString, mParents; # fileName, result
    mutable SearchResultsModel.ResultList mParentsList; # ordered parents
    mutable QList<SearchResultsModel.ResultList> mResults; # parents children
    SearchThread* mSearchThread

public slots:
    void clear()

protected slots:
    void thread_reset()
    void thread_resultsAvailable(  QString& fileName, results )
    void thread_resultsHandled(  QString& fileName, results )

signals:
    void firstResultsAvailable()


#endif # SEARCHRESULTSMODEL_H
