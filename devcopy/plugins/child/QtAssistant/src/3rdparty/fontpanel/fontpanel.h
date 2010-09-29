'''***************************************************************************
**
** Copyright (C) 1992-2008 Trolltech ASA. All rights reserved.
**
** This file is part of the tools applications of the Qt Toolkit.
**
** This file may be used under the terms of the GNU General Public
** License versions 2.0 or 3.0 as published by the Free Software
** Foundation and appearing in the files LICENSE.GPL2 and LICENSE.GPL3
** included in the packaging of self file.  Alternatively you may (at
** your option) use any later version of the GNU General Public
** License if such license has been publicly approved by Trolltech ASA
** (or its successors, any) and the KDE Free Qt Foundation. In
** addition, a special exception, gives you certain
** additional rights. These rights are described in the Trolltech GPL
** Exception version 1.2, can be found at
** http:#www.trolltech.com/products/qt/gplexception/ and in the file
** GPL_EXCEPTION.txt in self package.
**
** Please review the following information to ensure GNU General
** Public Licensing requirements will be met:
** http:#trolltech.com/products/qt/licenses/licensing/opensource/. If
** you are unsure which license is appropriate for your use, please
** review the following information:
** http:#trolltech.com/products/qt/licenses/licensing/licensingoverview
** or contact the sales department at sales@trolltech.com.
**
** In addition, a special exception, Trolltech, the sole
** copyright holder for Qt Designer, users of the Qt/Eclipse
** Integration plug-in the right for the Qt/Eclipse Integration to
** link to functionality provided by Qt Designer and its related
** libraries.
**
** This file is provided "AS IS" with NO WARRANTY OF ANY KIND,
** INCLUDING THE WARRANTIES OF DESIGN, AND FITNESS FOR
** A PARTICULAR PURPOSE. Trolltech reserves all rights not expressly
** granted herein.
**
** This file is provided AS IS with NO WARRANTY OF ANY KIND, THE
** WARRANTY OF DESIGN, AND FITNESS FOR A PARTICULAR PURPOSE.
**
***************************************************************************'''

#
#  W A R N I N G
#  -------------
#
# This file is not part of the Qt API.  It exists for the convenience
# of the Qt tools.  This header
# file may change from version to version without notice, even be removed.
#
# We mean it.
#

#ifndef FONTPANEL_H
#define FONTPANEL_H

#include <QtGui/QGroupBox>
#include <QtGui/QFont>
#include <QtGui/QFontDatabase>

QT_BEGIN_NAMESPACE

class QComboBox
class QFontComboBox
class QTimer
class QLineEdit

class FontPanel: public QGroupBox
    Q_OBJECT
public:
    FontPanel(QWidget *parentWidget = 0)

    QFont selectedFont()
    void setSelectedFont( QFont &)

    QFontDatabase.WritingSystem writingSystem()
    void setWritingSystem(QFontDatabase.WritingSystem ws)

private slots:
    void slotWritingSystemChanged(int)
    void slotFamilyChanged( QFont &)
    void slotStyleChanged(int)
    void slotPointSizeChanged(int)
    void slotUpdatePreviewFont()

private:
    QString family()
    QString styleString()
    int pointSize()
    int closestPointSizeIndex(int ps)

    void updateWritingSystem(QFontDatabase.WritingSystem ws)
    void updateFamily( QString &family)
    void updatePointSizes( QString &family, &style)
    void delayedPreviewFontUpdate()

    QFontDatabase m_fontDatabase
    QLineEdit *m_previewLineEdit
    QComboBox *m_writingSystemComboBox
    QFontComboBox* m_familyComboBox
    QComboBox *m_styleComboBox
    QComboBox *m_pointSizeComboBox
    QTimer *m_previewFontUpdateTimer


QT_END_NAMESPACE

#endif # FONTPANEL_H
