#ifndef PENVIRONMENTVARIABLESMANAGER_H
#define PENVIRONMENTVARIABLESMANAGER_H

#include "objects/MonkeyExport.h"
#include "pEnvironmentVariablesModel.h"

class Q_MONKEY_EXPORT pEnvironmentVariablesManager
{	
public:
	virtual ~pEnvironmentVariablesManager();
	
	bool load();
	bool save();
	
	pEnvironmentVariablesModel::Variables variables() const;
	void setVariables( const pEnvironmentVariablesModel::Variables& variables );
	
	bool mergeNewVariables( pEnvironmentVariablesModel::Variables& variables ) const;
	pEnvironmentVariablesModel::Variables mergeNewVariables( const pEnvironmentVariablesModel::Variables& variables ) const;
	bool removeUnmodifiedVariables( pEnvironmentVariablesModel::Variables& variables ) const;
	pEnvironmentVariablesModel::Variables removeUnmodifiedVariables( const pEnvironmentVariablesModel::Variables& variables ) const;
	QStringList variables( bool keepDisabled ) const;

protected:
	static const QString mSettingsKey;
	bool mInitialized;
	mutable pEnvironmentVariablesModel::Variables mVariables;
	
	virtual bool writeVariables( const pEnvironmentVariablesModel::Variables& variables ) const;
	virtual bool readVariables( pEnvironmentVariablesModel::Variables& variables ) const;
};

#endif // PENVIRONMENTVARIABLESMANAGER_H
