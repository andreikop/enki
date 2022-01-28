"""
uisettings --- Settings dialogue
================================
Module provides GUI to edit settings. This GUI may be used by other core modules and by plugins.

Conception
----------

Settings dialogue subsystem consists of 3 major entities:

* *UISettings.ui* GUI form. Contains of controls.
* *Option classes.

  Every object of the class links together control on GUI and option in the config file.
  It loads its option from config to GUI, and saves from GUI to config.

  config may be either :class:`enki.core.config.Config` or python dictionary
* :class:`enki.core.uisettings.UISettingsManager`. Invokes the dialogue.
  Emits signals when Plugins shall add own settings to the dialogue and when Plugins shall apply settings

.. raw:: html

    <img src="https://docs.google.com/drawings/pub?id=1jDIHjn2dNIfeJlbQniFbwA4mdPZGRX_Sxj3pL7GgYeM&amp;w=869&amp;h=594">

`Edit the diagramm <https://docs.google.com/drawings/d/1jDIHjn2dNIfeJlbQniFbwA4mdPZGRX_Sxj3pL7GgYeM/edit?hl=en_US>`_


GUI dialog invocation workflow
------------------------------

#. Enki starts. Each plugin connects themselves to **UISettingsManager.aboutToExecute**
#. An user clicks *Settings->Settings*
#. UISettings.ui are created
#. :class:`enki.core.uisettings.UISettingsManager` emits **aboutToExecute**
#. Each plugins adds own options to the dialogue
#. Each option loads its value from the :class:`enki.core.config.Config`
#. The user edits settigns
#. The user clicks *OK*
#. Each option writes it's new value to the config
#. :class:`enki.core.uisettings.UISettingsManager` emits **dialogAccepted**
#. Each plugin applies own settings

Adding new settings
-------------------

If you need to add own settings to UISettings dialog, you should:

#. Connect to UISettingsManager.aboutToExecute and UISettingsManager.dialogAccepted
#. Add controls to the dialog.
   You may edit UISettings.ui or add your controls dynamically during dialog creation
   (connect to UISettingsManager.aboutToExecute for adding dynamically)
#. Create *Option class instance for every configurable option on UISettingsManager.aboutToExecute

Classes
-------
Main classes:
    * :class:`enki.core.uisettings.UISettings` - settings dialogue. Created when shall be executed
    * :class:`enki.core.uisettings.UISettingsManager` - manager. Exists always

Option types:
    * :class:`enki.core.uisettings.CheckableOption` - bool option, CheckBox
    * :class:`enki.core.uisettings.TextOption` - string option, line edit
    * :class:`enki.core.uisettings.ListOnePerLineOption` - list of strings option, text edit
    * :class:`enki.core.uisettings.NumericOption` - numeric option, any numeric control
    * :class:`enki.core.uisettings.ColorOption` - color option, button
    * :class:`enki.core.uisettings.FontOption` - font option, button
    * :class:`enki.core.uisettings.ChoiseOption` - string from the set option, combo box

"""

import sys
import os.path

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QObject
from PyQt5.QtWidgets import QDialog, QFontDialog, QTreeWidgetItem
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5 import uic

from enki.core.core import core, DATA_FILES_PATH


def _tr(text):
    """Stub for translation
    """
    return text


def _set(config, key, value):
    """This method saves value for either core.config.Config instance and dictionary
    """
    if hasattr(config, 'set'):
        config.set(key, value)
    else:
        config[key] = value


class Option:
    """Base class for all Options. Every class knows control on UISettings form, configuration option name,
    and can load/save the option

    Do not create dirrectly, use *Option classes
    """

    def __init__(self, dialog, config, optionName, control):
        self.config = config
        self.optionName = optionName
        self.control = control
        self.dialog = dialog
        dialog.accepted.connect(self.save)
        self.load()

    def load(self):
        """Load the value from config to GUI. To be implemented by child classes
        """
        pass

    @pyqtSlot()
    def save(self):
        """Save the value from GUI to config. To be implemented by child classes
        """
        pass


class CheckableOption(Option):
    """Bool option.

    Control may be QCheckBox, QGroupBox or other control, which has .isChecked() and .setChecked()
    """

    def load(self):
        """Load the value from config to GUI
        """
        self.control.setChecked(self.config.get(self.optionName))

    def save(self):
        """Save the value from GUI to config
        """
        _set(self.config, self.optionName, self.control.isChecked())


