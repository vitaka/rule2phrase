#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import apertium,sys,re,subprocess;

splitter =re.compile(r"\^\.<sent>\$\[\n?\]")

def executePretransfer(src, sourceLang, targetLang):
	if (sourceLang=="br" and targetLang=="fr") or (sourceLang=="eu" and targetLang=="es") or (sourceLang=="en" and targetLang=="es"):
		command=["apertium", "-u","-f", "none", sourceLang+"-"+targetLang+"-pretransfer"]
	else:
		command=["apertium-pretransfer"]
	p=subprocess.Popen(command,-1,None,subprocess.PIPE,subprocess.PIPE)
	tuple=p.communicate(src.encode('utf-8'))
	output=tuple[0].decode('utf-8')
	return output

def applyPreTransfer(lexForms, cdict, sourceLang, targetLang):
	src=u"^.<sent>$[\n]".join(lexForms)+u"^.<sent>$[]"
	result=executePretransfer(src,sourceLang,targetLang)
	lines=splitter.split(result)[:-1]
	if len(lexForms) != len(lines):
		print >>sys.stderr, "Length mismatch when calling pretransfer. src "+str(len(lexForms))+" target"+str(len(lines))
		return
	
	for i in range(len(lines)):
		lexForm=lexForms[i]
		line=lines[i]
		
		generatedForms=list()
		prevPos=-1
		pos=line.find(u"^")
		while pos > -1:
			if prevPos>-1:
				generatedForms.append(line[prevPos:pos].strip())
			prevPos=pos
			pos=line.find(u"^",prevPos+1)
		generatedForms.append(line[prevPos:].strip())
		
		if len(generatedForms) >1:
			cdict[u" -- ".join(generatedForms)]=lexForm
		
		for gf in generatedForms:
			print gf.encode('utf-8')

sourceLang=sys.argv[2]
targetLang=sys.argv[3]

currentTag=u""
lexForms=list()

compoundDict=dict()

for line in sys.stdin:
	line=line.decode('utf-8').strip()
	if line != u"":
		if line[0] == u'#':
			if currentTag != u"":
				print  >> sys.stderr, currentTag.encode('utf-8')+" -> "+str(len(lexForms)) +" entries"
				applyPreTransfer(lexForms, compoundDict, sourceLang, targetLang)
			tag=line[1:]
			currentTag=tag
			lexForms=list()
		else:
			if currentTag != u"":
				lexForms.append(u"^"+line+currentTag+u"$")
				
if currentTag!=u"" and len(lexForms)>0:
	applyPreTransfer(lexForms, compoundDict,sourceLang, targetLang)
	
#print dictionary
f = open(sys.argv[1],'w')
for key in compoundDict:
	f.write(key.encode('utf-8')+" ||| "+compoundDict[key].encode('utf-8')+"\n")
f.close()

