#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import re, sys, string, apertium, getopt;
from expandPTLib import *

patternForLex=re.compile(r"\^(([^$]*)\$)")
patternForNumOrd=re.compile(r"\^([0-9]+<num>)<ord>\$")
patternForNom=re.compile(r"\^[^<]+<n>\$")


def reverseOrdinalsEuskara(lexForms,outputAlignments):
	modifiedLexforms=list()
	alignments=SentenceAlignments()
	i=0
	offset=0
	while i < len(lexForms) :
		if i < len(lexForms)-1 and patternForNumOrd.match(lexForms[i]) and patternForNom.match(lexForms[i+1]):
			modifiedLexforms.append(u"^"+patternNumOrd.match(lexForms[i]).group(1)+u"$")
			modifiedLexforms.append(u"^.<sent>$")
			modifiedLexforms.append(lexForms[i+1])
			alignments.alignments.append((i+offset,i))
			alignments.alignments.append((i+offset+2,i+1))
			i+=2
			offset+=1
		else:
			modifiedLexforms.append(lexForms[i])
			alignments.alignments.append((i+offset,i))
			i+=1
	
	if outputAlignments:
		print u" ".join(modifiedLexforms).encode('utf-8')+" ||| "+alignments.toString().encode('utf-8')
	else:
		print u" ".join(modifiedLexforms).encode('utf-8')


def reverseDummy(lexForms,outputAlignments):
	alignmentsStr=""
	if outputAlignments:
		for i in range(len(lexForms)):
			alignmentsStr+=(" "+str(i+1)+"-"+str(i+1))
		print u" ".join(lexforms).encode('utf-8')+" ||| "+alignmentsStr
	else:
		print u" ".join(lexforms).encode('utf-8')

		

srclang="es"
targetlang="pt"
debugOn=False
mwFile="error_mw_file_not_selected"

try:
	opts, args = getopt.getopt(sys.argv[1:], "ds:t:h", ["debug","sourcelang=","targetlang=","help"])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	usage()
	sys.exit(2)

for o, a in opts:
	if o in ("-h", "--help"):
		usage()
		sys.exit()
	elif o in ("-d", "--debug"):
		debugOn=True
	elif o in ("-s", "--sourcelang"):
		srclang=a
	elif o in ("-t", "--targetlang"):
		targetlang=a
	else:
		assert False, "unhandled option"

print >>sys.stderr, "srclang="+srclang+" targetlang="+targetlang+" debug:"+str(debugOn)

myfunction=reverseDummy

if srclang=="eu" and targetlang=="es":
	myfunction=reverseOrdinalsEuskara

for line in sys.stdin:
	line=line.decode('utf-8').strip()
	lexforms=list()
	iterator=patternForLex.finditer(line)
	for m in iterator:
		lexform=m.group()
		lexforms.append(lexform)
	myfunction(lexforms,debugOn)
	
