# This script configures Fresh for PyQt v4.
#
# Copyright (c) 2010 Andrei Kopats <hlamer@tut.by>
# 
# This file is part of Fresh framework.
# File based on configure.py file of QScintilla Qt bindings
# 
# This file may be used under the terms of the GNU General Public
# License versions 2.0 or 3.0 as published by the Free Software
# Foundation and appearing in the files LICENSE.GPL2 and LICENSE.GPL3
# included in the packaging of this file.  Alternatively you may (at
# your option) use any later version of the GNU General Public
# License if such license has been publicly approved by Riverbank
# Computing Limited (or its successors, if any) and the KDE Free Qt
# Foundation. In addition, as a special exception, Riverbank gives you
# certain additional rights. These rights are described in the Riverbank
# GPL Exception version 1.1, which can be found in the file
# GPL_EXCEPTION.txt in this package.
# 
# Please review the following information to ensure GNU General
# Public Licensing requirements will be met:
# http://trolltech.com/products/qt/licenses/licensing/opensource/. If
# you are unsure which license is appropriate for your use, please
# review the following information:
# http://trolltech.com/products/qt/licenses/licensing/licensingoverview
# or contact the sales department at sales@riverbankcomputing.com.
# 
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

import sys
import os
import glob
import optparse


# Import SIP's configuration module so that we have access to the error
# reporting.  Then try and import the configuration modules for both PyQt3 and
# PyQt4.
try:
    import sipconfig
except ImportError:
    sys.stderr.write("Unable to import sipconfig.  Please make sure SIP is installed.\n")
    sys.exit(1)

try:
    import PyQt4.pyqtconfig as pyqt4
    pyqt = pyqt4.Configuration()
    qt_data_dir = pyqt.qt_data_dir
except:
    sipconfig.error("Unable to find either PyQt v3 or v4.")

print pyqt.pyqt_mod_dir
print pyqt

# Initialise the globals.
sip_min_version = 0x040a00

fresh_define = ""

def create_optparser():
    """Create the parser for the command line.
    """

    def store_abspath(option, opt_str, value, parser):
        setattr(parser.values, option.dest, os.path.abspath(value))

    def store_abspath_dir(option, opt_str, value, parser):
        if not os.path.isdir(value):
            raise optparse.OptionValueError("'%s' is not a directory" % value)
        setattr(parser.values, option.dest, os.path.abspath(value))

    p = optparse.OptionParser(usage="python %prog [options]",
            version="2.4.2")

    p.add_option("-a", "--apidir", action="callback", default=None,
            type="string", metavar="DIR", dest="freshdir",
            callback=store_abspath, help="where Fresh's API file will be "
            "installed [default: QTDIR/fresh]")
    p.add_option("-c", "--concatenate", action="store_true", default=False,
            dest="concat", help="concatenate the C++ source files")
    p.add_option("-d", "--destdir", action="callback",
            default=pyqt.pyqt_mod_dir, type="string", metavar="DIR",
            dest="freshmoddir", callback=store_abspath, help="where the "
            "Fresh module will be installed [default: %s]" %
            pyqt.pyqt_mod_dir)
    p.add_option("-j", "--concatenate-split", type="int", default=1,
            metavar="N", dest="split", help="split the concatenated C++ "
            "source files into N pieces [default: 1]")
    p.add_option("-k", "--static", action="store_true", default=False,
            dest="static", help="build the Fresh module as a static "
            "library")
    p.add_option("-n", action="callback", default=None, type="string",
            metavar="DIR", dest="freshincdir", callback=store_abspath_dir,
            help="the directory containing the Fresh header file "
            "directory [default: %s]" % pyqt.qt_inc_dir)
    p.add_option("--no-docstrings", action="store_true", default=False,
            dest="no_docstrings", help="disable the generation of docstrings")
    p.add_option("-o", action="callback", default=None, type="string",
            metavar="DIR", dest="freshlibdir", callback=store_abspath_dir,
            help="the directory containing the Fresh library [default: "
            "%s]" % pyqt.qt_lib_dir)
    p.add_option("-r", "--trace", action="store_true", default=False,
            dest="tracing", help="build the Fresh module with tracing "
            "enabled")
    p.add_option("-s", action="store_true", default=False, dest="not_dll",
            help="Fresh is a static library and not a DLL (Windows only)")
    p.add_option("-u", "--debug", action="store_true", default=False,
            help="build the Fresh module with debugging symbols")
    p.add_option("-v", "--sipdir", action="callback", default=None,
            metavar="DIR", dest="freshsipdir", callback=store_abspath,
            type="string", help="where the Fresh .sip files will be "
            "installed [default: %s]" % pyqt.pyqt_sip_dir)
    
    return p


