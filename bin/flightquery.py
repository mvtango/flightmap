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

_here=os.path.split(__file__)[0]
locale.setlocale(locale.LC_ALL, "de_DE.utf8")
logging.basicConfig(file=sys.stderr,level=logging.DEBUG,format="%(message)s")
logger=logging.getLogger(__name__)




fieldnames={ 'old' : ["time","flight","hex","lat","lng","head","alt","speed","squawk","radar","type","reg","stamp"],
             'new' : ["time","flight","hex","lat","lng","head","alt","speed","squawk","radar","type","reg","stamp","fair","tair","fcode","e1","e2","e3","e4"]
		   }
 
bases={"filtered" : "raw/217.11.52.54/fly/filtered",
       "full"     : "/home/opendatacity/flightmap/flightradar24/dumps-jsonp", 
       "filtered"     : "/home/opendatacity/flightmap/flightradar24/dumps-jsonp-filtered", 
	}

parser = argparse.ArgumentParser(description="fd24 extractor", conflict_handler='resolve')
parser.add_argument('infiles',nargs="*")
parser.add_argument('--output',action="store",help="output file, default is stdout. Files will be accessible in http://projekte.ftd.de/~mvirtel/flightdata/extracted/ and below ", default=sys.stdout)
parser.add_argument('--every',action="store",help="record positions only every N minutes",type=int, metavar="N", default=60)
parser.add_argument('--slower',action="store",help="record positions only if speed below N; if set to 0, don't filter by speed - this is the default",type=int, metavar="N", default=0)
parser.add_argument('--listfiles',action="store_const",help="list files only, no output", default=0, const=1)
parser.add_argument('--by_registration',action="store_const",help="output a different file for every aircraft registration code, see filname_template for setting the filename and path", default=0, const=1)
parser.add_argument('--registration','-r', action="append",help="search for flight registration", default=None)
parser.add_argument('--filename_template',action="store",help="filename template for matched records", default="raw/extracted/by-registration/reg-%(reg)s.csv")
parser.add_argument('--after',action="store",help="files after Year-Month-Day (exclusive)", default="2012-07-01")
parser.add_argument('--before',action="store",help="files before Year-Month-Day (exclusive)", default=datetime.datetime.now().strftime("%Y-%m-%d"))
parser.add_argument('--basedir', action="store",help="base directory for selection, try %s" % ",".join(['"%s"' % a for a in bases.keys()]),default="filtered")
parser.add_argument('--output_delimiter', action="store",help="delimiter character for output file(s), default is ';'",default=";")
parser.add_argument('--input_delimiter', action="store",help="delimiter character for input file(s), default is '<tab>'",default="\t")
parser.add_argument('--find', action="store",help="find aircraft position, registration@year-month-day:hour:minute", default="")
parser.add_argument('--copy',action="store_const",help="make output format = input format", default=0, const=1)
parser.add_argument('--area', action="store",help="overflown area, format: (long,lat),(long,lat) the two points are endpoints of a diagonal that marks the requested area" , default="")
parser.add_argument('--fieldnames', action="store",help="fieldname sequence, options: %s" % ",".join(fieldnames.keys()), default="new")


args = vars(parser.parse_args())


from opener import f_open
# def f_open(a) :
#	if re.search("\.bz2$",a) :
#		return bz2.BZ2File(a,"r")
#	return open(a,"r")

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
	# logger.debug("{lats} {longs}".format(**locals()))
	def filter_flight(r) :
		if (float(r["lat"])>=lats[0] and float(r["lat"])<=lats[1]) and (float(r["lng"])>=longs[0] and float(r["lng"])<=longs[1]) :
			return True
		return False
	return filter_flight 

def seek_time(pot) :
	minseek=pot-datetime.timedelta(minutes=1)
	filesearch=re.compile(pot.strftime("/%Y-%m-%d[^/]+$"))
	minstamp=minseek.strftime("%Y.%m.%d %H:%M:%S")
	f=[a for a in args["infiles"] if filesearch.search(a)] 
	if f :
		tf=f_open(f[0])
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


