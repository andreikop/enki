#ifndef MKSQTDOCINSTALLER_H
#define MKSQTDOCINSTALLER_H

#include <QObject>

class QHelpEngine
class QtDocInstaller

class MkSQtDocInstaller : public QObject
    Q_OBJECT

public:
    MkSQtDocInstaller( engine = 0 )

    static QString collectionFileDirectory( createDir = False, cacheDir = QString() )
    static QString defaultHelpCollectionFileName()

protected:
    QHelpEngine* mHelpEngine
    QtDocInstaller* mQtDocInstaller

public slots:
    bool checkDocumentation()

protected slots:
    bool initHelpDB()
    void lookForNewQtDocumentation()
    void displayInstallationError(  QString& errorMessage )
    void qtDocumentationInstalled( bool newDocsInstalled )


#endif # MKSQTDOCINSTALLER_H
