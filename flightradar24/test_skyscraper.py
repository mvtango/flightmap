# Parameter

delay = 20

searchAirlines = ['AIB','GAF','BGA','ADB']
searchPlaneIds = ['D-AZEM','VC-1A','F-ZWUG','F-RARF','C5-GAF','AI-001','EP-GDS','MM-62174','MM-62209','MM-62243','20-1101','20-1102','PH-KBX','5U-BAG','NAF-001','SP-LIG','HZ-HM1A','YU-BNA','YU-BNZ','TC-ANA','TC-ATA']

usedb  = False
dbname = 'flightradar24_db'
dbuser = 'postgres'
dbpass = 'achim'
import pprint 


# Jetzt geht's los

def main():
    pass

if __name__ == '__main__':
    main()



# Importiere diverse Module ...
    
import urllib2
import datetime
import json
import time
import sys
import traceback
import os
import time
from skyscraper.client import Client
# from sets import Set
Set=frozenset
from zlib import decompress
import unicodedata
import logging
import locale
import codecs


## LOGGING 

_here=os.path.abspath(os.path.split(__file__)[0])

from logging.handlers import RotatingFileHandler
from logging import StreamHandler
handler=RotatingFileHandler("%s/log/jsonp-test%s.log" % (_here,__name__), mode="a", maxBytes=1024*1024*4, backupCount=5)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s %(lineno)s %(message)s "))
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)



if (usedb):
    try:
        connection = psycopg2.connect("dbname='" + dbname + "' user='" + dbuser + "' host='localhost' password='" + dbpass + "'")
    except:
        connection = False
        print "I am unable to connect to the database"

if not os.path.exists('dumps'):
    os.makedirs('dumps')
    
if not os.path.exists('filtered'):
    os.makedirs('filtered')

# initialisiere Suche

airlineSet = Set(searchAirlines)
planeIdSet = Set(searchPlaneIds)



# Beginne Scraping
# http://krk.fr24.com/zones/europe_all.js?callback=pd_callback&_=1380699512313
os.environ['TZ'] = 'EST-02'
time.tzset()
count = 0
planes = 0
lplanes=0
data = ""
SkyScraperClient=Client()

if __name__ == '__main__':

	with SkyScraperClient.create("Flightradar24 - test",
			      contacts=[dict(email="mv@datenfreunde.com",name="Martin Virtel")],
			      success_timer=delay*10) as watcher :
		while True :

			if count > 0:
				time.sleep(delay)
			   
			count += 1
			
				
			timeNow = time.localtime()
			timeString = time.strftime("%Y.%m.%d %H:%M:%S", timeNow)
			outputFilename = time.strftime("%Y-%m-%d", timeNow)
			
			# print timeString + ' (' + str(count) + ')'
			logger.info("scraper run # %s, %s planes" % (str(count),str(planes)))
			planeText = urllib2.urlopen("http://krk.fr24.com/zones/full_all.js").read()
			
			try :
				planeJSON = json.loads("{")
			except Exception, e:
				logger.exception(e)
				planeJSON=[]
		
			num=55	
			if (num>50) :
				watcher.success()
			else :
				watcher.log("%s Planes" % (num,))



	print "fertig"

