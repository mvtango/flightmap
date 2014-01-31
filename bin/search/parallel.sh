#! /bin/bash

outdir=/home/mvirtel/projekte/flightmap/extracted-copter/
max=10


function on_exit() 
{
	PIDS=`ps --ppid $$ --no-headers -o pid `
	kill -TERM $PIDS >/dev/null 2>&1
	echo Killed: $PIDS
}

trap on_exit EXIT

MAX=20

# 
# SEARCH='D-ALMS|D-ASIE|D-CMRM|D-CSIM|D-CLMS|D-CFCF|D-CKNA|D-CAWS|D-CHLR|CS-DRX|CS-DFC|D-AGSI|D-ALIL|D-CINS|D-CURA|D-CSIE|D-CELE|D-CADN|D-BADA|D-BADC|D-CSKY|D-CRAN|D-CBWW|D-CFCF'

SEARCH='D-HBAY|D-HAIT|D-HBYA|D-HBYF|D-HBYH|D-HDAC|D-HDCL|D-HDEC|D-HDFI|D-HDMA|D-HDPS|D-HEIM|D-HELM|D-HELP|D-HGAB|D-HGWD|D-HGYN|D-HHBG|D-HHIT|D-HIPT|D-HJAR|D-HJMD|D-HKUD|D-HKUG|D-HLCK|D-HLFR|D-HLGB|D-HLIR|D-HDMX|D-HLTB|D-HMMR|D-HMUS|D-HMUM|D-HMUZ|D-HOPI|D-HPMM|D-HRAV|D-HRAC|D-HRET|D-HSMA|D-HSOS|D-HSFB|D-HSMA|D-HSAN|D-HSFB|D-HSWG|D-HUHN|D-HUPE|D-HUTH|D-HWFH|D-HWVS'

for INPUT in `cat jobs` ; do


	children=`ps --ppid $$ --no-headers -o pid | wc -w`	
	while [ $children -gt $MAX ] ; do 
		echo Waiting $children children `du $outdir`
		sleep 10
		children=`ps --ppid $$ --no-headers -o pid | wc -w`	
	done 
	
	OUT=$outdir`basename $INPUT`.tsv
	
        bzcat $INPUT | egrep $SEARCH > $OUT &
	sleep 1
	children=`ps --ppid $$ --no-headers -o pid | wc -w`	
	echo Running $children $children
	echo `cat $outdir/*tsv | cut -f 12 | sort -u | grep -- - ` 
        echo `ls -1 $outdir | wc -l ` files ; cat /proc/loadavg;


done


children=`ps --ppid $$ --no-headers -o pid | wc -w`	
while [ $children -gt 3 ] ; do 
		echo Finished ... waiting $children
		sleep 10
		children=`ps --ppid $$ --no-headers -o pid | wc -w`	
done 

