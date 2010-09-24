#ifndef PENVIRONMENTVARIABLESMODEL_H
#define PENVIRONMENTVARIABLESMODEL_H

#include "objects/MonkeyExport.h"

#include <QAbstractItemModel>

class Q_MONKEY_EXPORT pEnvironmentVariablesModel : public QAbstractItemModel
{
	Q_OBJECT

public:
	struct Variable
	{
		Variable( const QString& _name = QString::null, const QString& _value = QString::null, bool _enabled = false )
		{
			name = _name;
			value = _value;
			enabled = _enabled;
		}

		QString name;
		QString value;
		bool enabled;
	};

	typedef QHash<QString, pEnvironmentVariablesModel::Variable> Variables;
	typedef QList<pEnvironmentVariablesModel::Variable*> VariableList;

	pEnvironmentVariablesModel( QObject* parent = 0 );

	virtual int columnCount( const QModelIndex& parent = QModelIndex() ) const;
	virtual QVariant data( const QModelIndex& index, int role = Qt::DisplayRole ) const;
	virtual QModelIndex index( int row, int column, const QModelIndex& parent = QModelIndex() ) const;
	virtual QModelIndex parent( const QModelIndex& index ) const;
	virtual int rowCount( const QModelIndex& parent = QModelIndex() ) const;

	virtual QVariant headerData( int section, Qt::Orientation orientation, int role = Qt::DisplayRole ) const;
	virtual bool hasChildren( const QModelIndex& parent = QModelIndex() ) const;
	virtual Qt::ItemFlags flags( const QModelIndex& index ) const;
	virtual bool setData( const QModelIndex& index, const QVariant& value, int role = Qt::EditRole );

	QModelIndex index( const QString& name, int column = 0 ) const;
	pEnvironmentVariablesModel::Variable variable( const QModelIndex& index ) const;

	const pEnvironmentVariablesModel::Variables& variables() const;
	const pEnvironmentVariablesModel::Variables& defaultVariables() const;
	QStringList variables( bool keepDisabled ) const;
	pEnvironmentVariablesModel::Variable variable( const QString& name ) const;
	bool contains( const QString& name ) const;
	bool isEmpty() const;
	
	static pEnvironmentVariablesModel::Variables stringListToVariables( const QStringList& variables );
	static QStringList variablesToStringList( const pEnvironmentVariablesModel::Variables& variables, bool keepDisabled );

public slots:
	void setVariables( const pEnvironmentVariablesModel::Variables& variables, bool setDefault );
	void setDefaultVariables( const pEnvironmentVariablesModel::Variables& variables );
	void setVariables( const QStringList& variables, bool setDefault );
	void setVariable( const QString& name, const pEnvironmentVariablesModel::Variable& variable );
	void removeVariable( const QString& name );
	void clearVariables();
	void resetVariablesToDefault();
	void resetVariablesToSystem( bool setDefault );

protected:
	mutable int mRowCount;
	mutable pEnvironmentVariablesModel::Variables mDefaultVariables;
	mutable pEnvironmentVariablesModel::Variables mVariables;
	mutable pEnvironmentVariablesModel::VariableList mOrder;

signals:
	void defaultVariablesChanged();
};

Q_DECLARE_METATYPE( pEnvironmentVariablesModel::Variable );
Q_DECLARE_METATYPE( pEnvironmentVariablesModel::Variables )

#endif // PENVIRONMENTVARIABLESMODEL_H
