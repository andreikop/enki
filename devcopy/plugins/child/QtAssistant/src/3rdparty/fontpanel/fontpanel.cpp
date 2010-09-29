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

#include "fontpanel.h"

#include <QtGui/QLabel>
#include <QtGui/QComboBox>
#include <QtGui/QFormLayout>
#include <QtGui/QSpacerItem>
#include <QtGui/QFontComboBox>
#include <QtCore/QTimer>
#include <QtGui/QLineEdit>

QT_BEGIN_NAMESPACE

FontPanel.FontPanel(QWidget *parentWidget) :
    QGroupBox(parentWidget),
    m_previewLineEdit(new QLineEdit),
    m_writingSystemComboBox(new QComboBox),
    m_familyComboBox(new QFontComboBox),
    m_styleComboBox(new QComboBox),
    m_pointSizeComboBox(new QComboBox),
    m_previewFontUpdateTimer(0)
    setTitle(tr("Font"))

    QFormLayout *formLayout = QFormLayout(self)
    # writing systems
    m_writingSystemComboBox.setEditable(False)

    QList<QFontDatabase.WritingSystem> writingSystems = m_fontDatabase.writingSystems()
    writingSystems.push_front(QFontDatabase.Any)
    foreach (QFontDatabase.WritingSystem ws, writingSystems)
        m_writingSystemComboBox.addItem(QFontDatabase.writingSystemName(ws), QVariant(ws))
    m_writingSystemComboBox.currentIndexChanged.connect(self.slotWritingSystemChanged)
    formLayout.addRow(tr("&Writing system"), m_writingSystemComboBox)

    m_familyComboBox.currentFontChanged.connect(self.slotFamilyChanged)
    formLayout.addRow(tr("&Family"), m_familyComboBox)

    m_styleComboBox.setEditable(False)
    m_styleComboBox.currentIndexChanged.connect(self.slotStyleChanged)
    formLayout.addRow(tr("&Style"), m_styleComboBox)

    m_pointSizeComboBox.setEditable(False)
    m_pointSizeComboBox.currentIndexChanged.connect(self.slotPointSizeChanged)
    formLayout.addRow(tr("&Point size"), m_pointSizeComboBox)

    m_previewLineEdit.setReadOnly(True)
    formLayout.addRow(m_previewLineEdit)

    setWritingSystem(QFontDatabase.Any)


def selectedFont(self):
    rc = m_familyComboBox.currentFont()
     family = rc.family()
    rc.setPointSize(pointSize())
     styleDescription = styleString()
    rc.setItalic(m_fontDatabase.italic(family, styleDescription))

    rc.setBold(m_fontDatabase.bold(family, styleDescription))

    # Weight < 0 asserts...
     weight = m_fontDatabase.weight(family, styleDescription)
    if weight >= 0:
        rc.setWeight(weight)
    return rc


def setSelectedFont(self, &f):
    m_familyComboBox.setCurrentFont(f)
    if m_familyComboBox.currentIndex() < 0:        # family not in writing system - find the corresponding one?
        QList<QFontDatabase.WritingSystem> familyWritingSystems = m_fontDatabase.writingSystems(f.family())
        if familyWritingSystems.empty():
            return

        setWritingSystem(familyWritingSystems.front())
        m_familyComboBox.setCurrentFont(f)


    updateFamily(family())

     pointSizeIndex = closestPointSizeIndex(f.pointSize())
    m_pointSizeComboBox.setCurrentIndex( pointSizeIndex)

     styleString = m_fontDatabase.styleString(f)
     styleIndex = m_styleComboBox.findText(styleString)
    m_styleComboBox.setCurrentIndex(styleIndex)
    slotUpdatePreviewFont()



def writingSystem(self):
     currentIndex = m_writingSystemComboBox.currentIndex()
    if  currentIndex == -1:
        return QFontDatabase.Latin
    return static_cast<QFontDatabase.WritingSystem>(m_writingSystemComboBox.itemData(currentIndex).toInt())


def family(self):
     currentIndex = m_familyComboBox.currentIndex()
    return currentIndex != -1 ?  m_familyComboBox.currentFont().family() : QString()


def pointSize(self):
     currentIndex = m_pointSizeComboBox.currentIndex()
    return currentIndex != -1 ? m_pointSizeComboBox.itemData(currentIndex).toInt() : 9


