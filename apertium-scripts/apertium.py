import subprocess;

#removed Apertium PATH.
#Scripts calling this python program must the the path
def translate(src,format,mode):
	p=subprocess.Popen(["apertium","-u", "-f", format, mode],-1,None,subprocess.PIPE,subprocess.PIPE)
	tuple=p.communicate(src.encode('utf-8'))
	supForm=tuple[0].decode('utf-8')
	return supForm
	
def translateAndReformat(src,mode):
	p=subprocess.Popen(["apertium", "-u","-f", "none", mode],-1,None,subprocess.PIPE,subprocess.PIPE)
	tuple=p.communicate(src.encode('utf-8'))
	unformattedtranslation=tuple[0].decode('utf-8')
	
	p2=subprocess.Popen("apertium-retxt",-1,None,subprocess.PIPE,subprocess.PIPE)
	tuple2=p2.communicate(unformattedtranslation.encode('utf-8'))
	return tuple2[0].decode('utf-8')
	
def preTransfer(src):
	p=subprocess.Popen(["apertium-pretransfer"],-1,None,subprocess.PIPE,subprocess.PIPE)
	tuple=p.communicate(src.encode('utf-8'))
	result=tuple[0].decode('utf-8')
	return result
