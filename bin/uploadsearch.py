from pyelasticsearch import ElasticSearch


s.put_mapping("flight-index",  "flight", { "flight" : {
                    "properties" : { 
                    "start" : { "type" : "string", "store" : "yes", "analyzer": "keyword" },
                    "end" : { "type" : "string", "store" : "yes",  "analyzer": "keyword"},
                    "duration" : { "type" : "long", "store" : "yes" },
                    "endtime" : { "type" : "date", "store" : "yes" },
                    "starttime" : { "type" : "date", "store" : "yes" },
                    "reg" : { "type" : "string", "store" : "yes", "analyzer": "keyword"},
                    "hex" : { "type" : "string", "store" : "yes", "analyzer": "keyword" },
                    "radar" : { "type" : "string", "store" : "yes", "analyzer": "keyword" },
                    "flight" : { "type" : "string", "store" : "yes","analyzer": "keyword"},
                    "id" : { "type" : "string", "store" : "yes" },
                    "datum" : { "type" : "string", "index" : "not_analyzed"}
                }
              }}
    )

def md(a) :
    a["datum"]=a["starttime"][:10]
    return a
    
    
def makets(a) :
    for f in ("starttime","endtime") :
        a[f]=maket(a[f])
    return a

d=simplejson.load(open("bin/flights.json"))


s=ElasticSearch("http://localhost:9200")
