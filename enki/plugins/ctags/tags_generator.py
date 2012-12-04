"""
tags_generator --- Generate and update tags (based on utility ctags).
======================================================
"""

from PyQt4.QtGui import QIcon, QDialog, QFileDialog
from enki.core.core import core
import os
import errno

class TagsGenerator:
    """This is plugin used for generate tags files by ctags
    """
    def __init__(self):
        from subprocess import check_call, PIPE, STDOUT, CalledProcessError
        
        try:
            # supress any output to shell, only check for available ctags
            check_call("ctags --version", shell=True, stdout=PIPE, stderr=STDOUT)
        except CalledProcessError, e:
            print "ctags doesn't installed. Code navigation will be disabled"
            return
        
        # Actions added to main menu only if ctags presents in system
        self._addAction()
        
        # Adds tracking states of opened files
        core.workspace().modifiedChanged.connect(self._checkForTagsUpdate)

    def del_(self):
        """This method is called by core for each plugin during termination
        """
    
    def _addAction(self):
        """Add actions to menu
        """
        core.actionManager().addMenu("mNavigation/mCtags", "Ctags")

        actionGenerate = core.actionManager().addAction("mNavigation/mCtags/aGenerate",
                                                        "Generate tags",
                                                        QIcon(':enkiicons/enki.png'))
        actionGenerate.triggered.connect(self._generateTags)
        
        actionUpdate = core.actionManager().addAction("mNavigation/mCtags/aUpdate",
                                                      "Update tags",
                                                      QIcon(':enkiicons/enki.png'))
        core.actionManager().setDefaultShortcut(actionUpdate, "Ctrl+F5")
        actionUpdate.triggered.connect(self._updateTags)
        
        core.workspace().currentDocumentChanged.connect(self._enableActionsState)
    
    def _enableActionsState(self):
        """Enable actions if any document opens and tags file presents
        """
        openedDoc = core.workspace().currentDocument()
        haveDocument = openedDoc is not None
        
        if haveDocument:
            if openedDoc.filePath() is None: #  If new file has created its path is None
                haveDocument = False
            else:
                tagsFileDir = os.path.dirname(openedDoc.filePath())
                tagsFile = os.path.join(tagsFileDir, ".tags")
                haveDocument = os.path.exists(tagsFile)
            
        core.actionManager().action("mNavigation/mCtags/aUpdate").setEnabled(haveDocument)
    
    def _generateTags(self):
        """Display dialog for choose root directory of project and
        generate tags by approach, described in http://ctags.sourceforge.net/faq.html#15
        A local tag file in each directory containing only the tags for source files in that directory, in addition to one single global tag file present in the root directory of your hierarchy, containing all non-static tags present in all source files in the hierarchy.
        """
        from subprocess import Popen, PIPE, STDOUT
        
        # Retrive root folder of project
        dialog = UICtags(core.mainWindow())
        if dialog.exec_() == QDialog.Rejected:
            return
        projectPath = dialog.getPath() + os.path.sep
        
        # Generate local tags in each folder
        command = "ctags -f .tags *"
        p = Popen(command, cwd = projectPath, shell=True, stdout=PIPE, stderr=STDOUT)
        if p.wait():
            print "error:", p.stdout.read()
        
        if dialog.isRecursive():
            for root, folders, files in os.walk(projectPath):
                for dir in folders:
                    if dir.startswith('.'):
                        continue
                    absPath = os.path.join(root, dir, "")
                    p = Popen(command, cwd = absPath, shell=True, stdout=PIPE, stderr=STDOUT)
                    if p.wait():
                        print "error:", p.stdout.read()
        
        # Generate global tags file
        if dialog.isRecursive():
            command = "ctags -f .tags_global_scope --file-scope=no -R *"
        else:
            command = "ctags -f .tags_global_scope --file-scope=no *"
        p = Popen(command, cwd = projectPath, shell=True, stdout=PIPE, stderr=STDOUT)
        if p.wait():
            print "error:", p.stdout.read()
        
        self._enableActionsState()
   
    def _updateTags(self):
        """Update only local tag file without updating global tag file
        """
        from subprocess import Popen, PIPE, STDOUT

        openedDoc = core.workspace().currentDocument()
        if openedDoc is None:
            raise UserWarning("Action is available, but must not")
        
        command = "ctags -f .tags *"
        curDir = os.path.dirname(openedDoc.filePath()) + os.path.sep
        p = Popen(command, cwd = curDir, shell=True, stdout=PIPE, stderr=STDOUT)
        if p.wait():
            print "error:", p.stdout.read()

    def _checkForTagsUpdate(self, document, modified):
        """If folder with opened document contain .tags file - run updating tags.
        """
        if document is None:
            print "_checkForTagsUpdate NULL document", modified
            return
        if modified:    # update tags only upon save files
            return
        tagsFileDir = os.path.dirname(document.filePath())
        tagsFile = os.path.join(tagsFileDir, ".tags")
        if not os.path.exists(tagsFile):
            return
        try:
            os.remove(tagsFile)
        except OSError, e:
            print "_checkForTagsUpdate Can't delete", tagsFile
            return
        self._updateTags()

class UICtags(QDialog):
    """Dialogue for choosing root folder of any project,
    for which tags files will generate
    """
    def __init__(self, parentWindow):
        QDialog.__init__(self, parentWindow)
        from PyQt4 import uic  # lazy import for better startup performance
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'uictags.ui'), self)
        self.setWindowTitle(self.tr("Generate tags"))

        openedDoc = core.workspace().currentDocument()
        projectPath = os.path.expanduser('~')
        if openedDoc is not None:
            projectPath = os.path.dirname(openedDoc.filePath())
        self.lineEditPath.setText(projectPath)
        
        self.buttonBrowse.pressed.connect(self._browseDirectory)
        
    def getPath(self):
        return self.lineEditPath.text()
    
    def isRecursive(self):
        return self.checkBoxRecursive.isChecked()
        
    def _browseDirectory(self):
        path = QFileDialog.getExistingDirectory( self, self.tr( "Project directory" ), self.lineEditPath.text() )

        if path:
            self.lineEditPath.setText( path )
