#! /bin/bash 
cd ~/projekte/flightmap
rsync -rv ./dazem-view/  martin@bitbucket:/home/martin/m.virtel.de/web/htdocs/embed/dazem
