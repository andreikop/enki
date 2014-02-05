"""
buffpopen --- Buffered subprocess. Popen implementation
=======================================================

This implementation allows to read and write output without blocking
"""

import subprocess
import threading
import os
import copy
import time

try:
    from Queue import Queue, Empty, Full
except ImportError:
    from queue import Queue, Empty, Full  # python 3.x


class BufferedPopen:
    """Bufferred version of Popen.
    Never locks, but uses unlimited buffers. May eat all the system memory, if something goes wrong.
    """

    def __init__(self, command):
        self._command = command

        self._inQueue = Queue(8192)
        self._outQueue = Queue(8192)
        self._errQueue = Queue(8192)

        self._inThread = None
        self._outThread = None
        self._errThread = None
        self._popen = None

    def start(self, args):
        """Start the process
        """
        env = copy.copy(os.environ)
        env['COLUMNS'] = str(2**16)  # Don't need to break lines in the mit scheme. It will be done by text edit
        env['LINES'] = '25'

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

        self._popen = subprocess.Popen(self._command.split() + args,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       startupinfo=si, env=env)

        self._inThread = threading.Thread(target=self._writeInputThread,
                                          name='enki.lib.buffpopen.input')
        self._outThread = threading.Thread(target=self._readOutputThread,
                                           kwargs={'pipe': self._popen.stdout},
                                           name='enki.lib.buffpopen.stdout')
        self._errThread = threading.Thread(target=self._readOutputThread,
                                           kwargs={'pipe': self._popen.stderr},
                                           name='enki.lib.buffpopen.stderr')

        self._mustDie = False
        self._inThread.start()
        self._outThread.start()
        #self._errThread.start()

    def stop(self):
        """Stop the process
        """
        self._mustDie = True

        if self._popen is not None:
            try:
                self._popen.terminate()
            except OSError:  # OK, it is already dead
                pass

            for i in range(5):
                if self._popen.poll() is None:
                    time.sleep(0.04)
                else:
                    break
            else:
                self._popen.kill()
                self._popen.wait()
                self._popen = None

        if self._inThread is not None and self._inThread.is_alive():
            self._inThread.join()
        if self._outThread is not None and self._outThread.is_alive():
            self._outThread.join()
        if self._errThread is not None and self._errThread.is_alive():
            self._errThread.join()

    def isAlive(self):
        """Check if process is alive
        """
        return self._popen.poll() is None

    def _readOutputThread(self, pipe):
        """Reader thread function. Reads output from process to queue
        """
        # hlamer: Reading output by one character is not effective, but, I don't know
        # how to implement non-blocking reading of not full lines better
        def read():
            if self.isAlive():
                return pipe.read(1)
            else:
                return pipe.read()

        text = read()
        while text and not self._mustDie:
            try:
                self._outQueue.put(text, False)
            except Full:
                time.sleep(0.01)
                continue

            text = read()

    def _writeInputThread(self):
        """Writer thread function. Writes data from input queue to process
        """
        while not self._mustDie:
            try:
                text = self._inQueue.get(True, 0.1)
            except Empty:
                continue

            self._popen.stdin.write(text)

    def write(self, text):
        """Write data to the subprocess
        """
        if not self.isAlive():
            return  # Ooops, the process is dead. It doesn't need any output

        self._inQueue.put(text)  # TODO test on big blocks of text. Make nonblocking even if queue is full

    def readOutput(self):
        """Read stdout data from the subprocess
        """
        text = ''
        while not self._outQueue.empty() and len(text) < 256:
            text += self._outQueue.get(False)
        return text
