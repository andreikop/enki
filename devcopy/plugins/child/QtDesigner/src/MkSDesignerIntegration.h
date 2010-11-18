#ifndef MKSDESIGNERINTEGRATION_H
#define MKSDESIGNERINTEGRATION_H

#include "qdesigner_integration_p.h"

class QDesignerFormEditorInterface

class MkSDesignerIntegration : public qdesigner_internal.QDesignerIntegration
    Q_OBJECT
    
public:
    MkSDesignerIntegration( QDesignerFormEditorInterface* core, parent = 0 )
    
    virtual QWidget* containerWindow( QWidget* widget )


#endif # MKSDESIGNERINTEGRATION_H
