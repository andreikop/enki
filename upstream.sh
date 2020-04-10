#!/bin/bash

PYTHONPATH=$(pwd)/../qutepart:$(pwd):$PYTHONPATH python3 enki $@
