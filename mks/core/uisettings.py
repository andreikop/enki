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
  
  config may be either :class:`mks.core.config.Config` or python dictionary
* :class:`mks.core.uisettings.ModuleConfigurator` interface. Must be implemented by plugin or core module.
  Creates and holds *Option objects, applies module settings, when necessary. Flushes config.

.. raw:: html

    <img src="https://docs.google.com/drawings/pub?id=1jDIHjn2dNIfeJlbQniFbwA4mdPZGRX_Sxj3pL7GgYeM&amp;w=869&amp;h=594">

`Edit the diagramm <https://docs.google.com/drawings/d/1jDIHjn2dNIfeJlbQniFbwA4mdPZGRX_Sxj3pL7GgYeM/edit?hl=en_US>`_


GUI dialog invocation workflow
------------------------------

#. MkS starts. Every plugin registers its ModuleConfigurator
#. An user clicks *Settings->Settings*
#. UISettings.ui are created
#. :class:`mks.core.uisettings.UISettingsManager` calls every ModuleConfigurator to load options
#. ModuleConfigurator creates options. Every option loads its value from the :class:`mks.core.config.Config`
#. The user edits settigns
#. The user clicks *OK*
#. :class:`mks.core.uisettings.UISettingsManager` calls every ModuleConfigurator to save settings
#. ModuleConfigurator calls every option to save settings
#. :class:`mks.core.uisettings.UISettingsManager` calls every ModuleConfigurator to apply settings
#. ModuleConfigurator applies module specific settings

Adding new settings
-------------------

If you need to add own settings to UISettings dialog, you should:

#. Implement and register your ModuleConfigurator
#. Add controls to the dialog.
   You may edit UISettings.ui or add your controls dynamically during dialog creation
   (in *ModuleConfigurator.__init__()*)
#. Create *Option class instance for every configurable option.

Classes
-------
Main classes:
    * :class:`mks.core.uisettings.UISettings` - settings dialogue
    * :class:`mks.core.uisettings.ModuleConfigurator` - plugin configurator

Classes for options:
    * :class:`mks.core.uisettings.CheckableOption` - bool option, CheckBox
    * :class:`mks.core.uisettings.TextOption` - string option, line edit
    * :class:`mks.core.uisettings.ListOnePerLineOption` - list of strings option, text edit
    * :class:`mks.core.uisettings.NumericOption` - numeric option, any numeric control
    * :class:`mks.core.uisettings.ColorOption` - color option, button
    * :class:`mks.core.uisettings.FontOption` - font option, button
    * :class:`mks.core.uisettings.ChoiseOption` - string from the set option, combo box

