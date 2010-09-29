#ifndef UISETTINGSQMAKE_H
#define UISETTINGSQMAKE_H

#include "ui_UISettingsQMake.h"

class QtVersionManager

class UISettingsQMake : public QWidget, Ui.UISettingsQMake
    Q_OBJECT
    
public:
    UISettingsQMake( parent = 0 )

protected:
    QtVersionManager* mQtManager

protected slots:
    void tbAdd_clicked()
    void tbRemove_clicked()
    void tbClear_clicked()
    void tbUp_clicked()
    void tbDown_clicked()
    void on_tbDefaultQtVersion_clicked()
    void qtVersionChanged()
    void on_tbQtVersionPath_clicked()
    void on_tbQtVersionQMakeSpec_clicked()
    void lw_currentItemChanged( QListWidgetItem* current, previous )
    void loadSettings()
    void on_dbbButtons_helpRequested()
    void on_dbbButtons_clicked( QAbstractButton* button )


#endif # UISETTINGSQMAKE_H
