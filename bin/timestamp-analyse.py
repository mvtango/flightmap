import datetime
import sys



for a in sys.stdin.readlines() :
	tabs=a.split("\t")
	try :
		delta=datetime.datetime.strptime(tabs[0],"%Y.%m.%d %H:%M:%S")-datetime.datetime.fromtimestamp(float(tabs[12]))
		sd="%s s." % delta.seconds
		tabs[0]="%s\t%s" % (tabs[0],sd)
		print "\t".join(tabs)
	except Exception, e :
		print e
		i=0
		for t in tabs :
			print "%s: %s" % (i,tabs[i])
			i=i+1
