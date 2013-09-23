from pyelasticsearch import ElasticSearch
import simplejson,sys

s=ElasticSearch("http://localhost:9200")

if "init" in sys.argv :
	try :
		s.delete_index("flights");
	except Exception, e:
		print e
	try :
		s.create_index("flights")
	except Exception, e:
		print e
	else :	
		print "Created flights"


	s.put_mapping("flights","flight",simplejson.loads('{"flight":{"properties":{"datum":{"type":"string","index":"not_analyzed","omit_norms":true,"index_options":"docs"},"type": { "type": "string", "index" : "not_analyzed" }, "duration":{"type":"double"},"end":{"properties":{"alt":{"type":"integer"},"dist":{"type":"float"},"speed":{"type":"integer"},"time":{"type":"date","format":"dateOptionalTime"},"town":{"type":"string","analyzer":"keyword"},"country":{"type":"string","analyzer":"keyword"}}},"flight":{"type":"string","store":true,"analyzer":"keyword"},"hex":{"type":"string","store":true,"analyzer":"keyword"},"id":{"type":"string","store":true},"radar":{"type":"string","store":true,"analyzer":"keyword"},"reg":{"type":"string","store":true,"analyzer":"keyword"},"route":{"properties":{"coordinates":{"type":"double"},"type":{"type":"string"}}},"start":{"properties":{"alt":{"type":"integer"},"dist":{"type":"float"},"speed":{"type":"integer"},"time":{"type":"date","format":"dateOptionalTime"},"town":{"type":"string","analyzer":"keyword"},"country":{"type":"string","analyzer":"keyword"}}}}}}'))



def md(a) :
    a["datum"]=a["starttime"][:10]
    return a
    
    
def makets(a) :
    for f in ("starttime","endtime") :
        a[f]=maket(a[f])
    return a



d=simplejson.load(sys.stdin)
chunksize=50
print "%s documents" % (len(d),)
for i in xrange(0,len(d),chunksize) :
	s.bulk_index("flights","flight",d[i:i+chunksize])	
	print "inserted %s starting from %s" % (chunksize,i)


