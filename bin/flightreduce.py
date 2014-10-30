#! /usr/bin/python
# coding: utf-8
#
import argparse
import sys,os
import csv
import re
import datetime
import pprint
import locale
import logging
import codecs
import bz2
import traceback
import copy 
import simplejson
from flightmap.airportlocator import nearest_airport
# import couchdb


# Quick fix for your example:
#import time
#from email.Utils import parsedate
#def cache_sort(i):
#    t = time.mktime(parsedate(i[1][1]['Date']))
#    return datetime.datetime.fromtimestamp(t)
# And monkey-patch cache_sort function:
#couchdb.http.cache_sort = cache_sort


_here=os.path.split(__file__)[0]
locale.setlocale(locale.LC_ALL, "de_DE.utf8")
logging.basicConfig(file=sys.stderr,level=logging.DEBUG,format="%(message)s")
logger=logging.getLogger(__name__)


bases={"filtered" : "raw/217.11.52.54/fly/filtered",
       "full"     : "raw/217.11.52.54/fly/dumps" ,
       "local"    : "/home/martin/projekte/flightmap/data/tsv",
       "dazem"    : "/home/martin/projekte/flightmap/data/dazem",
       "server"   : "/home/michael/flightradar_scraper/dumps-jsonp-filtered/",
       "server-old"   : "/home/michael/flightradar_scraper/filtered/",
       "nyx"      : "/home/opendatacity/scraper/flightradar24/dumps-jsonp-filtered/",
       "full"      : "/home/opendatacity/scraper/flightradar24/dumps-jsonp/"
        }



fieldnames={ 'old' : ["time","flight","hex","lat","lng","head","alt","speed","squawk","radar","type","reg","stamp"],
             'new' : ["time","flight","hex","lat","lng","head","alt","speed","squawk","radar","type","reg","stamp","fair","tair","fcode","e1","e2","e3","e4"]
		   }

parser = argparse.ArgumentParser(description="fd24 extractor", conflict_handler='resolve')
parser.add_argument('infiles',nargs="*")
parser.add_argument('--listfiles',action="store_const",help="list files only, no output", default=0, const=1)
parser.add_argument('--registration',action="store",help="search for flight registration", default=None)
parser.add_argument('--after',action="store",help="files after Year-Month-Day (exclusive)", default="2012-07-01")
parser.add_argument('--before',action="store",help="files before Year-Month-Day (exclusive)", default=datetime.datetime.now().strftime("%Y-%m-%d"))
parser.add_argument('--basedir', action="store",help="base directory for selection, try %s" % ",".join(['"%s"' % a for a in bases.keys()]),default="full")
parser.add_argument('--flightgap', action="store",help="start a new flight after N minutes without data", default=30)
parser.add_argument('--flightfile', action="store",help="output file for flight geoJSON, default: stdout", default=sys.stdout)
parser.add_argument('--input_delimiter', action="store",help="delimiter character for input file(s), default is '<tab>'",default="\t")
parser.add_argument('--flightdocs', action="store",help="json docs file", default=None)
parser.add_argument('--fieldnames', action="store",help="fieldname sequence, options: %s" % ",".join(fieldnames.keys()), default="old")
parser.add_argument('--area', action="store",help="overflown area, format: (long,lat),(long,lat) the two points are endpoints of a diagonal that marks the requested area" , default="")


args = vars(parser.parse_args())

# output_fields=["fn","rn","time","lat","lng","head","speed","alt","reg"]

output_fields=["time", "reg","type","lat","lng","alt","speed","head","flight","radar","reason","squawk","stime"]
output_base="raw/extracted"

# fieldnames=["time","flight","hex","lat","lng","head","alt","speed","squawk","radar","type","reg","stamp"]

def map_rec(rec,where="") :
	errors=[]
	for ic in ("head","alt","speed","stamp") :
		try :
			rec[ic]=int(rec[ic])
		except ValueError,e  :
			errors.append("invalid integer %s=%s [%s]" % (ic,rec[ic],e))
		except KeyError :
			errors.append("no '%s'" % (ic,))
	for ic in ("lat","lng") :
		try :
			# if rec[ic].find(".") == -1 :
			#	raise(ValueError,"no . in float")
			rec[ic]=float(rec[ic])
		except ValueError,e :
			errors.append("%s : %s, %s" % (e,ic,rec[ic]))
			#logger.error("%s %s=%s in %s (%s)" (e,ic,rec[ic],repr(rec),where))
		except KeyError :
			errors.append("no '%s'" % (ic,))

	rec["stime"]=datetime.datetime.fromtimestamp(rec["stamp"]).strftime('%Y-%m-%d %H:%M:%S')
	if errors :
		logger.error("%s errors: %s in %s" % (len(errors),",".join(errors),repr(rec)))
	return rec

from opener import f_open 

#def f_open(a) :
#	if re.search("\.bz2$",a) :
#		return bz2.BZ2File(a,"r")
#	return open(a,"r")


