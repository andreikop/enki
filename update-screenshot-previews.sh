#!/bin/sh

cd screenshots && ls *.png | xargs -i convert -scale 16% {} preview/{}