def inform_user():
    """Tell the user the option values that are going to be used.
    """
    sipconfig.inform("PyQt %s is being used." % pyqt.pyqt_version_str)
    sipconfig.inform("Qt v%s %s edition is being used." % (sipconfig.version_to_string(pyqt.qt_version), pyqt.qt_edition))
    sipconfig.inform("SIP %s is being used." % pyqt.sip_version_str)

    sipconfig.inform("The Fresh module will be installed in %s." % opts.freshmoddir)
    sipconfig.inform("The Fresh API file will be installed in %s." % os.path.join(opts.freshdir, "api", "python"))
    sipconfig.inform("The Fresh .sip files will be installed in %s." % opts.freshsipdir)

    if opts.no_docstrings:
        sipconfig.inform("The Fresh module is being built without generated docstrings.")
    else:
        sipconfig.inform("The Fresh module is being built with generated docstrings.")


'''
def check_qscintilla():
    """See if Fresh can be found and what its version is.
    """
    # Find the Fresh header files.
    sciglobal = os.path.join(opts.freshincdir, "Qsci", "qsciglobal.h")

    if os.access(sciglobal, os.F_OK):
        # Get the Fresh version string.
        _, sciversstr = sipconfig.read_version(sciglobal, "Fresh", "QSCINTILLA_VERSION", "QSCINTILLA_VERSION_STR")

        if glob.glob(os.path.join(opts.freshlibdir, "*qscintilla2*")):
            # Because we include the Python bindings with the C++ code we can
            # reasonably force the same version to be used and not bother about
            # versioning.
            if sciversstr != "2.4.2":
                sipconfig.error("Fresh %s is being used but the Python bindings 2.4.2 are being built.  Please use matching versions." % sciversstr)

            sipconfig.inform("Fresh %s is being used." % sciversstr)
        else:
            sipconfig.error("The Fresh library could not be found in %s. If Fresh is installed then use the -o argument to explicitly specify the correct directory." % opts.freshlibdir)
    else:
        sipconfig.error("Qsci/qsciglobal.h could not be found in %s. If Fresh is installed then use the -n argument to explicitly specify the correct directory." % opts.freshincdir)
'''

def sip_flags():
    """Return the SIP flags.
    """
    # Get the flags used for the main PyQt module.
    flags = pyqt.pyqt_sip_flags.split()
    
    # Generate the API file.
    flags.append("-a")
    flags.append("fresh.api")

    # Add PyQt's .sip files to the search path.
    flags.append("-I")
    flags.append(pyqt.pyqt_sip_dir)

    return flags


