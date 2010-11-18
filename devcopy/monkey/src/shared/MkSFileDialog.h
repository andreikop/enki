#ifndef MKSFILEDIALOG_H
#define MKSFILEDIALOG_H

#include "widgets/pFileDialog.h"

class XUPAddFiles
class XUPItem

class Q_MONKEY_EXPORT MkSFileDialog : public pFileDialog
    Q_OBJECT
    
public:
    MkSFileDialog( parent = 0, caption = QString(), directory = QString(), filter = QString(), textCodecEnabled = True, openReadOnlyEnabled = False )
    
    static pFileDialogResult getOpenFileName( parent = 0, caption = QString(), dir = QString(), filter = QString(), enabledTextCodec = True, enabledOpenReadOnly = True, selectedFilter = 0, options = 0 )
    static pFileDialogResult getOpenFileNames( parent = 0, caption = QString(), dir = QString(), filter = QString(), enabledTextCodec = True, enabledOpenReadOnly = True, selectedFilter = 0, options = 0 )
    static pFileDialogResult getSaveFileName( parent = 0, caption = QString(), dir = QString(), filter = QString(), enabledTextCodec = True, selectedFilter = 0, options = 0 )
    
    static pFileDialogResult getOpenProjects( parent = 0 )
    static pFileDialogResult getProjectAddFiles( parent = 0, allowChooseScope = True )
    static pFileDialogResult getNewEditorFile( parent = 0 )

protected:
    XUPAddFiles* mAddFiles

protected slots:
    void currentScopeChanged( XUPItem* scope )


#endif # MKSFILEDIALOG_H
