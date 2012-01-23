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
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

class BufferedPopen:
    """Bufferred version of Popen.
    Never locks, but uses unlimited buffers. May eat all the system memory, if something goes wrong.
    """
    
    def __init__(self, command):
        self._command = command
        
        self._inQueue = Queue()
        self._outQueue = Queue()

        self._inThread = None
        self._outThread = None
        self._popen = None
    
    def start(self):
        """Start the process
        """
        env = copy.copy(os.environ)
        env['COLUMNS'] = str(2**16)  # Don't need to break lines in the mit scheme. It will be done by text edit
        env['LINES'] = '25'
        self._popen = subprocess.Popen(self._command,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

        self._inThread = threading.Thread(target=self._writeInputThread)
        self._inThread.name = 'mks.buffpopen.input'
        self._outThread = threading.Thread(target=self._readOutputThread)
        self._inThread.setName('mks.buffpopen.output')

        self._mustDie = False
        self._inThread.start()
        self._outThread.start()

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
        if self._inThread is not None and self._outThread.is_alive():
            self._outThread.join()
    
    def isAlive(self):
        """Check if process is alive
        """
        return self._popen.poll() is None

    def _readOutputThread(self):
        """Reader thread function. Reads output from process to queue
        """
        # hlamer: Reading output by one character is not effective, but, I don't know 
        # how to implement non-blocking reading of not full lines better
        char = self._popen.stdout.read(1)
        while char:
            self._outQueue.put(char)
            char = self._popen.stdout.read(1)
            

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
        if not self.isAlive():  # Ooops, the process is dead
            raise RuntimeWarning("Process is not running")
        self._inQueue.put(text)  # TODO test on big blocks of text. Make nonblocking even if queue is full

    def readOutput(self):
        """Read stdout data from the subprocess
        """
        text = ''
        while not self._outQueue.empty():
            text += self._outQueue.get(False)
        return text
