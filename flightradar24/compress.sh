#! /bin/bash
cd `dirname $0`
find dumps dumps-jsonp  dumps-jsonp-filtered -type f ! -name "*.bz2" ! -name "*.7z" -mtime +2 -print |  xargs -I {} sh -c "7za a {}.7z {} && rm {}"  2>&1 >compress.log
