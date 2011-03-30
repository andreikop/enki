#!/bin/sh

QRC_FILE=mksicons.qrc
RESOURCE_FILE=../mks/resources/icons.py

echo '<RCC>' > $QRC_FILE
echo '	<qresource prefix="/mksicons" >' >> $QRC_FILE
for file in `ls *.png`; do \
	echo '		<file>'$file'</file>' >> $QRC_FILE;
done
echo '	</qresource>' >>$QRC_FILE
echo '</RCC>' >>$QRC_FILE

pyrcc4 -o $RESOURCE_FILE $QRC_FILE