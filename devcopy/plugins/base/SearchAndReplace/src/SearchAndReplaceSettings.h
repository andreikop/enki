#ifndef SEARCHANDREPLACESETTINGS_H
#define SEARCHANDREPLACESETTINGS_H

#include "ui_SearchAndReplaceSettings.h"
#include "SearchAndReplace.h"

class SearchAndReplaceSettings : public QWidget, public Ui::SearchAndReplaceSettings
{
    Q_OBJECT

public:
    SearchAndReplaceSettings( SearchAndReplace* plugin, QWidget* parent = 0 );
    virtual ~SearchAndReplaceSettings();

protected:
    SearchAndReplace* mPlugin;
    
    void loadSettings( const SearchAndReplace::Settings& settings );
    
protected slots:
    virtual void restoreDefault();
    virtual void reject();
    virtual void accept();
    
    void on_dbbButtons_clicked( QAbstractButton* button );
};

#endif // SEARCHANDREPLACESETTINGS_H
