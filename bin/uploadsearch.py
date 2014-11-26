from elasticsearch import Elasticsearch,helpers
import simplejson as json ,sys
import pprint 
import argparse
from simplejson.scanner import JSONDecodeError

parser = argparse.ArgumentParser(description="elasticsearch uploader", conflict_handler='resolve')
parser.add_argument('--init',action="store_const",help="erase index before uploading", default=0, const=1)
parser.add_argument('--target',action="store",help="elasticsearch url, default is http://localhost:9200", default="http://localhost:9200/")
parser.add_argument('--chunksize',action="store",help="bulk upload in batches of N docs", type=int, default=4)
parser.add_argument('--property',action="append",help="property added to every doc",  default=[])

args = vars(parser.parse_args())


s=Elasticsearch(args["target"])


def init() :
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
	s.indices.put_mapping(index="flights",doc_type="flight",body=json.loads('{"flight":{"properties":{"datum":{"type":"string","index":"not_analyzed","omit_norms":true,"index_options":"docs"}, "dataset":{"type":"string","index":"not_analyzed","omit_norms":true,"index_options":"docs"}, "type": { "type": "string", "index" : "not_analyzed" }, "duration":{"type":"double"},"end":{"properties":{"alt":{"type":"integer"},"dist":{"type":"float"},"speed":{"type":"integer"},"time":{"type":"date","format":"dateOptionalTime"},"town":{"type":"string","analyzer":"keyword"},"country":{"type":"string","analyzer":"keyword"}}},"flight":{"type":"string","store":true,"analyzer":"keyword"},"hex":{"type":"string","store":true,"analyzer":"keyword"},"id":{"type":"string","store":true},"radar":{"type":"string","store":true,"analyzer":"keyword"},"reg":{"type":"string","store":true,"analyzer":"keyword"},"route":{"properties":{"coordinates":{"type":"double"},"type":{"type":"string"}}}, "profile" : {"properties":{"a":{"type":"long"},"h":{"type":"long"},"q":{"type":"string"},"s":{"type":"long"},"t":{"type":"date", "format" : "dateOptionalTime" }}}, "start":{"properties":{"alt":{"type":"integer"},"dist":{"type":"float"},"speed":{"type":"integer"},"time":{"type":"date","format":"dateOptionalTime"},"town":{"type":"string","analyzer":"keyword"},"country":{"type":"string","analyzer":"keyword"}}}}}}'))



def md(a) :
    a["datum"]=a["starttime"][:10]
    return a
    
    
def makets(a) :
    for f in ("starttime","endtime") :
        a[f]=maket(a[f])
    return a


def docs_iterator(a,props) :
	for s in a :
		s.update(props)
		a= { "_source" : s, "_index" : "flights", "_type" : "flight", "_id" : s["id"], "_op_type" : "index" }
		yield a


if __name__=="__main__" :
    if args["init"] :
	print "Erasing index" 
	init()
    import pprint
    chunksize=args["chunksize"]
    props={}
    for p in args["property"] :
	kv=p.split("=",1)
	props[kv[0]]=kv[1]
    if props :
	print "Adding %s to documents." % repr(props)
    count=0
    b=[]
    for l in sys.stdin.readlines() :
	try :
            b.append(json.loads(l))
	except JSONDecodeError,e :
	    print "Invalid JSON: %s [%s]" % (b[0:10],e)
        if len(b)==chunksize :
            r=helpers.bulk(s,docs_iterator(b,props))
            print "{0}-{1} inserted: {2}".format(count,count+len(b)-1,repr(r))
            count=count+len(b)
            b=[]
    if len(b) :
        r=helpers.bulk(s,docs_iterator(b,props))
        print "{0} inserted: {1}".format(len(b),repr(r))



