from elasticsearch import Elasticsearch,helpers
import simplejson as json ,sys
import pprint 

s=Elasticsearch("http://localhost:9200")

if "init" in sys.argv :
	try :
		s.indices.delete("flights");
	except Exception, e:
		print e
	try :
		s.indices.create("flights")
	except Exception, e:
		print e 
	else :	
		print "Created flights"


	s.indices.put_mapping(index="flights",doc_type="flight",body=json.loads('{"flight":{"properties":{"datum":{"type":"string","index":"not_analyzed","omit_norms":true,"index_options":"docs"},"type": { "type": "string", "index" : "not_analyzed" }, "duration":{"type":"double"},"end":{"properties":{"alt":{"type":"integer"},"dist":{"type":"float"},"speed":{"type":"integer"},"time":{"type":"date","format":"dateOptionalTime"},"town":{"type":"string","analyzer":"keyword"},"country":{"type":"string","analyzer":"keyword"}}},"flight":{"type":"string","store":true,"analyzer":"keyword"},"hex":{"type":"string","store":true,"analyzer":"keyword"},"id":{"type":"string","store":true},"radar":{"type":"string","store":true,"analyzer":"keyword"},"reg":{"type":"string","store":true,"analyzer":"keyword"},"route":{"properties":{"coordinates":{"type":"double"},"type":{"type":"string"}}}, "profile" : {"properties":{"a":{"type":"long"},"h":{"type":"long"},"q":{"type":"string"},"s":{"type":"long"},"t":{"type":"date", "format" : "dateOptionalTime" }}}, "start":{"properties":{"alt":{"type":"integer"},"dist":{"type":"float"},"speed":{"type":"integer"},"time":{"type":"date","format":"dateOptionalTime"},"town":{"type":"string","analyzer":"keyword"},"country":{"type":"string","analyzer":"keyword"}}}}}}'))



def md(a) :
    a["datum"]=a["starttime"][:10]
    return a
    
    
def makets(a) :
    for f in ("starttime","endtime") :
        a[f]=maket(a[f])
    return a


def docs_iterator(a) :
	for s in a :
		a= { "_source" : s, "_index" : "flights", "_type" : "flight", "_id" : s["id"], "_op_type" : "index" }
		yield a


if __name__=="__main__" :
    import pprint
    chunksize=30
    b=[]
    for l in sys.stdin.readlines() :
        b.append(json.loads(l))
        if len(b)==chunksize :
            r=helpers.bulk(s,docs_iterator(b))
            print "{0} inserted: {1}".format(len(b),repr(r))
            b=[]
    if len(b) :
        r=helpers.bulk(s,docs_iterator(b))
        print "{0} inserted: {1}".format(len(b),repr(r))



