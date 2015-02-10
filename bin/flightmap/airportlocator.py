import os
from flightmap.csvstore import csvstore
from geopy import distance
from rtree import index

_here=os.path.split(__file__)[0]


store=csvstore(os.path.join(_here,"data/openflights.airports.csv"))
idx=index.Index()


for airport in store.data :
    bbox=list([float(a) for a in [airport["lng"],airport["lat"],airport["lng"],airport["lat"]]])
    aid=int(airport["nr"])
    idx.insert(aid,bbox,obj=airport)


def nearest_airport(lng,lat) :
    lat=float(lat)
    lng=float(lng)
    nearest=[a.object for a in idx.nearest((lng,lat,lng,lat),objects=True)]
    for airport in nearest :
        fp=(float(airport["lat"]),float(airport["lng"]))
        airport["distance"]=distance.distance((lat,lng),fp).km
	airport["airport_name"]=airport["airport"]  
	del airport["airport"]
    return nearest


if __name__=='__main__' :
	tests=(((8.64,52.03),"Bielefeld"),
		   ((9.3389,54.3223),"Hohn" ))
		   
	for (p,t) in tests :
		assert(nearest_airport(*p)[0]["town"]==t)

	assert(nearest_airport(8.64,52.03)[0]["town"]=="Bielefeld")
