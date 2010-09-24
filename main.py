#!/usr/bin/env python

import sys

from PyQt4 import QtGui, QtCore

import mks.config
import mks.monkeycore

def showHelp():
    showVersion()
    print "Command line arguments:"
    print "\t-h, --help      Show command line help"
    print "\t-v, --version   Show program version"
    print "\t-projects      Open the projects given as parameters (-projects project1 ...)"
    print "\t-files         Open the files given as parameters (-files file1 ...)"

def showVersion():
    print "%s version %s (%s)" % (mks.config.PACKAGE_NAME, mks.config.PACKAGE_VERSION, mks.config.PACKAGE_VERSION_STR)
    print "%s & The Monkey Studio Team" % mks.config.PACKAGE_COPYRIGHTS
    print "http://%s" % mks.config.PACKAGE_DOMAIN

def main():
    #QT_REQUIRE_VERSION( argc, argv, "4.5.0" );
    
    app = QtGui.QApplication ( sys.argv );
    
    app.setApplicationName( mks.config.PACKAGE_NAME );
    app.setOrganizationName( mks.config.PACKAGE_NAME );
    app.setOrganizationDomain( mks.config.PACKAGE_DOMAIN );
    
    QtCore.QObject.connect(app, QtCore.SIGNAL('lastWindowClosed()'),
                            app, QtCore.SLOT('quit()'))
    
    """
    // init pSettings
    //pSettings::setIniInformations();
    """
    
    """TODO
    // parse command line arguments
    //CommandLineManager clm;
    //clm.parse();
    """
    
    """TODO
    /*Properties p;
    p.writeToFile( "properties.xml" );*/
    """
    
    if '-v' in sys.argv or '--version' in sys.argv:
        showVersion()
        return 0
    
    if '-h' in sys.argv or '--help' in sys.argv:
        showHelp()
        return 0
    
    """TODO
    support projects and files opening
    """
    
    # init monkey studio core
    mks.monkeycore.init();
    """TODO
    // handle command line arguments
    clm.process();
    """
    
    # execute application
    result = app.exec_();
    
    """TODO
    // some cleanup
    MonkeyCore::pluginsManager()->clearPlugins();
    delete MonkeyCore::settings();
    // exit code
    """
    return result

if __name__ == '__main__':
    sys.exit(main())
