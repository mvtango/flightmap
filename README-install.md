# Depends on the following prerequisites:
  
apt-get update; apt-get install libspatialindex-dev
pip install geopy
pip install rtree
pip install pyelasticsearch


# Please get fresh airport data by executing 

cd bin/flightmap ; ./getdata.sh



# Initialize Elasticsearch before inserting any records

cd bin/flightmap; python ./uploadsearch init

