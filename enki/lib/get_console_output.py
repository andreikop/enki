"""Run console command and get it output syncronously

Popen wrapper, which does some platform specific hacks
"""

import subprocess
import os, os.path
import sys

# Determine if we're frozen with Pyinstaller or not.
if getattr(sys, 'frozen', False):
    isFrozen = True
else:
    isFrozen = False


def open_console_output(command, cwd):
    if hasattr(subprocess, 'STARTUPINFO'):  # windows only
        # On Windows, subprocess will pop up a command window by default when run from
        # Pyinstaller with the --noconsole option. Avoid this distraction.
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so it will.
        env = os.environ
    else:
        si = None
        if isFrozen and sys.platform.startswith('linux'):
            # Prepend the path to the frozen executable, since several other
            # utilities (Sphinx, ctags, etc.) are there.
            env = {'PATH': os.path.dirname(sys.executable) + ':' + os.environ['PATH']}
        else:
            env = None

    # On Windows, running this from the binary produced by Pyinstller
    # with the --noconsole option requires redirecting everything
    # (stdin, stdout, stderr) to avoid a OSError exception
    # "[Error 6] the handle is invalid."
    popen = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            startupinfo=si, env=env, cwd=cwd)

    return popen

def get_console_output(command, cwd=None):
    popen = open_console_output(command, cwd)
    return popen.communicate()
