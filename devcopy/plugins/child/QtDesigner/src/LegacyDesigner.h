#ifndef LEGACYDESIGNER_H
#define LEGACYDESIGNER_H

#include <QDesignerFormWindowInterface>

namespace LegacyDesigner
{
    QStringList defaultPluginPaths();
    Qt::WindowFlags previewWindowFlags( const QWidget* widget );
    QWidget* fakeContainer( QWidget* w );
    QWidget* createPreview( const QDesignerFormWindowInterface* fw, const QString& style, QString* errorMessage );
    QPixmap createPreviewPixmap( const QDesignerFormWindowInterface* fw, const QString& style, QString* errorMessage );
    QWidget* showPreview( const QDesignerFormWindowInterface* fw, const QString& style, QString* errorMessage );
};

#endif // LEGACYDESIGNER_H