class TextOption(Option):
    """Text option

    Control may be QLineEdit
    """

    def load(self):
        """Load the value from config to GUI
        """
        self.control.setText(self.config.get(self.optionName))

    def save(self):
        """Save the value from GUI to config
        """
        _set(self.config, self.optionName, self.control.text())


class ListOnePerLineOption(Option):
    """List of strings. One item per line.

    Control may be QPlainTextEdit
    """

    def load(self):
        """Load the value from config to GUI
        """
        self.control.setPlainText('\n'.join(self.config.get(self.optionName)))

    def save(self):
        """Save the value from GUI to config
        """
        lines = self.control.toPlainText().split('\n')
        _set(self.config, self.optionName, lines)


class NumericOption(Option):
    """Numeric option.

    Control may be QSlider or other control, which has .value() and .setValue() methods
    """

    def load(self):
        """Load the value from config to GUI
        """
        self.control.setValue(self.config.get(self.optionName))

    def save(self):
        """Save the value from GUI to config
        """
        _set(self.config, self.optionName, self.control.value())


class ColorOption(Option):
    """Color option

    Control must be enki.widgets.ColorButton
    """

    def load(self):
        """Load the value from config to GUI
        """
        self.control.setColor(QColor(self.config.get(self.optionName)))

    def save(self):
        """Save the value from GUI to config
        """
        _set(self.config, self.optionName, self.control.color().name())


class FontOption(Option):
    """Font option.

    Option has 2 controls:

    * QLineEdit is an example of font
    * Button is used for open font dialogue.

    This option opens Font dialogue automatically, when button has been clicked
    """

    def __init__(self, dialog, config, familyOption, sizeOption, editControl, buttonControl):  # pylint: disable=R0913
        self.familyOptionName = familyOption
        self.sizeOptionName = sizeOption
        self.editControl = editControl
        self.buttonControl = buttonControl
        self.buttonControl.clicked.connect(self._onClicked)
        Option.__init__(self, dialog, config, None, None)

    def load(self):
        """Load the value from config to GUI
        """
        font = QFont(self.config.get(self.familyOptionName), self.config.get(self.sizeOptionName))
        self.editControl.setFont(font)
        self.editControl.setToolTip(font.toString())

    def save(self):
        """Save the value from GUI to config
        """
        font = self.editControl.font()
        _set(self.config, self.familyOptionName, font.family())
        _set(self.config, self.sizeOptionName, font.pointSize())

    # On Windows, Python 3.5, PyQt 5.7, uncommenting the line below produces::
    #
    #   QObject::connect: Cannot connect QPushButton::clicked(bool) to (null)::_onClicked()
    #   CRITICAL:root:Traceback (most recent call last):
    #     File "E:\enki_all\enki\bin\..\enki\plugins\qpartsettings\__init__.py", line 163, in _onSettingsDialogAboutToExecute
    #       fontWidget.lFont, fontWidget.pbFont),
    #     File "E:\enki_all\enki\bin\..\enki\core\uisettings.py", line 226, in __init__
    #       self.buttonControl.clicked.connect(self._onClicked)
    #   TypeError: connect() failed between clicked(bool) and _onClicked()
    #
    # This makes no sense to me.
    #@pyqtSlot()
    def _onClicked(self):
        """Button click handler. Open font dialog
        """
        font, accepted = QFontDialog.getFont(self.editControl.font(), self.dialog)
        if accepted:
            self.editControl.setFont(font)


class ChoiseOption(Option):
    """This option allows to choose value from few possible.

    It is presented as set of QRadioButton's

    *controlToValue* dictionary contains mapping *checked radio button name: option value*
    """

    def __init__(self, dialog, config, optionName, controlToValue):
        self.cotrolToValue = controlToValue
        Option.__init__(self, dialog, config, optionName, None)

    def load(self):
        """Load the value from config to GUI
        """
        value = self.config.get(self.optionName)
        for button, keyValue in self.cotrolToValue.items():
            if value == keyValue:
                button.setChecked(True)
                break
        else:
            print('Button not found for option %s value' % self.optionName, value, file=sys.stderr)

    def save(self):
        """Save the value from GUI to config
        """
        for button in self.cotrolToValue.keys():
            if button.isChecked():
                _set(self.config, self.optionName, self.cotrolToValue[button])


