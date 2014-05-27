import os
import csv
from scraper import airlineSet, planeIdSet

PATH_DUMPS = '/home/michael/flightradar_scraper/dumps'
PATH_TMP_FILE = '/tmp/dump.tsv'

for filename in sorted(os.listdir(PATH_DUMPS))[3:]:

	print '*', filename
	
	if filename.endswith('.bz2'):
		print '  decompressing...'
		cmd = 'bunzip2 %s/%s -c > %s' % (PATH_DUMPS, filename, PATH_TMP_FILE)
		os.system(cmd)
		print '  done.'
		filename_src = PATH_TMP_FILE
	else:
		filename_src = filename

	print '  filtering...'
	f = open(filename_src)
	for line in f.readlines():
		if line.find('D-AZEM') != -1:
			print line
		# data = line.split('\t')
		# code = data[11]
		# if code in planeIdSet:
			# print line.replace('\t', '---'), code
		
	print '   done.'
	1/0