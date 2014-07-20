import subprocess
import re 

def o7zip(name) :
	p=subprocess.Popen(["/bin/sh","-c"," 7z e -so %s 2>/dev/null" % name],stdout=subprocess.PIPE)
	return p.stdout


def f_open(a) :
	if re.search("\.bz2$",a) :
		return bz2.BZ2File(a,"r")
	if re.search(r"\.7z$",a) :
		return o7zip(a) 
	return open(a,"r")