# output_fields=["fn","rn","time","lat","lng","head","speed","alt","reg"]

output_fields=["time", "reg","type","lat","lng","alt","speed","head","flight","radar","fcode","fair","tair"]
output_base="raw/extracted"


if __name__== "__main__" :
	import pprint
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
	if args["copy"] :
		output_fields=fieldnames[args["fieldnames"]]
	if hasattr(args["output"],"write") :
		off=args["output"]
		output_message=False
	else :
		off=open(os.path.join(output_base,args["output"]),"w")
		output_message="Find output in http://projekte.ftd.de/~mvirtel/flightdata/extracted/%s" % args["output"]
	if args["find"] :
		p=seek_pos(args["find"])
		if p :
			logger.info("%s - %s:%s" % (args["find"],p["lat"],p["lng"]))
		else :
			logger.info("%s - no position" % (args["find"]))
		exit()
	if not args["by_registration"] :
		off.write("%s\n" % args["output_delimiter"].join(output_fields))
		outfile=csv.DictWriter(off,fieldnames=output_fields,delimiter=args["output_delimiter"],extrasaction="ignore")
	already={ "reg" : {} }
	outfiles={}
	rect=0 
	reco=0
	startmoment=datetime.datetime.now()
	ffilter=find_filter()
	for fn in args["infiles"] :
		if args["listfiles"] :
			logger.debug("selected: %s" % fn)
			continue
			
		logger.debug("Opening %s for input " % fn)
		inp=f_open(fn)
		recc=0
		records=csv.DictReader(inp, fieldnames=fieldnames[args["fieldnames"]], delimiter=args["input_delimiter"])
		for rec in records :
			try :
				recc=recc+1
				rect=rect+1
				if (recc % 1000000)==0 :
					logger.info("%s:%s Mio. records" % (fn,recc/1000000))
				if args["registration"] :
					cont=True
					for r in args["registration"] :
						if rec["reg"][:len(r)]==r :
							cont=False
							break
					if cont :
						continue
				if args["slower"] :
					if int(rec["speed"])>=args["slower"] :
						continue
				if not ffilter(rec) :
					continue
				if (not rec["reg"] in already["reg"]) or (int(rec["stamp"])-already["reg"][rec["reg"]]>60*args["every"]) :
						if "filename" in output_fields :
							rec["filename"]=os.path.split(fn)[1]
						if "lineno" in output_fields :
							rec["lineno"]=recc
						if args["by_registration"] :
							if not rec["reg"] in outfiles :
								of=args["filename_template"] % rec
								logger.debug("output to: %s" % of)
								od=os.path.split(of)[0]
								if not os.path.exists(od) :
									os.path.makedirs(od)
								ofo=open(of,"w")
								ofo.write("%s\n" % args["output_delimiter"].join(output_fields))
								outfiles[rec["reg"]]=csv.DictWriter(ofo,fieldnames=output_fields,delimiter=args["output_delimiter"], extrasaction="ignore")
							outfiles[rec["reg"]].writerow(rec)
							reco=reco+1
						else :
							outfile.writerow(rec)
							reco=reco+1
						try :
							already["reg"][rec["reg"]]=int(rec["stamp"])
						except TypeError :
							logger.error("record without valid timestamp: %s" % pprint.pformat(rec))
			except Exception,e :
				logger.error("error %s for %s (#%s)" % (e,pprint.pformat(rec),recc))
		inp.close()
	elapsed=datetime.datetime.now()-startmoment
	logger.info("%.2f Mio. records read, %s records written in %s min %s sec." % (float(rect)/1000000,reco,int(elapsed.seconds/60),elapsed.seconds % 60))
	if args["by_registration"] :
		logger.info("%s file(s) written, find them at http://projekte.ftd.de/~mvirtel/flightdata/extracted/by_registration/" % len(outfiles.keys()))
	else :
		if output_message :
			logger.info(output_message)

