#! /bin/bash
cd `dirname $0`
find dumps dumps-jsonp  dumps-jsonp-filtered -type f ! -name "*.bz2" ! -name "*.7z" -mtime +2 -print |  xargs -I {} 7za a {}.7z {} && rm {} >compress.log 2>&1 
