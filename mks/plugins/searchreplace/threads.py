"""
threads --- Search and Replace threads
======================================

This threads are used for asynchronous search and replace
"""

import os.path
import re
import time
import fnmatch

from PyQt4.QtCore import pyqtSignal, \
                         QThread

from mks.plugins.searchreplace import *
import searchresultsmodel

def _isBinary(fileObject):
    """Expects, that file position is 0, when exits, file position is 0
    """
    binary = '\0' in fileObject.read( 4096 )
    fileObject.seek(0)
    return binary


class StopableThread(QThread):
    """Stoppable thread class. Used as base for search and replace thread.
    """
    _exit = False
    
    def __init__(self):
        QThread.__init__(self)
    
    def __del__(self):
        self.stop()

    def stop(self):
        """Stop thread synchronously
        """
        self._exit = True
        self.wait()
    
    def start(self):
        """Ensure thread is stopped, and start it
        """
        self.stop()
        self._exit = False
        QThread.start(self)

class SearchThread(StopableThread):
    """Thread builds list of files for search and than searches in this files.append
    """
    RESULTS_EMIT_TIMEOUT = 1.0

    reset = pyqtSignal()
    resultsAvailable = pyqtSignal(list)  # list of searchresultsmodel.FileResults
    progressChanged = pyqtSignal(int, int)  # int value, int total

    def search(self, context ):
        """Start search process.
        context stores search text, directory and other parameters
        """
        self.stop()
        
        self.searchContext = context
        if context.mode & ModeFlagReplace:
            self._checkStateForResults = Qt.Checked
        else: 
            self._checkStateForResults = None
        
        self.start()

    def clear(self):
        """Stop thread and clear search results
        """
        self.stop()
        self.reset.emit()            

    def _getFiles(self, path, maskRegExp):
        """Get recursive list of files from directory.
        maskRegExp is regExp object for check if file matches mask
        """
        retFiles = []
        for root, dirs, files in os.walk(os.path.abspath(path)):  # pylint: disable=W0612
            if root.startswith('.') or (os.path.sep + '.') in root:
                continue
            for fileName in files:
                if fileName.startswith('.'):
                    continue
                if maskRegExp and not maskRegExp.match(fileName):
                    continue
                fullPath = os.path.join(root, fileName)
                if not os.path.isfile(fullPath):
                    continue
                retFiles.append(root + os.path.sep + fileName)

            if self._exit :
                break

        return retFiles
    
    def _getFilesToScan(self):
        """Get list of files for search.
        """
        files = set()

        # TODO search in project
        #elif mode in (ModeSearchProjectFiles, ModeReplaceProjectFiles):
        #    sources = self.searchContext.sourcesFiles
        #    mask = self.searchContext.mask
        #    for fileName in sources:
        #        if  QDir.match( mask, fileName ) :
        #            files.append(fileName)
        
        if self.searchContext.mask:
            regExPatterns = [fnmatch.translate(pat) for pat in self.searchContext.mask]
            maskRegExpPattern = '(' + ')|('.join(regExPatterns) + ')'
            maskRegExp = re.compile(maskRegExpPattern)
        else:
            maskRegExp = None

        if self.searchContext.mode in (ModeSearchDirectory, ModeReplaceDirectory):
            path = self.searchContext.searchPath
            return self._getFiles(path, maskRegExp)
        elif self.searchContext.mode in \
                                (ModeSearchOpenedFiles, ModeReplaceOpenedFiles):
            files = self.searchContext.openedFiles.keys()
            if maskRegExp:
                basenames = [os.path.basename(f) for f in files]
                files = [f for f in basenames if maskRegExp.match(f)]
            return files
        else:
            assert(0)

    def _fileContent(self, fileName, encoding='utf_8'):
        """Read text from file
        """
        if fileName in self.searchContext.openedFiles:
            return self.searchContext.openedFiles[ fileName ]

        try:
            with open(fileName) as openedFile:
                if _isBinary(openedFile):
                    return ''
                return unicode(openedFile.read(), encoding, errors = 'ignore')
        except IOError as ex:
            print ex
            return ''

    def run(self):
        """Start point of the code, running in thread.
        Build list of files for search, than do search
        """
        startTime = time.clock()
        self.reset.emit()
        self.progressChanged.emit( -1, 0 )

        files = sorted(self._getFilesToScan())

        if  self._exit :
            return
        
        self.progressChanged.emit( 0, len(files))
        
        # Prepare data for search process        
        lastResultsEmitTime = time.clock()
        notEmittedFileResults = []
        # Search for all files
        for fileIndex, fileName in enumerate(files):
            results = self._searchInFile(fileName)
            if  results:
                newFileRes = searchresultsmodel.FileResults(self.searchContext.searchPath,
                                                            fileName,
                                                            results,
                                                            self._checkStateForResults)
                notEmittedFileResults.append(newFileRes)

            if notEmittedFileResults and \
               (time.clock() - lastResultsEmitTime) > self.RESULTS_EMIT_TIMEOUT:
                self.progressChanged.emit( fileIndex, len(files))
                self.resultsAvailable.emit(notEmittedFileResults)
                notEmittedFileResults = []
                lastResultsEmitTime = time.clock()

            if  self._exit :
                self.progressChanged.emit( fileIndex, len(files))
                break
        
        if notEmittedFileResults:
            self.resultsAvailable.emit(notEmittedFileResults)

    def _searchInFile(self, fileName):
        """Search in the file and return searchresultsmodel.Result s
        """
        lastPos = 0
        eolCount = 0
        results = []
        eol = "\n"
        
        content = self._fileContent( fileName )
        
        # Process result for all occurrences
        for match in self.searchContext.regExp.finditer(content):
            start = match.start()
            
            eolStart = content.rfind( eol, 0, start)
            eolEnd = content.find( eol, start)
            eolCount += content[lastPos:start].count( eol )
            lastPos = start
            
            wholeLine = content[eolStart + 1:eolEnd]
            column = start - eolStart
            if eolStart != 0:
                column -= 1
            
            result = searchresultsmodel.Result( fileName = fileName, \
                             wholeLine = wholeLine, \
                             line = eolCount, \
                             column = column, \
                             match=match,
                             checkState = self._checkStateForResults)
            results.append(result)

            if self._exit:
                break
        return results

