'''***************************************************************************
**
** Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
** Contact: Qt Software Information (qt-info@nokia.com)
**
** This file is part of the Qt Designer of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:LGPL$
** Commercial Usage
** Licensees holding valid Qt Commercial licenses may use self file in
** accordance with the Qt Commercial License Agreement provided with the
** Software or, alternatively, accordance with the terms contained in
** a written agreement between you and Nokia.
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
** additional rights. These rights are described in the Nokia Qt LGPL
** Exception version 1.0, in the file LGPL_EXCEPTION.txt in self
** package.
**
** GNU General Public License Usage
** Alternatively, file may be used under the terms of the GNU
** General Public License version 3.0 as published by the Free Software
** Foundation and appearing in the file LICENSE.GPL included in the
** packaging of self file.  Please review the following information to
** ensure the GNU General Public License version 3.0 requirements will be
** met: http:#www.gnu.org/copyleft/gpl.html.
**
** If you are unsure which license is appropriate for your use, please
** contact the sales department at qt-sales@nokia.com.
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

#ifndef DEVICEPROFILE_H
#define DEVICEPROFILE_H

#include "shared_global_p.h"

#include <QtCore/QString>
#include <QtCore/QSharedDataPointer>

QT_BEGIN_NAMESPACE

class QDesignerFormEditorInterface
class QWidget
class QStyle

namespace qdesigner_internal

class DeviceProfileData

''' DeviceProfile for embedded design. They influence
 * default properties (for example, fonts), and
 * style of the form. This class represents a device
 * profile. '''

class QDESIGNER_SHARED_EXPORT DeviceProfile
public:
    DeviceProfile()

    DeviceProfile( DeviceProfile&)
    DeviceProfile& operator=( DeviceProfile&)
    ~DeviceProfile()

    void clear()

    # Device name
    QString name()
    void setName( QString &)

    # System settings active
    bool isEmpty()

    # Default font family of the embedded system
    QString fontFamily()
    void setFontFamily( QString &)

    # Default font size of the embedded system
    int fontPointSize()
    void setFontPointSize(int p)

    # Display resolution of the embedded system
    int dpiX()
    void setDpiX(int d)
    int dpiY()
    void setDpiY(int d)

    # Style
    QString style()
    void setStyle( QString &)

    # Initialize from desktop system
    void fromSystem()

    static void systemResolution(int *dpiX, *dpiY)
    static void widgetResolution( QWidget *w, *dpiX, *dpiY)

    bool equals( DeviceProfile& rhs)

    # Apply to form/preview (using font inheritance)
    enum ApplyMode
        ''' Pre-Apply to parent widget of form being edited: Apply font
         * and make use of property inheritance to be able to modify the
         * font property freely. '''
        ApplyFormParent,
        ''' Post-Apply to preview widget: Change only inherited font
         * sub properties. '''
        ApplyPreview

    void apply( QDesignerFormEditorInterface *core, *widget, am)

    static void applyDPI(int dpiX, dpiY, *widget)

    QString toString()

    QString toXml()
    bool fromXml( QString &xml, *errorMessage)

private:
    QSharedDataPointer<DeviceProfileData> m_d


inline bool operator==( DeviceProfile &s1, &s2)
    return s1.equals(s2)

inline bool operator!=( DeviceProfile &s1, &s2)
    return not s1.equals(s2)





QT_END_NAMESPACE

#endif # DEVICEPROFILE_H
