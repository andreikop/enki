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
  It loads its option from :class:`mks.core.config.Config` to GUI, and saves from GUI to config.
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
"""

import sys
import os.path
from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QColor, \
                        QDialog, \
                        QFont, \
                        QFontDialog, \
                        QIcon

from mks.core.core import core, DATA_FILES_PATH

def _tr(text):
    """Stub for translation
    """
    return text

class ModuleConfigurator:
    """Interface, which must be implemented by core module or plugin, which needs to configure themselves via GUI dialog.
    
    See :class:`mks.core.openedfilemodel.Configurator` source for simple example of class implementation
    """
    def __init__(self, dialog):
        """Create all options. Every option loads its value during creation
        """
        pass

    def saveSettings(self):
        """ Save own settings. If there are own config file, flush it. If module uses core config file - do nothing.
        """
        pass

    def applySettings(self):
        """ Apply module specific settings
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
        self.config.set(self.optionName, self.control.isChecked())

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
        self.config.set(self.optionName, self.control.text())

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
        self.config.set(self.optionName, lines)

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
        self.config.set(self.optionName, self.control.value())

class ColorOption(Option):
    """Color option
    
    Control must be PyQt4.Fresh.pColorButton
    """
    def load(self):
        """Load the value from config to GUI
        """
        self.control.setColor(QColor(self.config.get(self.optionName)))
    
    def save(self):
        """Save the value from GUI to config
        """
        self.config.set(self.optionName, self.control.color().name())

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
        self.config.set(self.familyOptionName, font.family())
        self.config.set(self.sizeOptionName, font.pointSize())
    
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
                self.config.set(self.optionName, self.cotrolToValue[button])


class UISettingsManager:  # pylint: disable=R0903
    """Add to the main menu *Settings->Settings* action and execute settings dialogue
    """
    def __init__(self):
        self._action = core.actionModel().addAction("mSettings/aSettings",
                                                    _tr( "Settings.."), 
                                                    QIcon(':/mksicons/settings.png'))
        self._action.setStatusTip(_tr( "Edit settigns.."))
        self._action.triggered.connect(self._onEditSettings)
    
    def __term__(self):
        core.actionModel().removeAction(self._action)

    def _onEditSettings(self):
        """*Settings->Settings* menu item handler. Open the dialogue
        """
        UISettings(core.mainWindow()).exec_()


class UISettings(QDialog):
    """Settings dialog widget
    """
    
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self._createdObjects = []
        self._allTwItems = []
        self._moduleConfigurators = []

        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/UISettings.ui'), self)
        self.swPages.setCurrentIndex(0)
        
        self.setAttribute( Qt.WA_DeleteOnClose )
        self.createOptions()
        self.accepted.connect(self.saveSettings)
        self.accepted.connect(self.applySettings)

    def _initTopLevelItems(self):
        """Generate list of all tree items. Used to switch pages
        """
        def allItems(twItem):
            """Item itself and all children (reqursive)
            """
            yield twItem
            for childIndex in range(twItem.childCount()):
                for item in allItems(twItem.child(childIndex)):
                    yield item

        topLevelItems = [self.twMenu.topLevelItem(index) for index in range(self.twMenu.topLevelItemCount())]
        
        for topLevelItem in topLevelItems:
            self._allTwItems.extend(allItems(topLevelItem))

    def createOptions(self):
        """Create and load all opitons. Create ::class:`mks.core.uisettings.ModuleConfigurator` instances
        """
        
        # Get core and plugin configurators
        moduleConfiguratorClasses = []
        moduleConfiguratorClasses.extend(core.moduleConfiguratorClasses)
        for plugin in core.loadedPlugins():
            if plugin.moduleConfiguratorClass() is not None:  # If plugin has configurator
                moduleConfiguratorClasses.append(plugin.moduleConfiguratorClass())
        
        # Create configurator instances
        for moduleConfiguratorClass in moduleConfiguratorClasses:
            self._moduleConfigurators.append(moduleConfiguratorClass(self))

        # Expand all tree widget items
        self._initTopLevelItems()
        
        # resize to minimum size
        self.resize( self.minimumSizeHint() )
    
    def applySettings(self):
        """Dialog has been accepted. Call ModuleConfigurators for apply settings
        """
        for configurator in self._moduleConfigurators:
            configurator.applySettings()

    def saveSettings(self):
        """Flush main configuration file. Call ModuleConfigurators for flush other config files
        """
        for configurator in self._moduleConfigurators:
            configurator.saveSettings()
        try:
            core.config().flush()
        except UserWarning as ex:
            core.messageManager().appendMessage(unicode(ex))

    def on_twMenu_itemSelectionChanged(self):
        """Qt slot. Switch current page, after item in the pages tree has been selected
        """
        # get item
        selectedItem = self.twMenu.selectedItems()[0]
        self.lInformations.setText( selectedItem.text( 0 ) )
        self.swPages.setCurrentIndex(self._allTwItems.index(selectedItem))




