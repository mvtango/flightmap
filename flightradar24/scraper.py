# Parameter

delay = 20

searchAirlines = ['AIB','GAF','BGA','ADB']
searchPlaneIds = ['D-AZEM','VC-1A','F-ZWUG','F-RARF','C5-GAF','AI-001','EP-GDS','MM-62174','MM-62209','MM-62243','20-1101','20-1102','PH-KBX','5U-BAG','NAF-001','SP-LIG','HZ-HM1A','YU-BNA','YU-BNZ','TC-ANA','TC-ATA']

usedb  = False
dbname = 'flightradar24_db'
dbuser = 'postgres'
dbpass = 'achim'



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
from sets import Set
from zlib import decompress
import unicodedata
import logging
import locale
import codecs
from threading import Timer
import thread, time, sys

## LOGGING 

_here=os.path.abspath(os.path.split(__file__)[0])

from logging.handlers import RotatingFileHandler
from logging import StreamHandler
handler=RotatingFileHandler("%s/log/%s.log" % (_here,__name__), mode="a", maxBytes=1024*1024*4, backupCount=5)
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


def timeout() :
	logger.error("Timer interrupted main thread")
	thread.interrupt_main()




# Beginne Scraping

os.environ['TZ'] = 'EST-02'
time.tzset()
count = 0
planes = 0
data = ""
timer = None

if __name__ == '__main__':

	while True :

		if count > 0:
			time.sleep(delay)
		if timer is not None :
			timer.cancel()
			logger.debug("Timer set to 5")
			timer=Timer(5,timeout) # delay+40,timeout)
			timer.start()

		   
		count += 1
		
		try:
			
			
			timeNow = time.localtime()
			timeString = time.strftime("%Y.%m.%d %H:%M:%S", timeNow)
			outputFilename = time.strftime("%Y-%m-%d", timeNow)
			
			# print timeString + ' (' + str(count) + ')'
			logger.info("scraper run # %s, %s planes" % (str(count),str(planes)))
			planeText = urllib2.urlopen("http://www.flightradar24.com/PlaneFeed.json").read()
			
			planeJSON = json.loads(planeText)
			
			dumpFile = codecs.open("dumps/"+outputFilename+".tsv", "a","utf-8")
			filteredFile = codecs.open("filtered/"+outputFilename+".tsv", "a","utf-8") 
					
			for code in planeJSON:
				planes += 1
				data = planeJSON[code]
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

		
		except KeyboardInterrupt:
			break
		
		except Exception, e:
			logger.error("%s - data: %s" % (traceback.format_exc(),data))
			


	logger.debug("Exited") 

