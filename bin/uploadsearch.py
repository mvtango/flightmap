from pyelasticsearch import ElasticSearch
import simplejson,sys

s=ElasticSearch("http://localhost:9200")

s.delete_all_indexes();
try :
	s.create_index("flights")
except Exception, e:
	print e
else :	
	print "Created flights"


s.put_mapping("flights","flight",simplejson.loads('{"flight":{"properties":{"datum":{"type":"string","index":"not_analyzed","omit_norms":true,"index_options":"docs"},"duration":{"type":"double"},"end":{"properties":{"alt":{"type":"integer"},"dist":{"type":"float"},"speed":{"type":"integer"},"time":{"type":"date","format":"dateOptionalTime"},"town":{"type":"string","analyzer":"keyword"}}},"flight":{"type":"string","store":true,"analyzer":"keyword"},"hex":{"type":"string","store":true,"analyzer":"keyword"},"id":{"type":"string","store":true},"radar":{"type":"string","store":true,"analyzer":"keyword"},"reg":{"type":"string","store":true,"analyzer":"keyword"},"route":{"properties":{"coordinates":{"type":"double"},"type":{"type":"string"}}},"start":{"properties":{"alt":{"type":"integer"},"dist":{"type":"float"},"speed":{"type":"integer"},"time":{"type":"date","format":"dateOptionalTime"},"town":{"type":"string","analyzer":"keyword"}}}}}}'))



def md(a) :
    a["datum"]=a["starttime"][:10]
    return a
    
    
def makets(a) :
    for f in ("starttime","endtime") :
        a[f]=maket(a[f])
    return a



d=simplejson.load(sys.stdin)
print "%s documents" % (len(d),)
s.bulk_index("flights","flight",d)	


