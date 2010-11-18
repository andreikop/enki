#ifndef LEGACYDESIGNER_H
#define LEGACYDESIGNER_H

#include <QDesignerFormWindowInterface>

namespace LegacyDesigner
    QStringList defaultPluginPaths()
    Qt.WindowFlags previewWindowFlags(  QWidget* widget )
    QWidget* fakeContainer( QWidget* w )
    QWidget* createPreview(  QDesignerFormWindowInterface* fw, style, errorMessage )
    QPixmap createPreviewPixmap(  QDesignerFormWindowInterface* fw, style, errorMessage )
    QWidget* showPreview(  QDesignerFormWindowInterface* fw, style, errorMessage )


#endif # LEGACYDESIGNER_H