#TODO restore or remove old code

#def Dialog reject(self):
#    
#    settings = MonkeyCore.settings()        
#    for lexer in mLexers:
#        lexer.readSettings( *settings, scintillaSettingsPath().toLocal8Bit().constData() )
#    QDialog.reject(self)

#----------------------------------------------------------- constructor
#        
#        for b in self.findChildren(pColorButton):
#            b.setColorNameHidden( True )
#        #ifdef Q_WS_MAC
#            b.setIconSize( QSize( 32, 12 ) )
#        #else:
#            b.setIconSize( QSize( 32, 16 ) )
#        #endif
#        # loads text codecs
#        self.cbDefaultCodec.addItems( availableTextCodecs() )

#        # fill lexers combo
#        self.cbSourceAPIsLanguages.addItems( availableLanguages() )
#        self.cbLexersAssociationsLanguages.addItems( availableLanguages() )
#        self.cbLexerLanguages.addItems( availableLanguages() )

#        # resize column
#        self.twLexersAssociations.setColumnWidth( 0, 200 )

#        # resize column
#        self.twAbbreviations.setColumnWidth( 0, 100 )
#        self.twAbbreviations.setColumnWidth( 1, 180 )

#        # connections
#        # event filter
#        # lexer elements highlighting
#        self.pbLexersHighlightingForeground.clicked.connect(self.lexersHighlightingColour_clicked)
#        self.pbLexersHighlightingBackground.clicked.connect(self.lexersHighlightingColour_clicked)
#        self.pbLexersHighlightingFont.clicked.connect(self.lexersHighlightingFont_clicked)
#        self.pbLexersHighlightingAllForeground.clicked.connect(self.lexersHighlightingColour_clicked)
#        self.pbLexersHighlightingAllBackground.clicked.connect(self.lexersHighlightingColour_clicked)
#        self.pbLexersHighlightingAllFont.clicked.connect(self.lexersHighlightingFont_clicked)
#        for cb in self.gbLexersHighlightingElements.findChildren(QCheckBox):
#            if  self.cb != self.cbLexerFillEol :
#                self.cb.clicked.connect(self.cbLexerProperties_clicked)

#        for widget in  self.findChildren(QWidget):
#            widget.setAttribute( Qt.WA_MacSmallSize, True )
#            widget.setAttribute( Qt.WA_MacShowFocusRect, False )

#--------------------------------------------------------  loadSettings

#        # General
#        self.cbSaveSession.setChecked( saveSessionOnClose() )
#        self.cbRestoreSession.setChecked( restoreSessionOnStartup() )

#        #  General
#        
#        self.cbDefaultCodec.setCurrentIndex( self.cbDefaultCodec.findText( defaultCodec() ) )

#        # Source APIs
#        for ( i = 0; i < self.cbSourceAPIsLanguages.count(); i++ )
#            self.cbSourceAPIsLanguages.setItemData( i, 
#                        s.value( "SourceAPIs/" +cbSourceAPIsLanguages.itemText( i ) ).toStringList() )
#        if  self.cbSourceAPIsLanguages.count() > 0 :
#            self.cbSourceAPIsLanguages.setCurrentIndex( 0 )
#        #  Lexers Associations
#        QMap<QString, l = MonkeyCore.fileManager().associations()
#        for k in l.keys():
#            foreach ( QString e, l.value( k ) )
#                it = QTreeWidgetItem( self.twLexersAssociations )
#                it.setText( 0, e )
#                it.setText( 1, k )

