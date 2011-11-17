#!/bin/sh

rm -rf html
sphinx-build . html
cp -R screenshots html
