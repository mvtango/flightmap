#! /bin/bash

FILE="data/openflights.airports.csv"
cp $FILE-header.csv $FILE
wget --output-document=- "http://sourceforge.net/p/openflights/code/HEAD/tree/openflights/data/airports.dat?format=raw" >>$FILE