#
#        #  Lexers Highlighting
#        for l in mLexers:
#            l.readSettings( *s, scintillaSettingsPath().toLocal8Bit().constData() )

#        if  self.cbLexerLanguages.count() :
#            on_cbLexerLanguages_currentIndexChanged( self.cbLexerLanguages.itemText( 0 ) )

#        #  Abbreviations
#        for a in MonkeyCore.abbreviationsManager().abbreviations():
#            it = QTreeWidgetItem( self.twAbbreviations )
#            it.setText( 0, a.Macro )
#            it.setText( 1, a.Description )
#            it.setText( 2, a.Language )
#            it.setData( 0, Qt.UserRole, a.Snippet )

#        
#        # environment variables editor
#        eveVariables.setVariables( MonkeyCore.consoleManager().environmentVariablesManager().variables(), True )
#        

#------------------------------------------------------------
#        
#        
#        setSaveSessionOnClose( self.cbSaveSession.isChecked() )
#        setRestoreSessionOnStartup( self.cbRestoreSession.isChecked() )
#        # Editor
#        #  General
#        setAutoSyntaxCheck( self.cbAutoSyntaxCheck.isChecked() )
#        setDefaultCodec( self.cbDefaultCodec.currentText() )
#        
#        
#        # Source APIs
#        
#        sp = "SourceAPIs/"
#        for ( i = 0; i < self.cbSourceAPIsLanguages.count(); i++ )
#            s.setValue( sp +cbSourceAPIsLanguages.itemText( i ), 
#                        self.cbSourceAPIsLanguages.itemData( i ).toStringList() )

#        #  Lexers Associations
#        QMap<QString, suffixes

#        for ( i = 0; i < self.twLexersAssociations.topLevelItemCount(); i++ )
#            it = self.twLexersAssociations.topLevelItem( i )

#            suffixes[ it.text( 1 ) ] << it.text( 0 )

#
#        for type in suffixes.keys():
#            MonkeyCore.fileManager().setCommand( type, suffixes[ type )

#
#        MonkeyCore.fileManager().generateScript()

#        #  Lexers Highlighting
#        for l in mLexers:
#            l.setDefaultPaper( self.tbDefaultDocumentPaper.color() )
#            l.setDefaultColor( self.tbDefaultDocumentPen.color() )
#            l.writeSettings( *s, scintillaSettingsPath().toLocal8Bit().constData() )

#
#        #  Abbreviations
#        pAbbreviationList abbreviations
#        for ( i = 0; i < self.twAbbreviations.topLevelItemCount(); i++ )
#            it = self.twAbbreviations.topLevelItem( i )

#            pAbbreviation abbreviation
#            abbreviation.Macro = it.text( 0 )
#            abbreviation.Description = it.text( 1 )
#            abbreviation.Language = it.text( 2 )
#            abbreviation.Snippet = it.data( 0, Qt.UserRole ).toString()

#            abbreviations << abbreviation

#
#        MonkeyCore.abbreviationsManager().set( abbreviations )
#        MonkeyCore.abbreviationsManager().generateScript()
#        
#        # environment variables editor
#        MonkeyCore.consoleManager().environmentVariablesManager().setVariables( eveVariables.variables() )
#        MonkeyCore.consoleManager().environmentVariablesManager().save()

#        # flush settings to disk
#        s.sync()
#        
#    def on_cbSourceAPIsLanguages_beforeChanged(self, i ):
#        if  i == self.cbSourceAPIsLanguages.currentIndex() :
#            l = [lwSourceAPIs.item( j ).text() for j in range(lwSourceAPIs.count())]
#            self.cbSourceAPIsLanguages.setItemData( i, l )

#    def on_cbSourceAPIsLanguages_currentIndexChanged(self, i ):
#        lwSourceAPIs.clear()
#        lwSourceAPIs.addItems( self.cbSourceAPIsLanguages.itemData( i ).toStringList() )

