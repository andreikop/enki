#ifndef PCONSOLEMANAGERSTEPMODEL_H
#define PCONSOLEMANAGERSTEPMODEL_H

#include <QAbstractItemModel>

#include <objects/MonkeyExport.h>

#include "pConsoleManagerStep.h"

class Q_MONKEY_EXPORT pConsoleManagerStepModel : public QAbstractItemModel
{
	Q_OBJECT
	
public:
	pConsoleManagerStepModel( QObject* parent = 0 );
	virtual ~pConsoleManagerStepModel();
	
	virtual int columnCount( const QModelIndex& parent = QModelIndex() ) const;
	virtual QVariant data( const QModelIndex& index, int role = Qt::DisplayRole ) const;
	virtual QModelIndex index( int row, int column, const QModelIndex& parent = QModelIndex() ) const;
	virtual QModelIndex parent( const QModelIndex& index ) const;
	virtual int rowCount( const QModelIndex& parent = QModelIndex() ) const;
	
	virtual bool hasChildren( const QModelIndex& parent = QModelIndex() ) const;
	
	QModelIndex index( const pConsoleManagerStep& step ) const;
	pConsoleManagerStep step( const QModelIndex& index ) const;
	
	QModelIndex nextWarning( const QModelIndex& fromIndex ) const;
	QModelIndex nextError( const QModelIndex& fromIndex ) const;

public slots:
	void clear();
	void appendStep( const pConsoleManagerStep& step );
	void appendSteps( const pConsoleManagerStepList& steps );

protected:
	mutable pConsoleManagerStepList mSteps;
	uint mWarnings;
	uint mErrors;
};

#endif // PCONSOLEMANAGERSTEPMODEL_H
