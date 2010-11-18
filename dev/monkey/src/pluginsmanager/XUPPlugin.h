#ifndef XUPPLUGIN_H
#define XUPPLUGIN_H

#include "BasePlugin.h"

class XUPProjectItem;

class Q_MONKEY_EXPORT XUPPlugin : public BasePlugin
{
public:
	virtual bool editProject( XUPProjectItem* project ) = 0;
};

Q_DECLARE_INTERFACE( XUPPlugin, "org.monkeystudio.MonkeyStudio.XUPPlugin/1.0" )

#endif // XUPPLUGIN_H