#    def on_pbSourceAPIsDelete_clicked(self):
#        # get selected item
#        it = lwSourceAPIs.selectedItems()[0]
#        if  it :
#            del it
#            self.cbSourceAPIsLanguages_beforeChanged( self.cbSourceAPIsLanguages.currentIndex() )

#    def on_pbSourceAPIsAdd_clicked(self):
#        # get files
#        files = leSourceAPIs.text().split("")
#        # add them recursively
#        for fn in files:
#            if  lwSourceAPIs.findItems( fn, Qt.MatchFixedString ).count() == 0 :
#                lwSourceAPIs.addItem( fn )
#        # clear input
#        leSourceAPIs.clear()
#        # save datas
#        self.cbSourceAPIsLanguages_beforeChanged( self.cbSourceAPIsLanguages.currentIndex() )

#    def on_pbSourceAPIsBrowse_clicked(self):
#        files = QFileDialog.getOpenFileNames( self.window(), self.tr( "Select API files" ), 
#        QString.null, self.tr( "API Files (*.api);;All Files (*)" ) )
#        if files:
#            leSourceAPIs.setText( ';'.join(files))

#    def on_twLexersAssociations_itemSelectionChanged(self):
#        it = self.twLexersAssociations.selectedItems()[0]
#        if  it :
#            leLexersAssociationsFilenamePattern.setText( it.text( 0 ) )
#            self.cbLexersAssociationsLanguages.setCurrentIndex( 
#                        self.cbLexersAssociationsLanguages.findText( it.text( 1 ) ) )

#    def on_pbLexersAssociationsAddChange_clicked(self):
#        f = leLexersAssociationsFilenamePattern.text()
#        l = self.cbLexersAssociationsLanguages.currentText()
#        if  f.isEmpty() or l.isEmpty() :
#            return
#        it = self.twLexersAssociations.selectedItems()[0]
#        if  not it or it.text[0] != f :
#            # check if item with same parameters already exists
#            l = self.twLexersAssociations.findItems( f, Qt.MatchFixedString )
#            if  l.count() :
#                it = l.at( 0 )
#            else:
#                it = QTreeWidgetItem( self.twLexersAssociations )

#        it.setText( 0, f )
#        it.setText( 1, l )
#        self.twLexersAssociations.setCurrentItem( 0 )
#        self.twLexersAssociations.selectionModel().clear()
#        leLexersAssociationsFilenamePattern.clear()
#        self.cbLexersAssociationsLanguages.setCurrentIndex( -1 )

#    def on_pbLexersAssociationsDelete_clicked(self):
#        it = self.twLexersAssociations.selectedItems()[0]
#        if  it :
#            del it
#            self.twLexersAssociations.setCurrentItem( 0 )
#            self.twLexersAssociations.selectionModel().clear()
#            leLexersAssociationsFilenamePattern.clear()
#            self.cbLexersAssociationsLanguages.setCurrentIndex( -1 )

#    def on_cbLexerLanguages_currentIndexChanged(self, s ):
#        l = mLexers[s]
#        lwLexersHighlightingElements.clear()
#        for i in range(128):
#            n = l.description( i )
#            if n:
#                it = QListWidgetItem( lwLexersHighlightingElements )
#                it.setText( n )
#                it.setForeground( l.color( i ) )
#                it.setBackground( l.paper( i ) )
#                it.setFont( l.font( i ) )
#                it.setData( Qt.UserRole, i )
#    

#    def on_lwLexersHighlightingElements_itemSelectionChanged(self):
#        it = lwLexersHighlightingElements.selectedItems()[0]
#        if  it :
#            self.cbLexerFillEol.setChecked( mLexers.value[self.cbLexerLanguages.currentText()].eolFill( 
#                        it.data( Qt.UserRole ).toInt() ) )

