#! /bin/sh

cd /home/mvirtel/projekte/flightmap/bin

start=`date --date="2 days ago"  +%Y-%m-%d`
log=log/daily-insert.log

(date; python ./flightreduce.py --after=$start --base=server --flightdocs=- | python ./uploadsearch.py )  >>$log 2>&1 

tail -1000 $log >>$log.tmp

mv $log.tmp $log 