def generate_code():
    """Generate the code for the Fresh module.
    """
    mname = "fresh"
    
    sipconfig.inform("Generating the C++ source for the %s module..." % mname)

    # Build the SIP command line.
    argv = ['"' + pyqt.sip_bin + '"']

    argv.extend(sip_flags())

    if not opts.no_docstrings:
        argv.append("-o");

    if opts.concat:
        argv.append("-j")
        argv.append(str(opts.split))

    if opts.tracing:
        argv.append("-r")

    argv.append("-c")
    argv.append(".")

    buildfile = os.path.join("fresh.sbf")
    argv.append("-b")
    argv.append(buildfile)

    if pyqt.pyqt_version >= 0x040000:
        argv.append("../Python/sip/fresh.sip")
    
    os.system(" ".join(argv))

    # Check the result.
    if not os.access(buildfile, os.F_OK):
        sipconfig.error("Unable to create the C++ code.")

    # Generate the Makefile.
    sipconfig.inform("Creating the Makefile for the %s module..." % mname)

    def fix_install(mfile):
        if sys.platform != "darwin" or opts.static:
            return

        mfile.write("\tinstall_name_tool -change libqscintilla2.%u.dylib %s/libqscintilla2.%u.dylib $(DESTDIR)%s/$(TARGET)\n" % (FRESH_API_MAJOR, opts.freshlibdir, FRESH_API_MAJOR, opts.freshmoddir))

    if pyqt.pyqt_version >= 0x040000:
        class Makefile(pyqt4.QtGuiModuleMakefile):
            def generate_target_install(self, mfile):
                pyqt4.QtGuiModuleMakefile.generate_target_install(self, mfile)
                fix_install(mfile)
    else:
        class Makefile(pyqt3.QtModuleMakefile):
            def generate_target_install(self, mfile):
                pyqt3.QtModuleMakefile.generate_target_install(self, mfile)
                fix_install(mfile)

    installs = []
    sipfiles = []

    for s in glob.glob("sip/*.sip"):
        sipfiles.append(os.path.join("sip", os.path.basename(s)))

    installs.append([sipfiles, os.path.join(opts.freshsipdir, mname)])

    installs.append(("fresh.api", os.path.join(opts.freshdir, "api", "python")))

    makefile = Makefile(
        configuration=pyqt,
        build_file="fresh.sbf",
        install_dir=opts.freshmoddir,
        installs=installs,
        static=opts.static,
        debug=opts.debug,
        universal=pyqt.universal)
    
    if fresh_define:
        makefile.extra_defines.append(fresh_define)
    makefile.extra_include_dirs.append('..')
    makefile.extra_include_dirs.append(opts.freshincdir)
    makefile.extra_lib_dirs.append(opts.freshlibdir)
    makefile.extra_lib_dirs.append('.')
    makefile.extra_libs.append("cppfresh")

    makefile.generate()


def main(argv):
    """Create the configuration module module.

    argv is the list of command line arguments.
    """
    global pyqt

    # Check SIP is new enough.
    if "snapshot" not in pyqt.sip_version_str:
        if pyqt.sip_version < sip_min_version:
            sipconfig.error("This version of Fresh requires SIP v%s or later" % sipconfig.version_to_string(sip_min_version))

    # Parse the command line.
    global opts

    p = create_optparser()
    opts, args = p.parse_args()

    if args:
        p.print_help()
        sys.exit(2)

    if opts.not_dll:
        global fresh_define
        fresh_define = ""

    # Set the version of PyQt explicitly.
    global qt_data_dir

    if pyqt4 is None:
        sipconfig.error("PyQt v4 was specified with the -p argument but doesn't seem to be installed.")
    else:
        pyqt = pyqt4.Configuration()
        qt_data_dir = pyqt.qt_data_dir
    
    # Now we know which version of PyQt to use we can set defaults for those
    # arguments that weren't specified.
    if opts.freshmoddir is None:
        opts.freshmoddir = pyqt.pyqt_mod_dir

    if opts.freshincdir is None:
        opts.freshincdir = pyqt.qt_inc_dir

    if opts.freshlibdir is None:
        opts.freshlibdir = pyqt.qt_lib_dir

    if opts.freshsipdir is None:
        opts.freshsipdir = pyqt.pyqt_sip_dir

    if opts.freshdir is None:
        opts.freshdir = os.path.join(qt_data_dir, "fresh")
    """
    # Check for Fresh.
    check_qscintilla()
    """
    # Tell the user what's been found.
    inform_user()

    # Generate the code.
    generate_code()


###############################################################################
# The script starts here.
###############################################################################

if __name__ == "__main__":
    try:
        main(sys.argv)
    except SystemExit:
        raise
    except:
        sys.stderr.write(
"""An internal error occured.  Please report all the output from the program,
including the following traceback, to monkeystudio.ide@gmail.com.
""")
        raise