#    def lexersHighlightingColour_clicked(self):
#        # get self.sender
#        o = self.sender()
#        # color
#        # element colour
#        if  o == self.pbLexersHighlightingForeground or o == self.pbLexersHighlightingBackground :
#            # get item
#            it = lwLexersHighlightingElements.selectedItems()[0]
#            # cancel if no item
#            if  not it :
#                return
#            # get color
#            if o == self.pbLexersHighlightingForeground:
#                p = it.foreground().color()
#            else:
#                p = it.background().color
#            c = QColorDialog.getColor(p, self.window() )
#            # apply color
#            if  c.isValid() :
#                if  o == self.pbLexersHighlightingForeground :
#                    it.setForeground( c )
#                    mLexers.value( self.cbLexerLanguages.currentText() ).setColor( c, it.data( Qt.UserRole ).toInt() )
#                elif  o == self.pbLexersHighlightingBackground :
#                    it.setBackground( c )
#                    mLexers.value( self.cbLexerLanguages.currentText() ).setPaper( c, it.data( Qt.UserRole ).toInt() )
#        # gobal color
#        elif  o == self.pbLexersHighlightingAllForeground or o == self.pbLexersHighlightingAllBackground :
#            # get lexer
#            l = mLexers.value( self.cbLexerLanguages.currentText() )
#            # get color
#            c = QColorDialog.getColor( o == self.pbLexersHighlightingAllForeground ? l.color( -1 ) : 
#                        l.paper( -1 ), self.window() )
#            # apply
#            if  c.isValid() :
#                if  o == self.pbLexersHighlightingAllForeground :
#                    l.setColor( c, -1 )
#                elif  o == self.pbLexersHighlightingAllBackground :
#                    l.setPaper( c, -1 )
#                # refresh
#                on_cbLexerLanguages_currentIndexChanged( l.language() )

#    def lexersHighlightingFont_clicked(self):
#        # get self.sender
#        o = self.sender()
#        # values
#        # element font
#        if  o == self.pbLexersHighlightingFont :
#            # get item
#            it = lwLexersHighlightingElements.selectedItems()[0]
#            # cancel if no item
#            if  not it :
#                return
#            # get font
#            f, b = QFontDialog.getFont( &b, it.font(), self.window() )
#            # apply
#            if  b :
#                it.setFont( f )
#                mLexers.value( self.cbLexerLanguages.currentText() ).setFont( f, it.data( Qt.UserRole ).toInt() )
#        # global font
#        elif  o == self.pbLexersHighlightingAllFont :
#            # get lexer
#            l = mLexers[self.cbLexerLanguages.currentText()]
#            # get font
#            f, b = QFontDialog.getFont(l.font( -1 ), self.window() )
#            # apply
#            if  b :
#                l.setFont( f, -1 )
#                on_cbLexerLanguages_currentIndexChanged( l.language() )

#    def on_cbLexerFillEol_clicked(self, b ):
#        it = lwLexersHighlightingElements.selectedItems()[0]
#        if  it :
#            mLexers[self.cbLexerLanguages.currentText()].setEolFill( b, it.data( Qt.UserRole ).toInt() )

#    def on_pbLexersHighlightingReset_clicked(self):
#        # get lexer
#        l = mLexers[self.cbLexerLanguages.currentText()]
#        # reset and refresh
#        if  l :
#            resetLexer( l )
#            on_cbLexerLanguages_currentIndexChanged( l.language() )

#    def on_pbLexersApplyDefaultFont_clicked(self):
#        settings = MonkeyCore.settings()
#        font = self.lDefaultDocumentFont.font()
#        language = self.cbLexerLanguages.currentText()
#        
#        settings.setDefaultLexerProperties( font, False )
#        on_cbLexerLanguages_currentIndexChanged( language )

#    def on_twAbbreviations_itemSelectionChanged(self):
#        # get item
#        it = self.twAbbreviations.selectedItems()[0]
#        if  it :
#            teAbbreviationsCode.setPlainText( it.data( 0, Qt.UserRole ).toString() )
#        # enable/disable according to selection
#        teAbbreviationsCode.setEnabled( it )

#    def on_pbAbbreviationsAdd_clicked(self):
#        UIAddAbbreviation.edit( self.twAbbreviations );

#    def on_pbAbbreviationsRemove_clicked(self):
#        del self.twAbbreviations.selectedItems()[0]
#        teAbbreviationsCode.clear()

#    def on_teAbbreviationsCode_textChanged(self):
#        # get item
#        it = self.twAbbreviations.selectedItems()[0]
#        if  it :
#            it.setData( 0, Qt.UserRole, teAbbreviationsCode.toPlainText() )