def seek_time(pot) :
	minseek=pot-datetime.timedelta(minutes=1)
	filesearch=re.compile(pot.strftime("/%Y-%m-%d[^/]+$"))
	minstamp=minseek.strftime("%Y.%m.%d %H:%M:%S")
	f=[a for a in args["infiles"] if filesearch.search(a)] 
	if f :
		tf=f_open(f[0])
		print "FN: %s" % (fieldnames[args["fieldnames"]])
		records=csv.DictReader(tf, fieldnames=fieldnames[args["fieldnames"]], delimiter=args["input_delimiter"])
		for rec in records :
			if rec["time"]>minstamp :
				return records
	else :
		return False
	

def seek_pos(st) :
	(reg,pt)=st.split("@")
	logger.info("Seeking %s pos %s" % (reg,pt))
	pt=datetime.datetime.strptime(pt,"%Y-%m-%d:%H:%M")
	pm=(pt+datetime.timedelta(minutes=30)).strftime("%Y.%m.%d %H:%M:%S")
	records=seek_time(pt)
	for rec in records :
		if rec["reg"]==reg :
			return rec
		if rec["time"]>pm :
			break
	return False

already={  }
flights={ }

def test_threshold(rec,threshold={},output=None,flights=False) :
		#logging.debug("Testing %s" % repr(rec))
		registration=rec["reg"]
		if flights :
			push_flight(rec)
		if not registration in already :
			rec["reason"]="new"
			already[registration]={ "output": rec, "silenced" : None }
			#logger.debug(" - new!")
			return True
		recorded=already[registration]
		for (vi,va) in threshold.items() :
			#try :
			#	logger.debug("%s: actual %s, output %s, silenced %s" % (vi,vi in rec and rec[vi],vi in recorded["output"] and recorded["output"][vi],recorded["silenced"] and vi in recorded["silenced"] and recorded["silenced"]["vi"]))				
			#except KeyError :
			#	pass
			if (abs(rec[vi]-recorded["output"][vi])>va) :
				if ((vi=="stamp") and recorded["silenced"] and (abs(rec[vi]-recorded["silenced"][vi])>va)):
					recorded["silenced"]["reason"]="timegap"
					output.writerow(recorded["silenced"])
					# logger.debug("threshold for last silenced record reached for %s" % vi)
					recorded["silenced"]=None
				recorded["silenced"]=None
				recorded["output"]=rec
				rec["reason"]="thr %s>%s" % (vi,va)
				return True
		# logger.debug ("--- will be silenced")
		
		recorded["silenced"]=rec
		return False

def push_flight(rec,new=False) :
	key=rec["hex"]
	sec=int(args["flightgap"])*60
	point={}
	for k in ("lat","lng","alt","head","speed","stamp","stime","reg","squawk","radar") :
		point[k]=rec[k]
	if not key in flights :
		info={ "flights" : [ [point] ] }
		for k in ("reg","hex","type","radar","fair","tair","fcode") :
			info[k]=rec.get(k,"")
		flights[key]=info
	else :
		plane=flights[key]
		elapsed=(point["stamp"]-plane["flights"][-1][-1]["stamp"])
		# logger.info("Delta: %s < %s" % (elapsed,sec))
		if elapsed>sec :
			plane["flights"].append([point])
			# logger.info("New flight #%s" % len(plane["flights"]))
		else :
			plane["flights"][-1].append(point)
			
def find_filter() :
	""" returns function if there is an area to filter, false otherwise """
	if not args["area"] :
		return lambda a: True
	try :
		area=re.split(r"[^0-9\.]+",args["area"])
		assert len(area)==6
		longs=[float(area[1]),float(area[3])]
		lats=[float(area[2]),float(area[4])]	
	except Exception, e:
		logger.debug("invalid argument: --area {0} - expected format: (long,lat),(long,lat)".format(args["area"],))
		return lambda a: True 
	lats.sort()
	longs.sort()
	logger.debug("{lats} {longs}".format(**locals()))
	def filter_flight(fjson) :
		no=[]
		for c in fjson["geometry"]["coordinates"] :
			if (c[1]>=lats[0] and c[1]<=lats[1]) and (c[0]>=longs[0] and c[0]<=longs[1]) :
				return True
			else :
				no.append("%s" % c)
		logger.debug(" ".join(no[:10]))
		return False
	return filter_flight 

		