class UISettings(QDialog):
    """Settings dialog widget
    """

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self._createdObjects = []

        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/UISettings.ui'), self)
        self.swPages.setCurrentIndex(0)

        self.setAttribute(Qt.WA_DeleteOnClose)

        # Expand all tree widget items
        self._pageForItem = {"Ignored files": self.pIgnoredFiles,
                             "REPL": self.pRepl,
                             "Lint": self.pLint,
                             "Editor": self.pEditor}

        # resize to minimum size
        hint = self.sizeHint()
        self.resize(int(max(hint.width(), hint.height() * 1.61)), int(hint.height()))

    def _itemByPath(self, pathParts):
        """Find item by it's path. Path is list of parts. I.e. ['Editor', 'Ignored files']
        """
        item = self.twMenu.findItems(pathParts[0], Qt.MatchExactly)[0]
        for part in pathParts[1:]:
            for index in range(item.childCount()):
                if item.child(index).text[0] == part:
                    item = item.child(index)
                    break
            else:
                raise KeyError("Item %s not found" % part)
        return item

    def _itemPath(self, item):
        """Get path of item by reference to it
        """
        parts = [item.text(0)]
        while item.parent() is not None:
            item = item.parent()
            parts.insert(0, item.text(0))
        return '/'.join(parts)

    def appendPage(self, path, widget, icon=None):
        """Append page to the tree. Called by a plugin for creating own page. Example:
        ::

            widget = MitSchemeSettings(dialog)
            dialog.appendPage(u"Modes/MIT Scheme", widget, QIcon(':/enkiicons/languages/scheme.png'))

        """
        pathParts = path.split('/')
        if len(pathParts) == 1:
            parentItem = None
        else:
            parentItem = self._itemByPath(pathParts[:-1])

        twItem = QTreeWidgetItem([pathParts[-1]])
        if icon is not None:
            twItem.setIcon(0, icon)
        else:
            twItem.setIcon(0, QIcon(':/enkiicons/transparent.png'))

        if parentItem is not None:
            parentItem.addChild(twItem)
            self.twMenu.expandAll()
        else:
            self.twMenu.addTopLevelItem(twItem)

        self.swPages.addWidget(widget)
        self._pageForItem[path] = widget

    def appendOption(self, option):
        """Append *Option instance to the list of options
        """
        self._createdObjects.append(option)

    def on_twMenu_itemSelectionChanged(self):
        pass  # suppress docstring for non-public method
        """Qt slot. Switch current page, after item in the pages tree has been selected
        """
        selectedItem = self.twMenu.selectedItems()[0]

        itemPath = self._itemPath(selectedItem)
        page = self._pageForItem[itemPath]
        self.swPages.setCurrentWidget(page)


class UISettingsManager(QObject):  # pylint: disable=R0903
    """Add to the main menu *Settings->Settings* action and execute settings dialogue
    """

    aboutToExecute = pyqtSignal(UISettings)
    """
    aboutToExecute(:class:`enki.core.uisettings.UISettings`)

    **Signal** emitted, when dialog is about to be executed. Plugins shall add own settings to the dialogue
    """  # pylint: disable=W0105

    dialogAccepted = pyqtSignal()
    """
    accepted()

    **Signal** emitted, when dialog has been accepted. Plugins shall save and apply settings
    """  # pylint: disable=W0105

    def __init__(self):
        QObject.__init__(self)
        self._action = core.actionManager().addAction("mSettings/aSettings",
                                                      _tr("Settings.."),
                                                      QIcon(':/enkiicons/settings.png'))
        self._action.setStatusTip(_tr("Edit settigns.."))
        self._action.triggered.connect(self._onEditSettings)

    def terminate(self):
        core.actionManager().removeAction(self._action)

    @pyqtSlot()
    def _onEditSettings(self):
        """*Settings->Settings* menu item handler. Open the dialogue
        """
        dialog = UISettings(core.mainWindow())
        self.aboutToExecute.emit(dialog)
        dialog.accepted.connect(self.dialogAccepted)
        dialog.accepted.connect(self._saveSettings)
        dialog.open()

    @pyqtSlot()
    def _saveSettings(self):
        """Flush main configuration file.
        """
        try:
            core.config().flush()
        except UserWarning as ex:
            core.mainWindow().appendMessage(str(ex))
