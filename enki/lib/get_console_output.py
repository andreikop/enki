"""Run console command and get it output syncronously

Popen wrapper, which does some platform specific hacks
"""

import subprocess
import os


def get_console_output(command, args):
    if hasattr(subprocess, 'STARTUPINFO'):  # windows only
        # On Windows, subprocess will pop up a command window by default when run from
        # Pyinstaller with the --noconsole option. Avoid this distraction.
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so it will.
        env = os.environ
    else:
        si = None
        env = None

    # On Windows, running this from the binary produced by Pyinstller
    # with the --noconsole option requires redirecting everything
    # (stdin, stdout, stderr) to avoid a OSError exception
    # "[Error 6] the handle is invalid."
    popen = subprocess.Popen(
            [command] + args,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            startupinfo=si, env=env)

    return popen.communicate()