class ReplaceThread(StopableThread):
    """Thread does replacements in the directory according to checked items
    """
    resultsHandled = pyqtSignal(unicode, list)
    openedFileHandled = pyqtSignal(unicode, unicode)
    error = pyqtSignal(unicode)

    def replace(self, context, results):
        """Run replace process
        """
        self.stop()
        self.searchContext = context
        self._results = results
        self.start()

    def _saveContent(self, fileName, content, encoding):
        """Write text to the file
        """
        if encoding:
            try:
                content = content.encode(encoding)
            except UnicodeEncodeError as ex:
                pattern = self.tr("Failed to encode file to %s: %s")
                text = unicode(str(ex), 'utf_8')
                self.error.emit(pattern % (encoding, text))
                return
        try:
            with open(fileName, 'w') as openFile:
                openFile.write(content)
        except IOError as ex:
            pattern = self.tr("Error while saving replaced content: %s")
            text = unicode(str(ex), 'utf_8')
            self.error.emit(pattern % text)

    def _fileContent(self, fileName, encoding='utf_8'):
        """Read file
        """
        if fileName in self.searchContext.openedFiles:
            return self.searchContext.openedFiles[ fileName ]
        else:
            try:
                with open(fileName) as openFile:
                    content = openFile.read()
            except IOError as ex:
                self.error.emit( self.tr( "Error opening file: %s" % str(ex) ) )
                return ''
            
            if encoding:
                try:
                    return unicode(content, encoding)
                except UnicodeDecodeError as ex:
                    self.error.emit(self.tr( "File %s not read: unicode error '%s'. File may be corrupted" % \
                                    (fileName, str(ex) ) ))
                    return None
            else:
                return content

    def run(self):
        """Start point of the code, running i thread
        Does thread job
        """
        startTime = time.clock()
        
        for fileName in self._results.keys():
            handledResults = []
            content = self._fileContent( fileName, self.searchContext.encoding )
            if content is None:  # if failed to read file
                continue
            
            # count from end to begin because we are replacing by offset in content
            for result in self._results[ fileName ][::-1]:
                try:
                    replaceTextWithMatches = self.searchContext.regExp.sub(self.searchContext.replaceText,
                                                                           result.match.group(0))
                except re.error, ex:
                    message = unicode(ex.message, 'utf_8')
                    message += r'. Probably <i>\group_index</i> used in replacement string, but such group not found. '\
                               r'Try to escape it: <i>\\group_index</i>'
                    self.error.emit(message)
                    return
                content = content[:result.match.start()] + replaceTextWithMatches + content[result.match.end():]
                handledResults.append(result)
            
            if fileName in self.searchContext.openedFiles:
                # TODO encode content with self.searchContext.encoding 
                self.openedFileHandled.emit( fileName, content)
            else:
                self._saveContent( fileName, content, self.searchContext.encoding )
            
            self.resultsHandled.emit( fileName, handledResults)

            if  self._exit :
                break

        print "Replace finished in ", time.clock() - startTime
