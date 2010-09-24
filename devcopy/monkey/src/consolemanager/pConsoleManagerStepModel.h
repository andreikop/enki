#ifndef PCONSOLEMANAGERSTEPMODEL_H
#define PCONSOLEMANAGERSTEPMODEL_H

#include <QAbstractItemModel>

#include <objects/MonkeyExport.h>

#include "pConsoleManagerStep.h"

class Q_MONKEY_EXPORT pConsoleManagerStepModel : public QAbstractItemModel
    Q_OBJECT

public:
    pConsoleManagerStepModel( parent = 0 )
    virtual ~pConsoleManagerStepModel()

    virtual int columnCount(  parent = QModelIndex() )
    virtual QVariant data(  QModelIndex& index, role = Qt.DisplayRole )
    virtual QModelIndex index( int row, column, parent = QModelIndex() )
    virtual QModelIndex parent(  QModelIndex& index )
    virtual int rowCount(  parent = QModelIndex() )

    virtual bool hasChildren(  parent = QModelIndex() )

    QModelIndex index(  pConsoleManagerStep& step )
    pConsoleManagerStep step(  QModelIndex& index )

    QModelIndex nextWarning(  QModelIndex& fromIndex )
    QModelIndex nextError(  QModelIndex& fromIndex )

public slots:
    void clear()
    void appendStep(  pConsoleManagerStep& step )
    void appendSteps(  pConsoleManagerStepList& steps )

protected:
    mutable pConsoleManagerStepList mSteps
    uint mWarnings
    uint mErrors


#endif # PCONSOLEMANAGERSTEPMODEL_H
