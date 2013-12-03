#!/usr/bin/env python

import os
from os.path import join
import subprocess

for root, dirs, files in os.walk('.'):
    for name in files:
        full_path = join(root, name)
        # See if the given file is executable.
        if full_path.endswith('.py') and os.access(full_path, os.X_OK) and (not full_path.endswith('run_all.py')):
            print('Running ' + full_path)
            subprocess.call(['python', full_path])
    
