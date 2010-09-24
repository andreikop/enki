'''***************************************************************************
**
** Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
** All rights reserved.
** Contact: Nokia Corporation (qt-info@nokia.com)
**
** This file is part of the Qt Assistant of the Qt Toolkit.
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
** In addition, a special exception, gives you certain additional
** rights.  These rights are described in the Nokia Qt LGPL Exception
** version 1.1, in the file LGPL_EXCEPTION.txt in self package.
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

#include "preferencesdialog.h"
#include "filternamedialog.h"
#include "installdialog.h"
#include "fontpanel.h"
##include "centralwidget.h"
##include "aboutdialog.h"

#include <QtAlgorithms>

#include <QtGui/QHeaderView>
#include <QtGui/QFileDialog>
#include <QtGui/QMessageBox>
#include <QtGui/QMenu>
#include <QtGui/QFontDatabase>
#include <QtGui/QApplication>
#include <QtGui/QDesktopWidget>

#include <QtHelp/QHelpEngineCore>

QT_BEGIN_NAMESPACE

PreferencesDialog.PreferencesDialog(QHelpEngineCore *helpEngine, *parent)
        : QDialog(parent)
        , m_helpEngine(helpEngine)
        , m_appFontChanged(False)
        , m_browserFontChanged(False)
    m_ui.setupUi(self)

    connect(m_ui.buttonBox.button(QDialogButtonBox.Ok), SIGNAL(clicked()),
            self, SLOT(applyChanges()))
    connect(m_ui.buttonBox.button(QDialogButtonBox.Cancel), SIGNAL(clicked()),
            self, SLOT(reject()))

    QLatin1String key("EnableFilterFunctionality")
    m_hideFiltersTab = not m_helpEngine.customValue(key, True).toBool()

    key = QLatin1String("EnableDocumentationManager")
    m_hideDocsTab = not m_helpEngine.customValue(key, True).toBool()

    if not m_hideFiltersTab:
        m_ui.attributeWidget.header().hide()
        m_ui.attributeWidget.setRootIsDecorated(False)

        connect(m_ui.attributeWidget, SIGNAL(itemChanged(QTreeWidgetItem*, int)),
                self, SLOT(updateFilterMap()))

        connect(m_ui.filterWidget,
                SIGNAL(currentItemChanged(QListWidgetItem*, QListWidgetItem*)), self,
                SLOT(updateAttributes(QListWidgetItem*)))

        connect(m_ui.filterAddButton, SIGNAL(clicked()), self,
                SLOT(addFilter()))
        connect(m_ui.filterRemoveButton, SIGNAL(clicked()), self,
                SLOT(removeFilter()))

        updateFilterPage()

    else:
        m_ui.tabWidget.removeTab(m_ui.tabWidget.indexOf(m_ui.filtersTab))


    if not m_hideDocsTab:
        connect(m_ui.docAddButton, SIGNAL(clicked()), self,
                SLOT(addDocumentationLocal()))
        connect(m_ui.docRemoveButton, SIGNAL(clicked()), self,
                SLOT(removeDocumentation()))

        m_docsBackup = m_helpEngine.registeredDocumentations()
        m_ui.registeredDocsListWidget.addItems(m_docsBackup)

    else:
        m_ui.tabWidget.removeTab(m_ui.tabWidget.indexOf(m_ui.docsTab))


    updateFontSettingsPage()
    updateOptionsPage()


PreferencesDialog.~PreferencesDialog()
    QLatin1String key("")
    if m_appFontChanged:
        key = QLatin1String("appFont")
        m_helpEngine.setCustomValue(key, m_appFontPanel.selectedFont())

        key = QLatin1String("useAppFont")
        m_helpEngine.setCustomValue(key, m_appFontPanel.isChecked())

        key = QLatin1String("appWritingSystem")
        m_helpEngine.setCustomValue(key, m_appFontPanel.writingSystem())


    if m_browserFontChanged:
        key = QLatin1String("browserFont")
        m_helpEngine.setCustomValue(key, m_browserFontPanel.selectedFont())

        key = QLatin1String("useBrowserFont")
        m_helpEngine.setCustomValue(key, m_browserFontPanel.isChecked())

        key = QLatin1String("browserWritingSystem")
        m_helpEngine.setCustomValue(key, m_browserFontPanel.writingSystem())


    if m_appFontChanged or m_browserFontChanged:
        updateApplicationFont.emit()
        updateBrowserFont.emit()


    homePage = m_ui.homePageLineEdit.text()
    if homePage.isEmpty():
        homePage = QLatin1String("help")
    m_helpEngine.setCustomValue(QLatin1String("homepage"), homePage)

    option = m_ui.helpStartComboBox.currentIndex()
    m_helpEngine.setCustomValue(QLatin1String("StartOption"), option)


def showDialog(self):
    if exec() != Accepted:
        m_appFontChanged = m_browserFontChanged = False


def updateFilterPage(self):
    if not m_helpEngine:
        return

    m_ui.filterWidget.clear()
    m_ui.attributeWidget.clear()

    QHelpEngineCore help(m_helpEngine.collectionFile(), 0)
    help.setupData()
    m_filterMapBackup.clear()
     filters = help.customFilters()
    foreach ( QString &filter, filters)
        atts = help.filterAttributes(filter)
        m_filterMapBackup.insert(filter, atts)
        if not m_filterMap.contains(filter):
            m_filterMap.insert(filter, atts)


    m_ui.filterWidget.addItems(m_filterMap.keys())

    foreach ( QString &a, help.filterAttributes())
    QTreeWidgetItem(m_ui.attributeWidget, QStringList() << a)

    if m_filterMap.keys().count():
        m_ui.filterWidget.setCurrentRow(0)


def updateAttributes(self, *item):
    QStringList checkedList
    if item:
        checkedList = m_filterMap.value(item.text())
    QTreeWidgetItem *itm
    for (i = 0; i < m_ui.attributeWidget.topLevelItemCount(); ++i)
        itm = m_ui.attributeWidget.topLevelItem(i)
        if checkedList.contains(itm.text(0)):
            itm.setCheckState(0, Qt.Checked)
        else:
            itm.setCheckState(0, Qt.Unchecked)



def updateFilterMap(self):
    if not m_ui.filterWidget.currentItem():
        return
    filter = m_ui.filterWidget.currentItem().text()
    if not m_filterMap.contains(filter):
        return

    QStringList newAtts
    QTreeWidgetItem *itm = 0
    for (i = 0; i < m_ui.attributeWidget.topLevelItemCount(); ++i)
        itm = m_ui.attributeWidget.topLevelItem(i)
        if itm.checkState(0) == Qt.Checked:
            newAtts.append(itm.text(0))

    m_filterMap[filter] = newAtts


def addFilter(self):
    FilterNameDialog dia(self)
    if dia.exec() == QDialog.Rejected:
        return

    filterName = dia.filterName()
    if not m_filterMap.contains(filterName):
        m_filterMap.insert(filterName, QStringList())
        m_ui.filterWidget.addItem(filterName)


    QList<QListWidgetItem*> lst = m_ui.filterWidget
                                  .findItems(filterName, Qt.MatchCaseSensitive)
    m_ui.filterWidget.setCurrentItem(lst.first())


def removeFilter(self):
    QListWidgetItem *item =
        m_ui.filterWidget .takeItem(m_ui.filterWidget.currentRow())
    if not item:
        return

    m_filterMap.remove(item.text())
    m_removedFilters.append(item.text())
    delete item
    if m_ui.filterWidget.count():
        m_ui.filterWidget.setCurrentRow(0)


def addDocumentationLocal(self):
     fileNames = QFileDialog.getOpenFileNames(self,
                                  tr("Add Documentation"), QString(), tr("Qt Compressed Help Files (*.qch)"))
    if fileNames.isEmpty():
        return

    QStringList invalidFiles
    QStringList alreadyRegistered
    foreach ( QString &fileName, fileNames)
         nameSpace = QHelpEngineCore.namespaceName(fileName)
        if nameSpace.isEmpty():
            invalidFiles.append(fileName)
            continue


        if (m_ui.registeredDocsListWidget.findItems(nameSpace,
                Qt.MatchFixedString).count())
            alreadyRegistered.append(nameSpace)
            continue


        m_helpEngine.registerDocumentation(fileName)
        m_ui.registeredDocsListWidget.addItem(nameSpace)
        m_regDocs.append(nameSpace)
        m_unregDocs.removeAll(nameSpace)


    if not invalidFiles.isEmpty() or not alreadyRegistered.isEmpty():
        QString message
        if not alreadyRegistered.isEmpty():
            foreach ( QString &ns, alreadyRegistered)
                message += tr("The namespace %1 is already registerednot ")
                           .arg(QString("<b>%1</b>").arg(ns)) + QLatin1String("<br>")

            if not invalidFiles.isEmpty():
                message.append(QLatin1String("<br>"))


        if not invalidFiles.isEmpty():
            message += tr("The specified file is not a valid Qt Help Filenot ")
            message.append(QLatin1String("<ul>"))
            foreach ( QString &file, invalidFiles)
            message += QLatin1String("<li>") + file + QLatin1String("</li>")
            message.append(QLatin1String("</ul>"))

        QMessageBox.warning(self, tr("Add Documentation"), message)


    updateFilterPage()


def removeDocumentation(self):
    foundBefore = False
    #widget = CentralWidget.instance()
    #QMap<int, openedDocList = widget.currentSourceFileList()
    QStringList values;#(openedDocList.values())

    QList<QListWidgetItem*> l = m_ui.registeredDocsListWidget.selectedItems()
    for item in l:
         ns = item.text()
        if not foundBefore and values.contains(ns):
            if (0 == QMessageBox.information(self, tr("Remove Documentation"),
                                              tr("Some documents currently opened in Assistant reference the "
                                                 "documentation you are attempting to remove. Removing the "
                                                 "documentation will close those documents."), tr("Cancel"),
                                              tr("OK"))) return
            foundBefore = True


        m_unregDocs.append(ns)
        #m_TabsToClose += openedDocList.keys(ns)
        delete m_ui.registeredDocsListWidget.takeItem(
            m_ui.registeredDocsListWidget.row(item))


    if m_ui.registeredDocsListWidget.count():
        m_ui.registeredDocsListWidget.setCurrentRow(0,
                QItemSelectionModel.ClearAndSelect)



def applyChanges(self):
    filtersWereChanged = False
    if not m_hideFiltersTab:
        if m_filterMap.count() != m_filterMapBackup.count():
            filtersWereChanged = True

        else:
            QMapIterator<QString, it(m_filterMapBackup)
            while (it.hasNext() and not filtersWereChanged)
                it.next()
                if not m_filterMap.contains(it.key()):
                    filtersWereChanged = True

                else:
                    a = it.value()
                    b = m_filterMap.value(it.key())
                    if a.count() != b.count():
                        filtersWereChanged = True

                    else:
                        QStringList.const_iterator i(a.constBegin())
                        while (i != a.constEnd())
                            if not b.contains(*i):
                                filtersWereChanged = True
                                break

                            ++i







    if filtersWereChanged:
        foreach ( QString &filter, m_removedFilters)
        m_helpEngine.removeCustomFilter(filter)
        QMapIterator<QString, it(m_filterMap)
        while (it.hasNext())
            it.next()
            m_helpEngine.addCustomFilter(it.key(), it.value())



    qSort(m_TabsToClose)
    '''
    widget = CentralWidget.instance()
    for (i = m_TabsToClose.count(); --i >= 0;)
        widget.closeTabAt(m_TabsToClose.at(i))
    if widget.availableHelpViewer()== 0:
        widget.setSource(QUrl(QLatin1String("about:blank")))
    '''
    if m_unregDocs.count():
        foreach ( QString &doc, m_unregDocs)
        m_helpEngine.unregisterDocumentation(doc)


    if filtersWereChanged or m_regDocs.count() or m_unregDocs.count():
        m_helpEngine.setupData()

    accept()


def updateFontSettingsPage(self):
    m_browserFontPanel = FontPanel(self)
    m_browserFontPanel.setCheckable(True)
    m_ui.stackedWidget_2.insertWidget(0, m_browserFontPanel)

    m_appFontPanel = FontPanel(self)
    m_appFontPanel.setCheckable(True)
    m_ui.stackedWidget_2.insertWidget(1, m_appFontPanel)

    m_ui.stackedWidget_2.setCurrentIndex(0)

     QString customSettings(tr("Use custom settings"))
    m_appFontPanel.setTitle(customSettings)

    key = QLatin1String("appFont")
    font = qVariantValue<QFont>(m_helpEngine.customValue(key))
    m_appFontPanel.setSelectedFont(font)

    key = QLatin1String("appWritingSystem")
    system = static_cast<QFontDatabase.WritingSystem>
                                          (m_helpEngine.customValue(key).toInt())
    m_appFontPanel.setWritingSystem(system)

    key = QLatin1String("useAppFont")
    m_appFontPanel.setChecked(m_helpEngine.customValue(key).toBool())

    m_browserFontPanel.setTitle(customSettings)

    key = QLatin1String("browserFont")
    font = qVariantValue<QFont>(m_helpEngine.customValue(key))
    m_browserFontPanel.setSelectedFont(font)

    key = QLatin1String("browserWritingSystem")
    system = static_cast<QFontDatabase.WritingSystem>
             (m_helpEngine.customValue(key).toInt())
    m_browserFontPanel.setWritingSystem(system)

    key = QLatin1String("useBrowserFont")
    m_browserFontPanel.setChecked(m_helpEngine.customValue(key).toBool())

    connect(m_appFontPanel, SIGNAL(toggled(bool)), self,
            SLOT(appFontSettingToggled(bool)))
    connect(m_browserFontPanel, SIGNAL(toggled(bool)), self,
            SLOT(browserFontSettingToggled(bool)))

    QList<QComboBox*> allCombos = qFindChildren<QComboBox*>(m_appFontPanel)
    for box in allCombos:
        connect(box, SIGNAL(currentIndexChanged(int)), self,
                SLOT(appFontSettingChanged(int)))


    allCombos = qFindChildren<QComboBox*>(m_browserFontPanel)
    for box in allCombos:
        connect(box, SIGNAL(currentIndexChanged(int)), self,
                SLOT(browserFontSettingChanged(int)))



def appFontSettingToggled(self, on):
    Q_UNUSED(on)
    m_appFontChanged = True


def appFontSettingChanged(self, index):
    Q_UNUSED(index)
    m_appFontChanged = True


def browserFontSettingToggled(self, on):
    Q_UNUSED(on)
    m_browserFontChanged = True


def browserFontSettingChanged(self, index):
    Q_UNUSED(index)
    m_browserFontChanged = True


def updateOptionsPage(self):
    homepage = m_helpEngine.customValue(QLatin1String("homepage"),
                       QLatin1String("")).toString()

    if homepage.isEmpty():
        homepage = m_helpEngine.customValue(QLatin1String("defaultHomepage"),
                                             QLatin1String("help")).toString()

    m_ui.homePageLineEdit.setText(homepage)

    option = m_helpEngine.customValue(QLatin1String("StartOption"),
                                           ShowLastPages).toInt()
    m_ui.helpStartComboBox.setCurrentIndex(option)

    connect(m_ui.blankPageButton, SIGNAL(clicked()), self, SLOT(setBlankPage()))
    connect(m_ui.currentPageButton, SIGNAL(clicked()), self, SLOT(setCurrentPage()))
    connect(m_ui.defaultPageButton, SIGNAL(clicked()), self, SLOT(setDefaultPage()))


def setBlankPage(self):
    m_ui.homePageLineEdit.setText(QLatin1String("about:blank"))


def setCurrentPage(self):
    QString homepage;# = CentralWidget.instance().currentSource().toString()
    if homepage.isEmpty():
        homepage = QLatin1String("help")

    m_ui.homePageLineEdit.setText(homepage)


def setDefaultPage(self):
    homepage = m_helpEngine.customValue(QLatin1String("defaultHomepage"),
                       QLatin1String("help")).toString()
    m_ui.homePageLineEdit.setText(homepage)


QT_END_NAMESPACE
