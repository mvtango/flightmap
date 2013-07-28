#! /bin/bash 
cd ~/projekte/flightmap
rsync -rvv ./html/  martin@bitbucket:/home/martin/m.virtel.de/web/htdocs/embed/dazem
