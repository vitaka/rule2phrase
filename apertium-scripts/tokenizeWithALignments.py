#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import getopt,sys,subprocess;
from expandPTLib import *

ENC='utf-8'

def tokenize(inputStr,lang,path):
	p=subprocess.Popen([path,"-l", lang],-1,None,subprocess.PIPE,subprocess.PIPE)
	tuple=p.communicate(inputStr.encode(ENC))
	output=tuple[0].decode(ENC)
	return output

def processBatch(lb,tokenizingALignmentsInEnd,language,path,field):
	tokinput=u""
	batchparts=list()
	for line in lb:
		parts=line.split(u"|||")
		cleanparts=list()
		for p in parts:
			cleanparts.append(p.strip())
		batchparts.append(cleanparts)
		text=parts[field-1].strip()
		words=text.split()
		tokinput+=(u" | ".join(words)+u"\n")

	batchtokoutput=tokenize(tokinput,language,path)
	
	c=0
	for tokoutput in batchtokoutput.strip().split(u"\n"):
		myparts=batchparts[c]
		outputWords=tokoutput.split(u" &#124; ")
		alignments=SentenceAlignments()
		offset=0
		tokenizedSf=list()
		for i in range(len(outputWords)):
			ow=outputWords[i]
			listOW=ow.strip().split()
			num=len(listOW)
			for j in range(num):
				alignments.alignments.append((i+1+offset+j,i+1))
				tokenizedSf.append(listOW[j])
			offset+=(num-1)
		outputParts=myparts[:field-1]+[u" ".join(tokenizedSf)]
		if not tokenizingALignmentsInEnd:
			outputParts.append(alignments.toString())
		outputParts= outputParts + myparts[field:]
		if tokenizingALignmentsInEnd:
			outputParts.append(alignments.toStringInverse())
		print u" ||| ".join(outputParts).encode(ENC)
		c+=1

try:
	opts, args = getopt.getopt(sys.argv[1:], "f:el:p:", ["field=","end","language=","path="])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	sys.exit(2)

field=1
tokenizingALignmentsInEnd=False
path=""
language="br"
for o, a in opts:
	if o in ("-f","--field"):
		field=int(a)
	elif o in ("-e","--end"):
		tokenizingALignmentsInEnd=True
	elif o in ("-l","--language"):
		language=a
	elif o in ("-p","--path"):
		path=a

lineBatch=list()
maxsize=10000

for line in sys.stdin:
	line=line.decode(ENC).strip()
	lineBatch.append(line)
	if len(lineBatch) >= maxsize:
		processBatch(lineBatch,tokenizingALignmentsInEnd,language,path,field)
		lineBatch=[]
if len(lineBatch) > 0:
	processBatch(lineBatch,tokenizingALignmentsInEnd,language,path,field)

