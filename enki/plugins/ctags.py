from PyQt4.QtGui import QIcon, QDialog, QFileDialog
from enki.core.core import core
import os
import errno

class Plugin:
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
        haveDocument = core.workspace().currentDocument() is not None
        
        if haveDocument:
            openedDoc = core.workspace().currentDocument()
            tagsFile = os.path.dirname(openedDoc.filePath())
            tagsFile += os.path.sep + ".tags"
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
        projectPath = dialog.getPath()
        
        # Generate local tags in each folder
        dirs = self._getDirs(projectPath)
        for dir in dirs:
            from subprocess import call
        
            dir += os.path.sep
            command = "ctags -f .tags *"
            p = Popen(command, cwd = dir, shell=True, stdout=PIPE, stderr=STDOUT)
            returnCode = p.wait()

            if returnCode:
                print "error:", p.stdout.read()
        
        # Generate global tags file
        projectPath += os.path.sep
        command = "ctags -f .tags_global_scope --file-scope=no -R *"
        p = Popen(command, cwd = projectPath, shell=True, stdout=PIPE, stderr=STDOUT)
        returnCode = p.wait()

        if returnCode:
            print "error:", p.stdout.read()
        
        self._enableActionsState()
   
    def _updateTags(self):
        """Update only local tag file without updating global tag file
        """
        from subprocess import Popen, PIPE, STDOUT

        openedDoc = core.workspace().currentDocument()
        if openedDoc is None:
            raise UserWarning("Action is available, but must not")
        
        curDir = os.path.dirname(openedDoc.filePath())
        curDir += os.path.sep
        command = "ctags -f .tags *"
        
        p = Popen(command, cwd = curDir, shell=True, stdout=PIPE, stderr=STDOUT)
        returnCode = p.wait()
        if returnCode:
            print "error:", p.stdout.read()

    def _getDirs(self, absPath):
        """Recursive walk through directory.
        Return list of all directories
        """ 
        result = [absPath]
        
        for name in os.listdir(absPath):
            # skip .svn and similar directories (or hidden)
            if name.startswith('.'):
                continue
            
            fullPath = os.path.join(absPath, name)
            if os.path.isdir(fullPath):
                dirs = self._getDirs(fullPath)
                if dirs is not None:
                    result += dirs
        
        return result

class UICtags(QDialog):
    """Dialogue for choosing root folder of any project,
    for which tags files will generate
    """
    def __init__(self, parentWindow):
        import os.path
        
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
        
    def _browseDirectory(self):
        path = QFileDialog.getExistingDirectory( self, self.tr( "Project directory" ), self.lineEditPath.text() )

        if path:
            self.lineEditPath.setText( path )
