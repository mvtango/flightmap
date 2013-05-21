from pyelasticsearch import ElasticSearch


s.put_mapping("flights",  "flight", { "flight" : {
                    "properties" : { 
                    "start" : { "type" : "object",
								"store" : "yes",
							    "properties" : {
									"town" : { "type" : "string", "analyzer" : "keyword" },
									"dist" : { "type" : "float" },
									"alt"  : { "type" : "integer"},
									"time" : { "type" : "date" },
									"speed": { "type" : "integer" },
							  }
					},
					"end" : { "type" : "object",
								"store" : "yes",
							    "properties" : {
									"town" : { "type" : "string", "analyzer" : "keyword" },
									"dist" : { "type" : "float" },
									"alt"  : { "type" : "integer"},
									"time" : { "type" : "date" },
									"speed": { "type" : "integer" },
							  }
					},
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
