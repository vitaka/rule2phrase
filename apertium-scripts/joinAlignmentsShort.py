#!/usr/bin/python
# coding=utf-8
# -*- encoding: utf-8 -*-

import re, sys, string, apertium,getopt;
from expandPTLib import *

NUMALS=4

try:
	opts, args = getopt.getopt(sys.argv[1:], "s:t:", ["sourceElements=","targetElements="])
except getopt.GetoptError, err:
	# print help information and exit:
	print str(err) # will print something like "option -a not recognized"
	sys.exit(2)

for o, a in opts:
	if o in ("-s", "--sourceElements"):
		NUMALSSRC=int(a)
	elif o in ("-t", "--targetElements"):
		NUMALSTARGET=int(a)
	else:
		assert False, "unhandled option"

numLine=0
for line in sys.stdin:
	line=line.decode('utf-8')
	parts=line.split(u" ||| ")
	
	numLine+=1
	
	if len(parts) >= NUMALS:
		
		alsList=list()
		partIndex=0
		finalAlignments=SentenceAlignments()
		
		for i in range(NUMALS):
			sa=SentenceAlignments()
			sa.parse(parts[partIndex])
			alsList.append(sa)
			partIndex+=1
		
		
		finalAlignments.merge(alsList)
		print finalAlignments.toStringMinusOne().encode('utf-8')
		
	else:
		#print >> sys.stderr, "WARNING: invalid alignments line "
		print >> sys.stderr, "WARNING: invalid alignments. line "+str(numLine)
		print ""