if __name__== "__main__" :
	import pprint
	startmoment=datetime.datetime.now()
	if not os.path.exists(args["basedir"]) :
		if args["basedir"] in bases:
			args["basedir"]=bases[args["basedir"]]
	if (args["infiles"] and len(args["infiles"])>0) :
		args["infiles"].sort(lambda a,b: cmp(os.path.split(a)[1],os.path.split(b)[1]))
		logger.debug("%s files as arguments" % len(args["infiles"]))
	else :
		try :
			available=os.listdir(args["basedir"])
		except Exception, e:
			logger.error("No files found in %s, Error: %s" % (args["basedir"],e))
			exit()
		available.sort(lambda a,b: cmp(a,b))
		args["infiles"]=[os.path.join(args["basedir"],a) for a in available if ((a>args["after"]) and (a[:len(args["before"])]<=args["before"]))]
		logger.debug("%s files selected from %s in range [%s,%s]" % (len(args["infiles"]),args["basedir"],args["after"],args["before"]))
	rect=0
	for fn in args["infiles"] :
		if args["listfiles"] :
			logger.debug("selected: %s" % fn)
			continue			
		logger.debug("Opening %s for input " % fn)
		inp=f_open(fn)
		recc=0
		records=csv.DictReader(inp, fieldnames=fieldnames[args["fieldnames"]], delimiter=args["input_delimiter"])
		testfunc=test_threshold
		for rec in records :
			try :
				recc=recc+1
				rect=rect+1
				if (recc % 1000000)==0 :
					logger.info("%s:%s Mio. records" % (fn,recc/1000000))
				if args["registration"] :
					if not rec["reg"][:len(args["registration"])]==args["registration"] :
						continue
				map_rec(rec)
				push_flight(rec)
			except Exception,e :
				logger.error(traceback.format_exc())
				logger.error("error %s for %s (#%s)" % (e,pprint.pformat(rec),recc))
		inp.close()
	elapsed=datetime.datetime.now()-startmoment
	logger.info("%.2f Mio. records read in %s min %s sec." % (float(rect)/1000000,int(elapsed.seconds/60),elapsed.seconds % 60))
	if args["flightgap"] :
		if not hasattr(args["flightfile"],"write") :
			o=open(args["flightfile"],"w") 
		else :
			o=args["flightfile"]
		fs=[]
		flightfilter=find_filter()
		for (hcode,plane) in flights.items() :
			props={}
			for (k,v) in plane.items() :
				if type(v) == type("") :
					props[k]=v 
			for flight in plane["flights"] :
				fprops=copy.copy(props)
				fprops["starttime"]=flight[0]["stime"]
				fprops["endtime"]=flight[-1]["stime"]
				fprops["start"]=nearest_airport(float(flight[0]["lng"]),float(flight[0]["lat"]))[0]
				fprops["start"]["airport"]=fprops["fair"]
				fprops["start"]["point"]=flight[0]
				fprops["end"]=nearest_airport(float(flight[-1]["lng"]),float(flight[-1]["lat"]))[0]			
				fprops["end"]["point"]=flight[-1]
				fprops["end"]["airport"]=fprops["tair"]
				del fprops["tair"]
				del fprops["fair"]
				fprops["duration"]=flight[-1]["stamp"]-flight[0]["stamp"]
				fprops["alt"]=[ a["alt"] for a in flight ]
				fprops["points"]=[ p for p in flight ]
			

				flightid="%s-%s" % (hcode,flight[0]["stime"].replace(" ",""))
				#logger.debug("FPROPS: %s" % pprint.pformat(fprops))
				flightjson= { "properties" : fprops, "id" : flightid, "type" : "Feature", 
				               "geometry" : { "type" : "LineString", 
				               "coordinates" : [ [float(a["lng"]),float(a["lat"])] for a in flight] }  }
				if flightfilter(flightjson) :
					fs.append(flightjson)
		# simplejson.dump(fs,o)
		logger.info("%s flights recorded to %s" % (len(fs),args["flightfile"]))
		if args["flightdocs"]:
			dcs=map(lambda a :  { 		"start"     : { "time" : a["properties"]["starttime"].replace(" ","T"),
														"alt"  : a["properties"].get("points",[{ 'alt' : None }])[0]["alt"],
														"town" : a["properties"]["start"]["town"],
														"country" : a["properties"]["start"]["country"],
														"dist" : a["properties"]["start"]["distance"],
														"speed": a["properties"].get("points",[{ 'speed' : None }])[0]["speed"]
													 },
										"end"     : {   "time" : a["properties"]["endtime"].replace(" ","T"),
														"alt"  : a["properties"].get("points",[{ 'alt' : None }])[0]["alt"],
														"town" : a["properties"]["end"]["town"],
														"country" : a["properties"]["end"]["country"],
														"dist" : a["properties"]["end"]["distance"]	,
														"speed": a["properties"].get("points",[{ 'speed' : None }])[-1]["speed"]
													 },
										"route"     : a["geometry"],
										"duration"  : float("%.2f" % (float(a["properties"]["duration"])/3600),),
										"reg"		: a["properties"]["reg"],
										"flight"    : a["properties"]["reg"],
										"radar"     : a["properties"]["radar"],
										"hex"       : a["properties"]["hex"],
										"type"      : a["properties"]["type"],
										"datum"     : a["properties"]["starttime"][:10],
										"id"        : a["id"] }, fs) # filter(lambda a: a["properties"].get("points",False),fs))
			if args["flightdocs"] :
				if args["flightdocs"]=="-" :
					fdof=sys.stdout
				else :
					fdof=open(args["flightdocs"],"w")
				simplejson.dump(dcs,fdof)
				logger.info("%s flights saved to to json doc list %s" % (len(dcs),args["flightdocs"]))

				
