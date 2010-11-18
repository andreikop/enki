'''***************************************************************************
**
** Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
** Contact: Nokia Corporation (qt-info@nokia.com)
**
** This file is part of the Qt Designer of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:LGPL$
** No Commercial Usage
** This file contains pre-release code and may not be distributed.
** You may use self file in accordance with the terms and conditions
** contained in the Technology Preview License Agreement accompanying
** self package.
**
** GNU Lesser General Public License Usage
** Alternatively, file may be used under the terms of the GNU Lesser
** General Public License version 2.1 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPL included in the
** packaging of self file.  Please review the following information to
** ensure the GNU Lesser General Public License version 2.1 requirements
** will be met: http:#www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** In addition, a special exception, gives you certain
** additional rights.  These rights are described in the Nokia Qt LGPL
** Exception version 1.1, in the file LGPL_EXCEPTION.txt in self
** package.
**
** If you have questions regarding the use of self file, contact
** Nokia at qt-info@nokia.com.
**
**
**
**
**
**
**
**
** $QT_END_LICENSE$
**
***************************************************************************'''

#
#  W A R N I N G
#  -------------
#
# This file is not part of the Qt API.  It exists for the convenience
# of Qt Designer.  This header
# file may change from version to version without notice, even be removed.
#
# We mean it.
#

#ifndef PREVIEWMANAGER_H
#define PREVIEWMANAGER_H

#include "shared_global_p.h"

#include <QtCore/QObject>
#include <QtCore/QString>
#include <QtCore/QSharedDataPointer>

QT_BEGIN_NAMESPACE

class QDesignerFormWindowInterface
class QWidget
class QPixmap
class QAction
class QActionGroup
class QMenu
class QWidget
class QDesignerSettingsInterface

namespace qdesigner_internal
# ----------- PreviewConfiguration

class PreviewConfigurationData

class QDESIGNER_SHARED_EXPORT PreviewConfigurationpublic:
    PreviewConfiguration()
    explicit PreviewConfiguration( QString &style,
                                   QString &applicationStyleSheet = QString(),
                                   QString &deviceSkin = QString())

    PreviewConfiguration( PreviewConfiguration&)
    PreviewConfiguration& operator=( PreviewConfiguration&)
    ~PreviewConfiguration()

    QString style()
    void setStyle( QString &)

    # Style sheet to prepend (to simulate the effect od QApplication.setSyleSheet()).
    QString applicationStyleSheet()
    void setApplicationStyleSheet( QString &)

    QString deviceSkin()
    void setDeviceSkin( QString &)

    void clear()
    void toSettings( QString &prefix, *settings)
    void fromSettings( QString &prefix, *settings)

private:
    QSharedDataPointer<PreviewConfigurationData> m_d


QDESIGNER_SHARED_EXPORT bool operator<( PreviewConfiguration &pc1, &pc2)
QDESIGNER_SHARED_EXPORT bool operator==( PreviewConfiguration &pc1, &pc2)
QDESIGNER_SHARED_EXPORT bool operator!=( PreviewConfiguration &pc1, &pc2)

# ----------- Preview window manager.
# Maintains a list of preview widgets with their associated form windows and configuration.

class PreviewManagerPrivate

class QDESIGNER_SHARED_EXPORT PreviewManager : public QObject
    Q_OBJECT
public:

    enum PreviewMode        # Modal preview. Do not use on Macs as dialogs would have no close button
        ApplicationModalPreview,
        # Non modal previewing of one form in different configurations (closes if form window changes)
        SingleFormNonModalPreview,
        # Non modal previewing of several forms in different configurations
        MultipleFormNonModalPreview

    explicit PreviewManager(PreviewMode mode, *parent)
    virtual ~PreviewManager()

    # Show preview. Raise existing preview window if there is one with a matching
    # configuration, create a preview.
    QWidget *showPreview( QDesignerFormWindowInterface *, &pc, deviceProfileIndex '''=-1''', *errorMessage)
    # Convenience that creates a preview using a configuration taken from the settings.
    QWidget *showPreview( QDesignerFormWindowInterface *, &style, deviceProfileIndex '''=-1''', *errorMessage)
    QWidget *showPreview( QDesignerFormWindowInterface *, &style, *errorMessage)

    int previewCount()

    # Create a pixmap for printing.
    QPixmap createPreviewPixmap( QDesignerFormWindowInterface *fw, &pc, deviceProfileIndex '''=-1''', *errorMessage)
    # Convenience that creates a pixmap using a configuration taken from the settings.
    QPixmap createPreviewPixmap( QDesignerFormWindowInterface *fw, &style, deviceProfileIndex '''=-1''', *errorMessage)
    QPixmap createPreviewPixmap( QDesignerFormWindowInterface *fw, &style, *errorMessage)

    virtual bool eventFilter(QObject *watched, *event)

public slots:
    void closeAllPreviews()

signals:
    void firstPreviewOpened()
    void lastPreviewClosed()

private slots:
    void slotZoomChanged(int)

private:

    virtual Qt.WindowFlags previewWindowFlags( QWidget *widget)
    virtual QWidget *createDeviceSkinContainer( QDesignerFormWindowInterface *)

    QWidget *raise( QDesignerFormWindowInterface *, &pc)
    QWidget *createPreview( QDesignerFormWindowInterface *,
                            PreviewConfiguration &pc,
                           int deviceProfileIndex ''' = -1 ''',
                           QString *errorMessage,
                           '''Disabled by default, <0 '''
                           initialZoom = -1)

    void updatePreviewClosed(QWidget *w)

    PreviewManagerPrivate *d

    PreviewManager( PreviewManager &other)
    PreviewManager &operator =( PreviewManager &other)



QT_END_NAMESPACE

#endif # PREVIEWMANAGER_H
