#ifndef TRANSLATIONDIALOG_H
#define TRANSLATIONDIALOG_H

#include "objects/MonkeyExport.h"

#include <QDialog>
#include <QHash>

class TranslationManager;
class QTreeWidgetItem;

namespace Ui {
	class TranslationDialog;
};

class Q_MONKEY_EXPORT TranslationDialog : public QDialog
{
	Q_OBJECT

public:
	TranslationDialog( TranslationManager* translationManager, QWidget* parent = 0 );
	virtual ~TranslationDialog();
	
	QString selectedLocale() const;
	
	static QString getLocale( TranslationManager* translationManager, QWidget* parent = 0 );

protected:
	Ui::TranslationDialog* ui;
	TranslationManager* mTranslationManager;
	QHash<QString, QTreeWidgetItem*> mRootItems;
	
	QTreeWidgetItem* newItem( const QLocale& locale );
	QTreeWidgetItem* rootItem( const QLocale& locale );

protected slots:
	void on_tbLocate_clicked();
	void on_tbReload_clicked();
};

#endif // TRANSLATIONDIALOG_H
