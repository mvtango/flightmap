import sys
import json


for l in sys.stdin.readlines() :
	o=json.loads(l)
	print "{0}-{1} {o[hex]}".format(o["profile"][-1]["t"],o["profile"][0]["t"],**locals())

