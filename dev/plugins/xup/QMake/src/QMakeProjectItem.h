#ifndef QMAKEPROJECTITEM_H
#define QMAKEPROJECTITEM_H

#include <xupmanager/core/XUPProjectItem.h>

class QMakeProjectItem : public XUPProjectItem
{
	Q_OBJECT
	
public:
	enum ProjectType { QMakeProject = 1 };
	
	QMakeProjectItem();
	virtual ~QMakeProjectItem();
	
	virtual QString toString() const;
	inline virtual int projectType() const { return QMakeProjectItem::QMakeProject; }
	virtual void registerProjectType() const;
	inline virtual XUPProjectItem* newProject() const { return new QMakeProjectItem(); }
	virtual QString getVariableContent( const QString& variableName );
	virtual bool analyze( XUPItem* item );
	virtual bool open( const QString& fileName, const QString& codec );
	virtual bool save();
	virtual QString targetFilePath( bool allowToAskUser = false, XUPProjectItem::TargetType type = XUPProjectItem::DefaultTarget, XUPProjectItem::PlatformType = XUPProjectItem::CurrentPlatform );
	
	virtual BuilderPlugin* builder( const QString& plugin = QString() ) const;
	virtual DebuggerPlugin* debugger( const QString& plugin = QString() ) const;
	virtual InterpreterPlugin* interpreter( const QString& plugin = QString() ) const;
	virtual void installCommands();

protected:
	bool handleSubdirs( XUPItem* subdirs );
};

#endif // QMAKEPROJECTITEM_H
