#!/bin/sh

QRC_FILE=enkiicons.qrc
RESOURCE_FILE=../enki/resources/icons.py

TMP_RESOURCE_FILE=/tmp/icons.py

echo '<RCC>' > $QRC_FILE
echo '	<qresource prefix="/enkiicons" >' >> $QRC_FILE
for file in `ls -d *.png languages/*.png logo/* logo/*/*`; do \
	echo '		<file>'$file'</file>' >> $QRC_FILE;
done
echo '	</qresource>' >>$QRC_FILE
echo '</RCC>' >> $QRC_FILE

pyrcc4 -o $TMP_RESOURCE_FILE $QRC_FILE

grep -v '^qInitResources()' $TMP_RESOURCE_FILE > $RESOURCE_FILE

rm $TMP_RESOURCE_FILE