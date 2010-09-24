#ifndef PENVIRONMENTVARIABLEEDITOR_H
#define PENVIRONMENTVARIABLEEDITOR_H

#include "objects/MonkeyExport.h"
#include "ui_pEnvironmentVariableEditor.h"

class Q_MONKEY_EXPORT pEnvironmentVariableEditor : public QDialog, public Ui::pEnvironmentVariableEditor
{
	Q_OBJECT

public:
	pEnvironmentVariableEditor( QWidget* parent = 0, const QString& name = QString::null, const QString& value = QString::null );

	QString name() const;
	QString value() const;
};

#endif // PENVIRONMENTVARIABLEEDITOR_H
