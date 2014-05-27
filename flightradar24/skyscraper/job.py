#
# 

import traceback
import datetime
import pprint

debug=False


# Public Domain, i.e. feel free to copy/paste
#
# Considered a hack in Python 2
# https://gist.github.com/techtonik/2151727

import inspect

def caller_name(skip=2):
    """Get a name of a caller in the format module.class.method
    
       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.
       
       An empty string is returned if skipped levels exceed stack height
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
      return ''
    parentframe = stack[start][0]    
    
    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append( codename ) # function or a method
    del parentframe
    return ".".join(name)


class Job :
	"""Encapsules a Skyscraper job created by a client. 
	On creation, a range of hooks and contacs can be established. 
	
	Example usage - see readme.md in package root.
	
	"""
	
	
	
	def __init__(self,client,*args,**kwargs) :
		"""
	Normally only called by skyscraper.Client instance.
	
	Available methods:
	start()
	end()
	ping()
	warn()
	success()
	error(message)
	log(message)
		"""

		self.client=client
		if len(args)>0 :
			name=args[0]
		else :
			# get name of calling function
			try :
				name=caller_name(skip=3)
			except Exception :
				name=""
			if not name :
				name="Unknown Caller"
		param=dict(hooks=[],name=name[-20:],description="%s created on %s by skyscraperpy" % (name,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
		for (k,v) in kwargs.items() :
			if k.find("_") > 0 :
				param["hooks"].append({ k.replace("_","-") : v })
			else :
				param[k]=v
		if len(param["hooks"])==0 :
			param["hooks"].append({"run-timer" : 90})
		self.data=self.client.term("create",**param)
		
	def term(self,myterm,**kwargs) :
		if hasattr(self,"data") and self.data is not None :
			if debug :
				print "%s: %s" % (myterm,self.data["id"])
			return self.client.term(myterm,self.data["id"],**kwargs)
		else :
			return False
		
	def ping(self) :
		return self.term("ping")
		
	def start(self) :
		return self.term("start")
		
	def end(self) :
		retval=self.term("end")
		if hasattr(self,"data") :
			self.data=None
		return retval

	def success(self) :
		return self.term("success")

	def warn(self) :
		return self.term("warn")

	def error(self, message) :
		return self.term("error",message=message)
	
	def destroy(self) :
		return self.term("destroy")
	
	def log(self,message) :
		return self.term("log",message=message)

	def __del__(self) :
		self.destroy()
			
	def __enter__(self) :
		self.start()
		return self
		
	def __exit__(self,etype,value,tb) :
		if etype is not None :
			self.error(traceback.format_exc(tb))
		# self.end()
		self.destroy()
		return True
