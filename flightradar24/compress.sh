#! /bin/bash
cd `dirname $0`
find dumps dumps-jsonp  -type f ! -name "*.bz2" -mtime +2 -print | xargs bzip2 -v >compress.log 2>&1 
