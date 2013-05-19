#! /bin/bash

FILE="data/openflights.airports.csv"
cp $FILE-header.csv $FILE
wget --output-document=- http://openflights.svn.sourceforge.net/viewvc/openflights/openflights/data/airports.dat >>$FILE

