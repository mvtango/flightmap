# coding: utf-8

import requests
import simplejson

from skyscraper.job import Job

class SkyscraperClientError(Exception) :
	pass

class Client :
	
	def __init__(self,endpoint="http://skyscraper.opendatacloud.de/api/") :
		self.endpoint=endpoint
		self.jobs={}
		
		
	def term(self,*args,**kwargs) :
		url="%s%s" % (self.endpoint,"/".join(args))
		if kwargs :
			data=simplejson.dumps(kwargs)
			c=requests.post(url, headers={'content-type': 'application/json'},
							data=data)
		else :
			c=requests.get(url)
		if c.status_code==400 :
			raise SkyscraperClientError(c.content)
		else :
			try :
				return simplejson.loads(c.content)
			except Exception,e :
				return { 'Error' : repr(e), id: None } 
		
		
	def create(self,*args,**kwargs) :
		"""
	Possible first parameter: Job Name
	if not given, the name of the calling function will be used
	
	Possible named parameters
			* description
			* start_timer - The maximum time between two start signals
			* run_timer The maximum time between start and end signals
			* ping_timer The maximum time between two ping signals
			* success_timer The maximum time between two success signals
			* warning_counter_max The maximum number of warning signals during one execution
			* success_counter_min The minimum number of success signals during one execution
			* success_counter_max The maximum number of success signals during one execution
			* ping-counter_min The minimum number of ping signals during one execution
			* ping-counter_max The maximum number of ping signals during one execution
			* contacts: A list of dicts with the possible keys email, name, sms, pushover

	
	See https://github.com/opendatacity/skyscraper for more explanation
		"""
		j=Job(self,*args,**kwargs)
		self.jobs[j.data["id"]]=j
		return j
		
	def __del__(self) :
		for j in self.jobs.values() :
			j.destroy()
			j.end()
		

		