def styleString(self):
     currentIndex = m_styleComboBox.currentIndex()
    return currentIndex != -1 ? m_styleComboBox.itemText(currentIndex) : QString()


def setWritingSystem(self, ws):
    m_writingSystemComboBox.setCurrentIndex(m_writingSystemComboBox.findData(QVariant(ws)))
    updateWritingSystem(ws)



def slotWritingSystemChanged(self, int):
    updateWritingSystem(writingSystem())
    delayedPreviewFontUpdate()


def slotFamilyChanged(self, &):
    updateFamily(family())
    delayedPreviewFontUpdate()


def slotStyleChanged(self, int):
    updatePointSizes(family(), styleString())
    delayedPreviewFontUpdate()


def slotPointSizeChanged(self, int):
    delayedPreviewFontUpdate()


def updateWritingSystem(self, ws):

    m_previewLineEdit.setText(QFontDatabase.writingSystemSample(ws))
    m_familyComboBox.setWritingSystem (ws)
    # Current font not in WS ... set index 0.
    if m_familyComboBox.currentIndex() < 0:        m_familyComboBox.setCurrentIndex(0)
        updateFamily(family())



def updateFamily(self, &family):
    # Update styles and trigger update of point sizes.
    # Try to maintain selection or select normal
     oldStyleString = styleString()

     styles = m_fontDatabase.styles(family)
     hasStyles = not styles.empty()

    m_styleComboBox.setCurrentIndex(-1)
    m_styleComboBox.clear()
    m_styleComboBox.setEnabled(hasStyles)

    normalIndex = -1
     normalStyle = QLatin1String("Normal")

    if hasStyles:        for style in styles:            # try to maintain selection or select 'normal' preferably
             newIndex = m_styleComboBox.count()
            m_styleComboBox.addItem(style)
            if oldStyleString == style:                m_styleComboBox.setCurrentIndex(newIndex)
            } else:
                if oldStyleString ==  normalStyle:
                    normalIndex = newIndex


        if m_styleComboBox.currentIndex() == -1 and normalIndex != -1:
            m_styleComboBox.setCurrentIndex(normalIndex)

    updatePointSizes(family, styleString())


def closestPointSizeIndex(self, desiredPointSize):
    #  try to maintain selection or select closest.
    closestIndex = -1
    closestAbsError = 0xFFFF

     pointSizeCount = m_pointSizeComboBox.count()
    for (i = 0; i < pointSizeCount; i++)         itemPointSize = m_pointSizeComboBox.itemData(i).toInt()
         absError = qAbs(desiredPointSize - itemPointSize)
        if absError < closestAbsError:            closestIndex  = i
            closestAbsError = absError
            if closestAbsError == 0:
                break
        } else {    # past optimum
            if absError > closestAbsError:                break



    return closestIndex



def updatePointSizes(self, &family, &styleString):
     oldPointSize = pointSize()

    QList<int> pointSizes =  m_fontDatabase.pointSizes(family, styleString)
    if pointSizes.empty():
        pointSizes = QFontDatabase.standardSizes()

     hasSizes = not pointSizes.empty()
    m_pointSizeComboBox.clear()
    m_pointSizeComboBox.setEnabled(hasSizes)
    m_pointSizeComboBox.setCurrentIndex(-1)

    #  try to maintain selection or select closest.
    if hasSizes:        QString n
        for pointSize in pointSizes:
            m_pointSizeComboBox.addItem(n.setNum(pointSize), QVariant(pointSize))
         closestIndex = closestPointSizeIndex(oldPointSize)
        if closestIndex != -1:
            m_pointSizeComboBox.setCurrentIndex(closestIndex)



def slotUpdatePreviewFont(self):
    m_previewLineEdit.setFont(selectedFont())


def delayedPreviewFontUpdate(self):
    if not m_previewFontUpdateTimer:        m_previewFontUpdateTimer = QTimer(self)
        m_previewFontUpdateTimer.timeout.connect(self.slotUpdatePreviewFont)
        m_previewFontUpdateTimer.setInterval(0)
        m_previewFontUpdateTimer.setSingleShot(True)

    if m_previewFontUpdateTimer.isActive():
        return
    m_previewFontUpdateTimer.start()


QT_END_NAMESPACE
