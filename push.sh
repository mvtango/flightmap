#! /bin/bash 
cd ~/projekte/flightmap
rsync -rv ./html/  martin@bitbucket:/home/martin/m.virtel.de/web/htdocs/embed/dazem