"""

import sys
import os.path
from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal, Qt, QObject
from PyQt4.QtGui import QColor, \
                        QDialog, \
                        QFont, \
                        QFontDialog, \
                        QIcon, \
                        QTreeWidgetItem

from mks.core.core import core, DATA_FILES_PATH

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

class ModuleConfigurator:
    """Interface, which must be implemented by core module or plugin, which needs to configure themselves via GUI dialog.
    
    See :class:`mks.core.openedfilemodel.Configurator` source for simple example of class implementation
    """
    def __init__(self, dialog):
        """Create all options. Every option loads its value during creation
        """
        pass


class Option:
    """Base class for all Options. Every class knows control on UISettings form, configuration option name,
    and can load/save the option
    
    Do not create dirrectly, use *Option classes
    """
    def __init__(self, dialog, config, optionName, control):
        self.config = config
        self.optionName = optionName
        self.control = control
        dialog.accepted.connect(self.save)
        self.load()
    
    def load(self):
        """Load the value from config to GUI. To be implemented by child classes
        """
        pass

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
    
    Control must be mks.widgets.ColorButton
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
        self.editControl.setFont( font )
        self.editControl.setToolTip( font.toString() )
    
    def save(self):
        """Save the value from GUI to config
        """
        font = self.editControl.font()
        _set(self.config, self.familyOptionName, font.family())
        _set(self.config, self.sizeOptionName, font.pointSize())
    
    def _onClicked(self):
        """Button click handler. Open font dialog
        """
        font, accepted = QFontDialog.getFont(self.editControl.font(), core.mainWindow() )
        if accepted:
            self.editControl.setFont( font )


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
        for button, keyValue in self.cotrolToValue.iteritems():
            if value == keyValue:
                button.setChecked(True)
                break
        else:
            print >> sys.stderr, 'Button not found for option %s value' % self.optionName, value
    
    def save(self):
        """Save the value from GUI to config
        """
        for button in self.cotrolToValue.iterkeys():
            if button.isChecked():
                _set(self.config, self.optionName, self.cotrolToValue[button])


class UISettings(QDialog):
    """Settings dialog widget
    """
    
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self._createdObjects = []
        self._pageForItem = {}
        self._moduleConfigurators = []

        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/UISettings.ui'), self)
        self.swPages.setCurrentIndex(0)
        
        self.setAttribute( Qt.WA_DeleteOnClose )
        self.createOptions()

    def createOptions(self):
        """Create and load all opitons. Create ::class:`mks.core.uisettings.ModuleConfigurator` instances
        """
        
        # Get core and plugin configurators
        moduleConfiguratorClasses = []
        moduleConfiguratorClasses.extend(core.moduleConfiguratorClasses)
        for plugin in core.loadedPlugins():
            if hasattr(plugin, 'moduleConfiguratorClass'):  # If plugin has configurator
                moduleConfiguratorClasses.append(plugin.moduleConfiguratorClass())
        
        # Create configurator instances
        for moduleConfiguratorClass in moduleConfiguratorClasses:
            self._moduleConfigurators.append(moduleConfiguratorClass(self))

        # Expand all tree widget items
        self._pageForItem.update (  {u"General": self.pGeneral,
                                     u"File associations": self.pAssociations,
                                     u"Editor": self.pEditorGeneral,
                                     u"Editor/Auto completion": self.pAutoCompletion,
                                     u"Editor/Colours": self.pColours,
                                     u"Editor/Indentation": self.pIndentation,
                                     u"Editor/Brace matching": self.pBraceMatching,
                                     u"Editor/Edge": self.pEdgeMode,
                                     u"Editor/Caret": self.pCaret,
                                     u"Editor/EOL": self.pEditorVisibility,
                                     u"Modes": self.pModes})
        
        # resize to minimum size
        self.resize( self.minimumSizeHint() )
    
    def _itemByPath(self, pathParts):
        """Find item by it's path. Path is list of parts. I.e. ['Editor', 'General']
        """
        item = self.twMenu.findItems(pathParts[0], Qt.MatchExactly)[0]
        for part in pathParts[1:]:
            for index in range (item.childCount()):
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
        """Append page to the tree. Called by a plugin module configurator to create own page. Example:
        ::
        
            class Configurator(ModuleConfigurator):
                def __init__(self, dialog):
                    ModuleConfigurator.__init__(self, dialog)
                    
                    widget = MitSchemeSettings(dialog)
                    dialog.appendPage(u"Modes/MIT Scheme", widget, QIcon(':/mksicons/languages/scheme.png'))
        
        """
        pathParts = path.split('/')
        if len(pathParts) == 1:
            parentItem = None
        else:
            parentItem = self._itemByPath(pathParts[:-1])
        
        twItem = QTreeWidgetItem([pathParts[-1]])
        if icon is not None:
            twItem.setIcon(0, icon)
        
        if parentItem is not None:
            parentItem.addChild(twItem)
        else:
            self.twMenu.addTopLevelItem(twItem)
        
        self.swPages.addWidget(widget)
        self._pageForItem[path] = widget

    def appendOption(self, option):
        """Append *Option instance to list of options
        """
        self._createdObjects.append(option)

    def on_twMenu_itemSelectionChanged(self):
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
    aboutToExecute(:class:`mks.core.uisettings.UISettings`)
    
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
                                                    _tr( "Settings.."), 
                                                    QIcon(':/mksicons/settings.png'))
        self._action.setStatusTip(_tr( "Edit settigns.."))
        self._action.triggered.connect(self._onEditSettings)
    
    def __del__(self):
        core.actionManager().removeAction(self._action)

    def _onEditSettings(self):
        """*Settings->Settings* menu item handler. Open the dialogue
        """
        dialog = UISettings(core.mainWindow())
        self.aboutToExecute.emit(dialog)
        dialog.accepted.connect(self.dialogAccepted)
        dialog.accepted.connect(self._saveSettings)
        dialog.exec_()

    def _saveSettings(self):
        """Flush main configuration file. Call ModuleConfigurators for flush other config files
        """
        try:
            core.config().flush()
        except UserWarning as ex:
            core.mainWindow().appendMessage(unicode(ex))
