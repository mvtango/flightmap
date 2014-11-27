#! /bin/bash

DAY=$1  

AREA="(37,47),(40,49)"
OUTDIR=out/thursdays
NAME=$DAY-47493740-strict.json

mkdir -p $OUTDIR

bin/flightreduce.py --after $DAY --before $DAY  --area=$AREA --strict --flightdocs=$OUTDIR/$NAME

