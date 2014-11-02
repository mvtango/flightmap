#! /bin/sh

cd /home/opendatacity/flightmap/bin

start=`date --date="20 days ago"  +%Y-%m-%d`
log=log/daily-insert.log

(date; python ./flightreduce.py --after=$start --base=nyx --flightdocs=- | python ./uploadsearch.py )  >>$log 2>&1 

tail -1000 $log >>$log.tmp

mv $log.tmp $log 

date >>$log



