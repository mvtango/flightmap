# Parameter

delay = 20

searchAirlines = ['AIB','GAF','BGA','ADB']
searchPlaneIds = ['D-AZEM','VC-1A','F-ZWUG','F-RARF','C5-GAF','AI-001','EP-GDS','MM-62174','MM-62209','MM-62243','20-1101','20-1102','PH-KBX','5U-BAG','NAF-001','SP-LIG','HZ-HM1A','YU-BNA','YU-BNZ','TC-ANA','TC-ATA','D-ALMS','D-ASIE','D-CMRM','D-CSIM','D-CLMS','D-CFCF','D-CKNA','D-CAWS','D-CHLR','CS-DRX','CS-DFC','D-AGSI','D-ALIL','D-CINS','D-CURA','D-CSIE','D-CELE','D-CADN','D-BADA','D-BADC','D-CSKY','D-CRAN','D-CBWW','D-CFCF']

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
import re


## LOGGING 

_here=os.path.abspath(os.path.split(__file__)[0])

from logging.handlers import RotatingFileHandler
from logging import StreamHandler
handler=RotatingFileHandler("%s/log/jsonp%s.log" % (_here,__name__), mode="a", maxBytes=1024*1024*4, backupCount=5)
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

	planeRE=re.compile(r'"[^"]+":\[[^\]]+]')


	while True : 
		with SkyScraperClient.create("Flightradar24",
		      contacts=[dict(email="sss@gmx.info",name="Martin Virtel")],
		      success_timer=delay*10) as watcher :
			if count > 0:
				time.sleep(delay)
			   
			count += 1
			
				
			timeNow = time.localtime()
			timeString = time.strftime("%Y.%m.%d %H:%M:%S", timeNow)
			outputFilename = time.strftime("%Y-%m-%d", timeNow)
			
			# print timeString + ' (' + str(count) + ')'
			logger.info("scraper run # %s, %s planes" % (str(count),str(planes)))
			planeText = urllib2.urlopen("http://krk.fr24.com/zones/full_all.js").read()
			planeJSON={}
			iterator=planeRE.finditer(planeText)
			cont=True
			while cont :
				try :
					jstr="{%s}" % iterator.next().group()
    				except StopIteration :
        				cont=False
				else :
					try :
						obj=json.loads(jstr)
					except :
						logger.debug("Error with %s" % jstr , exc_info=True)
					else :
        					planeJSON.update(obj)
				finally :
					pass



				



			
			dumpFile = codecs.open("dumps-jsonp/"+outputFilename+".tsv", "a","utf-8")
			filteredFile = codecs.open("dumps-jsonp-filtered/"+outputFilename+".tsv", "a","utf-8") 
								
			print("Processing %s positions" % len(planeJSON.keys()))			
			for code in planeJSON.keys():
				planes += 1
				data = planeJSON[code]
				if (type(data) == type([])) :
					print "Data (OK) %s %s" % (planes,data)
					data = [timeString, code] + data
		
					for i in range(len(data)):
						if isinstance(data[i], basestring):
							data[i] = data[i]
						else:
							data[i] = str(data[i])
				
					line = '\t'.join(data) + '\n'
					try :
						dumpFile.write(line)
					except UnicodeEncodeError,e :
						logger.error("Error encoding %s:%s" % (repr(line),e))
				
					if (data[11] in planeIdSet) or (code[0:3] in airlineSet):
						try :
							filteredFile.write(line)
						except UnicodeEncodeError,e :
							logger.error("Error encoding %s:%s" % (repr(line),e))
				else :
					print "Data (not ok): %s" % data
			print("Processed %s positions" % len(planeJSON.keys()))			
			logger.debug("Processed %s positions" % len(planeJSON.keys()))			
			num=planes-lplanes
			lplanes=planes
			if (num>50) :
				watcher.success()
			else :
				watcher.log("%s Planes" % (num,))



	print "fertig"

